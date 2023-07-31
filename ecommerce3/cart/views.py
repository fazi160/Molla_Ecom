from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Cart
# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from wishlist.models import Wishlist
from django.views.decorators.cache import cache_control
from django.http.response import JsonResponse
from products.models import Product

@login_required(login_url='user_login')
def cart(request):
    cart = Cart.objects.filter(user=request.user).order_by('id')
    single_product_total = []
    total_price = 0
    tax = 0
    single_total = 0
    grand_total = 0

    for item in cart:
        if item.product.offer is None:
            total_price += item.product.product_price * item.product_qty
            single_product_total.append(item.product.product_price * item.product_qty)
          
        else:
            total_price += item.product.product_price * item.product_qty
            single_product_total.append((item.product.product_price - item.product.offer.discount_amount) * item.product_qty)
            total_price -= item.product.offer.discount_amount * item.product_qty


    tax = total_price * 0.18
    grand_total = total_price + tax
    context = {
        'cart': cart,
        'total_price': total_price,
        'tax': tax,
        'single_product_total': single_product_total,
        'grand_total': grand_total
    }

    return render(request, 'user/cart.html', context)




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def add_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
           
            prod_id = request.POST.get('prod_id')
            
            try:
                product_check = Product.objects.get(id=prod_id)
                

            except Product.DoesNotExist:
                return JsonResponse({'status': 'No such product found'})

            if Cart.objects.filter(user=request.user, product_id=prod_id).exists():
                return JsonResponse({'status': 'product already in Cart'})
            else:
                prod_qty = int(request.POST.get('product_qty'))
                
                if product_check.quantity >= prod_qty:
                    Cart.objects.create(user=request.user, product_id=prod_id, product_qty=prod_qty)
                    # try:
                    #     if Wishlist.objects.filter(user = request.user, product = prod_id).exists():
                    #         wishlist = Wishlist.objects.filter(user = request.user, product = prod_id)
                    #         wishlist.delete()
                    # except:
                        
                    #     pass
                    return JsonResponse({'status': 'product added successfully'})
                else:
                    return JsonResponse({'status': "Only few quantity available"})
        else:
            return JsonResponse({'status': 'Login to continue'})
    return redirect('product_detail')



# Update cart quantity
# @cache_control(no_cache=True,must_revalidate=True,no_store=True)



                   

def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if (Cart.objects.filter(user=request.user, product_id=product_id)):
            prod_qty = request.POST.get('product_qty')
            cart = Cart.objects.get(product_id=product_id, user=request.user)
            cartes = cart.product.quantity
            if int(cartes) >= int(prod_qty):
                cart.product_qty = prod_qty
                cart.save()

                carts = Cart.objects.filter(user = request.user).order_by('id')
                total_price = 0
                for item in carts:
                    if item.product.offer == None:
                        total_price = total_price + item.product.product_price * item.product_qty
                    else :
                        total_price = total_price + item.product.product_price * item.product_qty
                        total_price = total_price - (item.product.offer.discount_amount * item.product_qty)

                       
                return JsonResponse({'status': 'Updated successfully','sub_total':total_price,'product_price':cart.product.product_price,'quantity':prod_qty})
            else:
                return JsonResponse({'status': 'Not allowed this Quantity'})
    return JsonResponse('something went wrong, reload page',safe=False)

# Deletecart
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def deletecartitem(request,product_id):    
    product_id = product_id
    cart_items = Cart.objects.filter(user=request.user, product=product_id)
    if cart_items.exists():
        cart_items.delete()
    return redirect('cart')
