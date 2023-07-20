from django.shortcuts import render,redirect
from cart.models import Cart
from userprofile.models import Address
from checkout.models import Order,OrderItem
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
# Create your views here.

# user side
from django.db.models import Q

from django.shortcuts import render,redirect
from cart.models import Cart
from userprofile.models import Address
from checkout.models import Order,OrderItem
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
# Create your views here.

# user side



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

    print(order_id, order_od_status, '1111111111')

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

        print("Keyword:", keyword)  # Debug statement
        print("Number of Orders:", orders.count())  # Debug statement

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