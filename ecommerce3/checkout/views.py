from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from cart.models import Cart
from userprofile.models import Address, Wallet
from products.models import Product
from checkout.models import Order, OrderItem
import random
import string
from django.http import JsonResponse
from decimal import Decimal
from django.contrib import messages
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from coupons.models import Coupon, Usercoupon
from django.db.models import Subquery
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce
from django.db.models import F, ExpressionWrapper, DecimalField, Sum, Case, When
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import os
from django.http import HttpResponse

@login_required(login_url='user_login')
def checkout(request):
    cartitems = Cart.objects.filter(user=request.user)
    
    # Annotate cart items with the total price based on whether they have an offer or not
    cartitems = cartitems.annotate(
        product_price_with_offer=Case(
            When(product__offer__isnull=True, then=F('product__product_price')),  # No offer, use regular price
            default=F('product__product_price') - F('product__offer__discount_amount')  # Apply offer discount
        )
    )
    
    # Annotate cart items with the total price after applying the offer and considering the quantity
    cartitems = cartitems.annotate(
        total_with_offer=ExpressionWrapper(F('product_price_with_offer') * F('product_qty'), output_field=DecimalField())
    )
    
    # Calculate the total price after applying the offer for all items in the cart
    total_price = cartitems.aggregate(sum_total=Sum('total_with_offer')).get('sum_total', 0)
    
    # Check if total_price is None and set it to 0 if it is None
    if total_price is None:
        total_price = Decimal('0')
    
    tax_rate = Decimal('0.18')  # Convert tax rate to Decimal
    tax = total_price * tax_rate
    grand_total = total_price + tax
    
    address = Address.objects.filter(user=request.user)
    active_coupons = Coupon.objects.filter(active=True)
    context = {
        'cartitems': cartitems,
        'total_price': total_price,
        'grand_total': grand_total,
        'tax': tax,
        'address': address,
        'active_coupons': active_coupons,
    }

    return render(request, 'checkout/proceed.html', context)

@login_required(login_url='user_login')
def placeorder(request):
    if request.method == 'POST':
        user = request.user

        # Retrieve the address ID from the form data
        address_id = request.POST.get('address')

        if not address_id:
            messages.error(request, 'Address field is mandatory!')
            return redirect('checkout')

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            messages.error(request, 'Invalid address selected.')
            return redirect('checkout')

        # Create a new Order instance and set its attributes
        neworder = Order(user=user, address=address)
        neworder.od_status = 'Pending'
        neworder.payment_mode = request.POST.get('payment_method')
        neworder.payment_id = request.POST.get('payment_id')
        neworder.message = request.POST.get('order_note')

        # Calculate the cart total price and tax
        cart_items = Cart.objects.filter(user=user)
        cart_total_price = 0  # Initialize the total price to zero
        for item in cart_items:
            product = item.product
            product_price_with_offer = (
                product.product_price - product.offer.discount_amount
                if product.offer
                else product.product_price
            )
            item_total_price = product_price_with_offer * item.product_qty
            cart_total_price += item_total_price

        # Check if a coupon code was selected and apply the coupon discount
        selected_coupon_code = request.POST.get('selectedCoupon')
        if selected_coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=selected_coupon_code)
                if coupon.active:
                    cart_total_price -= cart_total_price * (coupon.discount / 100)
                    # Set the applied coupon to the order (optional, but can be useful)
                    neworder.applied_coupon = coupon
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')
                return redirect('checkout')

        # Convert tax rate to Decimal
        tax = cart_total_price * Decimal('0.18')
        cart_total_price += tax

        # Check the selected payment method
        payment_method = request.POST.get('payment_method')
        if payment_method == "wallet":
            try:
                wallet = Wallet.objects.get(user=user)
            except Wallet.DoesNotExist:
                wallet = Wallet.objects.create(user=user, wallet=0)

            if wallet.wallet >= cart_total_price:
                # Sufficient wallet balance, deduct the amount and proceed with the order
                wallet.wallet -= cart_total_price
                wallet.save()
            else:
                return JsonResponse({'status': "Your wallet amount is very low"})
                return redirect('checkout')

        # Round the total_price attribute of the neworder instance to 2 decimal places
        neworder.total_price = round(cart_total_price, 2)

        # Generate a unique tracking number
        trackno = random.randint(1111111, 9999999)
        while Order.objects.filter(tracking_no=trackno).exists():
            trackno = random.randint(1111111, 9999999)
        neworder.tracking_no = trackno

        neworder.save()

        # Create OrderItem instances for each cart item
        for item in cart_items:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.product_price,
                quantity=item.product_qty
            )

            # Decrease the product quantity from the available stock
            product = Product.objects.get(id=item.product.id)  # Get the Product instance
            product.quantity -= item.product_qty
            product.save()

        # Delete the cart items after the order is placed
        cart_items.delete()

        # Check if a valid coupon code was applied and create a Usercoupon entry
        if selected_coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=selected_coupon_code)
                if coupon.active:
                    Usercoupon.objects.create(coupon=coupon, user=user, total_price=cart_total_price)
            except Coupon.DoesNotExist:
                pass

        # Call a function to generate invoice PDF (implement this function separately)
        generate_invoice_pdf(request, neworder.id)

        return JsonResponse({'status': "Your order has been placed successfully"})

    return redirect('checkout')


