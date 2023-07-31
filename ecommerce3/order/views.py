from django.shortcuts import render,redirect
from cart.models import Cart
from userprofile.models import Address
from checkout.models import Order,OrderItem
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from products.models import Product
from userprofile.models import Wallet
from django.contrib import messages
from django.db.models import Q
from .models import Orderreturn


def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at').prefetch_related('orderitem_set', 'address')
    context = {
        'orders': orders,
    }
    return render(request, 'order/ad-orders.html', context)


def changestatus(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    orderitem_id = request.POST.get('orderitem_id')
    order_status = request.POST.get('order_status')
    orderitems = OrderItem.objects.get(id = orderitem_id)

    orderitems.status = order_status
    orderitems.save()
    return JsonResponse({'status': "Updated"+ str(order_status) + "successfully"}) 


def change_od_status(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    order_id = request.POST.get('order_id')
    order_od_status = request.POST.get('order_od_status')  # Rename the variable

    

    try:
        order = Order.objects.get(id=order_id)
        order.od_status = order_od_status
        order.save()
        # The order's od_status field has been updated
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        print("Order does not exist.")
    
    return JsonResponse({'status': "Updated " + str(order_od_status) + " successfully"})


def search_orders(request):
    if not request.user.is_superuser:
        return redirect('adminsignin')

    keyword = request.GET.get('keyword', '').strip().lower()
    if keyword:
        orders = Order.objects.filter(
            Q(tracking_no__icontains=keyword.lower()) |
            Q(id__icontains=keyword.lower()) |
            Q(total_price__icontains=keyword.lower()) |
            Q(payment_id__icontains=keyword.lower())|
            Q(payment_mode__icontains=keyword.lower())|
            Q(user__username__icontains=keyword.lower())
        ).order_by('id')

        

        if orders.exists():
            context = {
                'orderitems': OrderItem.objects.filter(order__in=orders),
            }
            return render(request, 'order/ad-orders.html', context)
        else:
            message = "No orders found."
            return render(request, 'order/ad-orders.html', {'message': message})
    else:
        message = "Please enter a valid search keyword."
        return render(request, 'order/ad-orders.html', {'message': message})

def ordercancel(request):
    orderid = int(request.POST.get('order_id'))
    orderitem_id = request.POST.get('orderitem_id')
    orderitem = OrderItem.objects.filter(id=orderitem_id).first()
    

    
    order = Order.objects.filter(id=orderid).first()
    qty = orderitem.quantity
    pid = orderitem.product.id
    product = Product.objects.filter(id=pid).first()
    

    if order.payment_mode == 'Razorpay' or order.payment_mode == 'wallet' :
        order = Order.objects.get(id=orderid)
        total_price = orderitem.price*orderitem.quantity*1.18

        try:
            wallet = Wallet.objects.get(user=request.user)
            wallet.wallet += total_price
            wallet.save()
        except Wallet.DoesNotExist:
            wallet = Wallet.objects.create(user=request.user, wallet=total_price)
    # Update the product quantity
    product.quantity = product.quantity + qty
    product.save()
    
    orderitem.status = 'Cancelled'
    orderitem.save()
    return redirect('user_profile')

def orderreturn(request, return_id):
    if request.method == 'POST':
        options = request.POST.get('options')
        reason = request.POST.get('reason')

        # validation
        if options.strip() == '':
            messages.error(request, "enter valid Options")
            return redirect('vieworderdetail')

        try:
            orderitem_id = OrderItem.objects.get(id=return_id)
        except OrderItem.DoesNotExist:
            return redirect('user_profile')

        qty = orderitem_id.quantity
        pid = orderitem_id.product.id
        order_id = Order.objects.get(id=orderitem_id.order.id)

        product = Product.objects.filter(id=pid).first()
        product.quantity = product.quantity + qty
        product.save()

        orderitem_id.status = 'Return'
        total_p = orderitem_id.price

        # Calculate the total price to add to the wallet
        total_price_to_add = total_p * qty * 1.18

        
        
        orderitem_id.save()

        # Update the wallet with the total price to add
        try:
            wallet = Wallet.objects.get(user=request.user)
            wallet.wallet += total_price_to_add
            wallet.save()
        except Wallet.DoesNotExist:
            wallet = Wallet.objects.create(user=request.user, wallet=total_price_to_add)

        returnorder = Orderreturn.objects.create(user=request.user, order=order_id, options=options, reason=reason)

        return redirect('user_profile')




def edit_address(request,edit_id):

    if request.method == 'POST':

        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
        country=request.POST.get('country')
        address=request.POST.get('address')
        city=request.POST.get('city')
        pincode=request.POST.get('pincode')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        state=request.POST.get('state')
        order_note=request.POST.get('order_note')


        if request.user is None:
            return
        
        if first_name.strip() == '' or last_name.strip() == '':
            messages.error(request,'names cannot be empty!!!')
            return redirect('user_profile')
        
        if country.strip()=='':
            messages.error(request,'Country cannot be empty')
            return redirect('user_profile')
        if city.strip()=='':
            messages.error(request,'city cannot be empty')
            return redirect('user_profile')
        if address.strip()=='':
            messages.error(request,'address cannot be empty')
            return redirect('user_profile')
        if pincode.strip()=='':
            messages.error(request,'pincode cannot be empty')
            return redirect('user_profile')
        if phone.strip()=='':
            messages.error(request,'phone cannot be empty')
            return redirect('user_profile')
        if email.strip()=='':
            messages.error(request,'email cannot be empty')
            return redirect('user_profile')
        if state.strip()=='':
            messages.error(request,'state cannot be empty')
            return redirect('user_profile')

        try:
            ads = Address.objects.get(id=edit_id)
        except Address.DoesNotExist:
            messages.error(request, 'Address not found')
            return redirect('user_profile')
        ads.user=request.user
        ads.first_name=first_name
        ads.last_name=last_name
        ads.country=country
        ads.address=address
        ads.city=city
        ads.pincode=pincode
        ads.phone=phone
        ads.email=email
        ads.state=state
        ads.order_note=order_note
        ads.save()

        return redirect('user_profile')
    else:
        return redirect('user_profile')
