from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Address,Wallet
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from cart.models import Cart
from wishlist.models import Wishlist
from checkout.models import Address
from checkout.models import Order,OrderItem
from django.http import JsonResponse
from accounts.models import ReferralCode




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def user_profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    orderitems = OrderItem.objects.filter(order__in=orders).order_by('-order__created_at')

    referral_code = ReferralCode.objects.filter(user=request.user).first()
    is_referral_code_used = referral_code.used if referral_code else False

    user_info = {
        'address': Address.objects.filter(user=request.user).first(),
        'user': User.objects.get(username=request.user),
        'wallets': Wallet.objects.filter(user=request.user),
        'referral_code': referral_code,
        'is_referral_code_used': is_referral_code_used,
        'cart': Cart.objects.filter(user=request.user).order_by('-id'),
        'wishlist': Wishlist.objects.filter(user=request.user).order_by('-id'),
        'addresses': Address.objects.filter(user=request.user),
        'orders': orders,
        'orderitems': orderitems,
    }

    return render(request, 'user/user_dashboard/userpro.html', user_info)




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')
def view_order_detail(request,orderitem_id):
    try:
        order_item = OrderItem.objects.filter(order__tracking_no=orderitem_id)
        order = Order.objects.get(tracking_no = orderitem_id)
    except Order.DoesNotExist:
        messages.error(request, "The specified OrderItem does not exist.")
        return redirect('orders')
    address = int(order.address.id)
    cotext = {
        'order' : order,
        'address': Address.objects.get(id=address),
        'order_item' : order_item,
    }
    return render(request, 'user/user_dashboard/order_detailed.html',cotext)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')
def add_address(request):

    if request.method == 'POST':

        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
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

        ads=Address()
        ads.user=request.user
        ads.first_name=first_name
        ads.last_name=last_name
        ads.address=address
        ads.city=city
        ads.pincode=pincode
        ads.phone=phone
        ads.email=email
        ads.state=state
        ads.save()

        return redirect('user_profile')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')  
def editprofile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        

        if username == '':
            messages.error(request, 'Username is empty')
            return redirect('user_profile')
        if first_name == '' or last_name == '':
            messages.error(request, 'First or Lastname is empty')
            return redirect('user_profile')

        try:
            user = User.objects.get(username=request.user)
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            messages.success(request, 'User profile updated successfully')
        except ObjectDoesNotExist:
            messages.error(request, 'User does not exist')

    return redirect('user_profile')


# Change Password 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')
def changepassword(request):
    
    if request.method == 'POST':
        
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')
        
    #  Validation
        if new_password != confirm_new_password:
            messages.error(request,'Password did not match')
            return redirect('user_profile')
        user = User.objects.get(username = request.user)
        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)
            
            messages.success(request, 'Password updated successfully')
            return redirect('user_profile')
        else:
            messages.error(request, 'Invalid old password')
            return redirect('user_profile')
    return redirect('user_profile')

# delete Address
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')
def deleteaddress(request,delete_id):
    address = Address.objects.get(id = delete_id)
    address.delete()
    return redirect('user_profile')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')
def edit_address(request,edit_id):

    if request.method == 'POST':

        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
        
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
def referral_check(request):
    user = request.user

    # Get the ReferralCode instance associated with the user
    referral_obj = get_object_or_404(ReferralCode, user=user)
    
    if referral_obj.used:
        messages.warning(request, 'You have already used a referral code.')
        return redirect('user_profile')

    if request.method == 'POST':
        
        user_input_code = request.POST.get('refid')
        

        try:
            # Try to get the ReferralCode object based on the provided code
            referral_code = ReferralCode.objects.get(code=user_input_code)
        except ReferralCode.DoesNotExist:
            # Referral code does not exist
            messages.warning(request, 'Invalid referral code.')
        else:
            # Check if the referral code is not related to the current user
            if referral_code.user != user:
                # Referral code is valid and not related to the current user
                

                # Add money to the wallet of the user related to the referral code (50 units)
                add_money_to_wallet(referral_code.user, 50)

                # Add money to the wallet of the current user (referrer) (100 units)
                add_money_to_wallet(user, 100)

                # Mark the referral code as used
                referral_code.used = True
                referral_code.save()

                # Mark the user as having used a referral code
                referral_obj.used = True
                referral_obj.save()

                # You can perform additional actions if needed, like giving rewards, etc.

            else:
                # Referral code is related to the current user
                messages.warning(request, 'Referral code is already associated with your account.')

    return redirect('user_profile')





def add_money_to_wallet(user, amount):
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        # Create a new wallet if it doesn't exist for the user
        wallet = Wallet.objects.create(user=user, wallet=amount)
    else:
        # Update the existing wallet balance
        wallet.wallet += amount
        wallet.save()