def generate_invoice_pdf(request, order_id):
    
    try:
        order = Order.objects.get(id=order_id) 
        order_items = OrderItem.objects.filter(order=order)
    except Order.DoesNotExist:
        # Handle the case if the order does not exist
        return HttpResponse("Order not found", status=404)

    # Render the XHTML template with dynamic data
    context = {
        'order': order,
        'order_items': order_items,
    }
    rendered_template = render_to_string('order/invoice.html', context)

    # Convert the XHTML content to PDF
    pdf_file = os.path.join(settings.BASE_DIR, 'invoice.pdf')
    with open(pdf_file, 'wb') as pdf:
        pisa.CreatePDF(rendered_template, dest=pdf)

    # Send the email with both the PDF attachment and the order confirmation
    subject = "Welcome to Molla Books, Your Order is Placed!!!"
    message = f'''
        Your order has been placed successfully.
        Hello {order.user.username},
        Your Order has been placed successfully.
        Thank you for choosing Molla Books!
        Payment mode: {order.payment_mode}
        Your Payment ID is {order.payment_id}
        Your Order Tracking ID: {order.tracking_no}
    '''
    from_email = settings.EMAIL_HOST_USER
    to_email = [order.user.email]

    email = EmailMessage(subject, message, from_email, to_email)
    email.attach_file(pdf_file)  # Attach the PDF to the email
    email.send()

    # Delete the temporary PDF file
    os.remove(pdf_file)
    return redirect('placeorder')

@login_required(login_url='user_login')
def add_checkout_address(request):
    if request.method == 'POST':
        address = Address()
        address.user = request.user
        address.first_name = request.POST.get('firstname')
        address.last_name = request.POST.get('lastname')
        address.country = request.POST.get('country')
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.pincode = request.POST.get('pincode')
        address.phone = request.POST.get('phone')
        address.email = request.POST.get('email')
        address.state = request.POST.get('state')
        address.order_note = request.POST.get('ordernote')
        # address.payment_mode = request.POST.get('payment_method')
        address.save()

        return redirect('checkout')
    return redirect('checkout')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')
def razarypaycheck(request):
    cart = Cart.objects.filter(user=request.user)
    total_price = 0
    grand_total=0
    for item in cart:
        total_price = total_price + item.product.product_price * item.product_qty
        tax = total_price * 0.18
        grand_total += total_price+tax
    
    return JsonResponse({'total_price': grand_total})

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        grand_total = Decimal(request.POST.get('grand_total'))
        product_id = request.POST.get('product_id')

        try:
            active_offer = None
            product_offers = None

            # Check for an applicable offer related to the product
            if product_id:
                product_offers = Offer.objects.filter(product_id=product_id, start_date__lte=date.today(), end_date__gte=date.today())
                if product_offers.exists():
                    active_offer = product_offers.first()

            # Check for an applicable coupon
            if coupon_code:
                existing_coupon = Coupon.objects.get(coupon_code=coupon_code)

                if not existing_coupon.active:
                    return JsonResponse({'status': 'Coupon is not active'})

                if Usercoupon.objects.filter(coupon=existing_coupon, user=request.user).exists():
                    return JsonResponse({'status': 'Coupon already used'})

                # Check if the user has placed an order with the coupon before adding it
                if Order.objects.filter(user=request.user, od_status='Delivered').exists():
                    # Apply the coupon discount to the grand total
                    grand_total -= (grand_total * existing_coupon.discount / 100)

                    # Save the coupon usage for the current user with total_price as 0
                    Usercoupon.objects.create(coupon=existing_coupon, user=request.user, total_price=0)

            # Apply offer discount to the grand total (if available for the selected product)
            if active_offer:
                grand_total -= (grand_total * active_offer.discount_amount / 100)

            return JsonResponse({
                'status': 'Discounts applied successfully',
                'offer_discount': active_offer.discount_amount if active_offer else 0,
                'coupon_discount': existing_coupon.discount if coupon_code else 0,
                'grand_total': grand_total,
            })

        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'Coupon does not exist'})
        except Exception as e:
            
            return JsonResponse({'status': str(e)})

    return JsonResponse({'status': 'Invalid request'})

