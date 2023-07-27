from django.shortcuts import render,redirect
from django.views.decorators.cache import cache_control,never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages,auth
from .models import UserOTP
import re
import random
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from .models import ReferralCode
from userprofile.models import Wallet

# Create your views here.
import random
import string

def generate_referral_code():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(8))
    return code



def add_to_wallet(user, amount):
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        # Create a new wallet if it doesn't exist for the user
        wallet = Wallet.objects.create(user=user, wallet=amount)
    else:
        # Update the existing wallet balance
        wallet.wallet += amount
        wallet.save()

        

def user_signup(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':

        get_otp = request.POST.get('otp')

        if get_otp:

            get_email = request.POST.get('email')
            usr=User.objects.get(email=get_email)

            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active=True
                usr.save()
                auth.login(request,usr)
                 # messages.success(request,f'Account is created for {usr.email}')
                UserOTP.objects.filter(user=usr).delete()

                # Assign referral code after user is active
                referral_code = generate_referral_code()

                while ReferralCode.objects.filter(code=referral_code).exists():
                    # Regenerate referral code if it already exists in the ReferralCode table
                    referral_code = generate_referral_code()

                ReferralCode.objects.create(user=usr, code=referral_code)

                # Add 10 units to the user's wallet
                add_to_wallet(usr, 0)

                return redirect('home')
            else:
                messages.warning(request,f'you Entered a Wrong OTP')
                return render(request,'accounts/register.html')

        #user validation
        else:

            firstname=request.POST['fname']
            lastname=request.POST['lname']
            username=request.POST['username']
          
            email=request.POST['email']
            password1=request.POST['password1']    
            password2=request.POST['password2']

            #null values checking 

            check=[username,email,password1,password2]

            for values in check:

                if values == '':
                    context ={

                        'pre_firstname' :firstname,
                        'pre_lastname':lastname,
                        'pre_username':username,
                        'pre_email':email,
                        'pre_password1':password1,
                        'pre_password2':password2
                        

                    }
                    messages.info(request,'some fields are empty')
                    return render(request,'accounts/register.html',context)
                else:
                    pass
            result=validate_username(username)

            if result is not False:
                context={
                     'pre_firstname' :firstname,
                        'pre_lastname':lastname,
                        'pre_username':username,
                      
                        'pre_email':email,
                        'pre_password1':password1,
                        'pre_password2':password2
                        

                    }
                messages.info(request,result)
                return render(request,'accounts/register.html',context)
            else:
                pass

            resmail=validateemail(email)


            if resmail is False:
                context={
                        'pre_firstname' :firstname,
                        'pre_lastname':lastname,
                        'pre_username':username,
                      
                        'pre_email':email,
                        'pre_password1':password1,
                        'pre_password2':password2
                        

                    }
                messages.info(request,'enter valid email')
               
                return render(request,'accounts/register.html',context)
           
            passw = validatepassword(password1)

            if passw is False:
                context={
                        'pre_firstname' :firstname,
                        'pre_lastname':lastname,
                        'pre_username':username,
                      
                        'pre_email':email,
                        'pre_password1':password1,
                        'pre_password2':password2
                        

                    }
                messages.info(request,'Enter strong password')
                return render(request,'accounts/register.html',context)
            else:
                pass

            

            if password1 == password2:

                try:
                    User.objects.get(email=email)
                except:
                    usr=User.objects.create_user(first_name=firstname,last_name=lastname,username=username,email=email,password=password1)
                    usr.is_active=False
                    usr.save()

                    user_otp=random.randint(100000,999999)
                    UserOTP.objects.create(user=usr,otp=user_otp)
                    mess=f'Hello \t{usr.username},\nYour OTP to verify your account is {user_otp}\n Thanks You!'
                    send_mail(
                        "Welcome to Dualip , verify your Email",
                        mess,
                        settings.EMAIL_HOST_USER,
                        [usr.email],

                        fail_silently=False


                        )
                    return render(request,'accounts/register.html',{'otp':True,'usr':usr})
                else:
                    context={
                        'pre_firstname' :firstname,
                        'pre_lastname':lastname,
                        'pre_username':username,
                       
                        'pre_email':email,
                        'pre_password1':password1,
                        'pre_password2':password2
                        

                    }
                    messages.error(request,'Email already exists')
                    return render(request,'accounts/register.html',context)
            else:
                context={
                        'pre_firstname' :firstname,
                        'pre_lastname':lastname,
                        'pre_username':username,
                       
                        'pre_email':email,
                        'pre_password1':password1,
                        'pre_password2':password2
                        

                    }
                messages.error(request,'passwords mismatch')
                return render(request,'accounts/register.html',context)
    else:

        return render(request,'accounts/register.html')


def validate_username(value):
    if not re.match(r'^[a-zA-Z\s]*$',value):

        return 'Name should only contain alphabets '
    elif value.strip() =='' or value.strip() == " ":
        return 'Name field cannot be empty'
    elif User.objects.filter(username=value).exists():
        return 'Username already exists'
    else:
        return False


def validateemail(email):

    from django.core.validators import validate_email

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def validatepassword(password):
    from django.contrib.auth.password_validation import validate_password
    try:
        validate_password(password)
        return True
    except ValidationError:
        return False


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username=request.POST['username']
        passwd=request.POST['password']

        #validation

        if username.strip() == '' or passwd.strip() == '':
            messages.error(request,"fields can't be blank")
            return redirect('user_login')
        user =authenticate(username=username,password=passwd)
        if user is not None and user.is_active:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Your username or password is incorrect ')
            return redirect('user_login')

    return render(request,'accounts/login.html')





def forgot_password(request):

    if request.method=='POST':
        get_otp=request.POST.get('otp')
        if get_otp:
            get_email=request.POST.get('email')
            usr=User.objects.get(email=get_email)
            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                user = User.objects.get(email = get_email)
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                Pass = validatepassword(password1)
                if password1 == password2:
                    if Pass is False:
                        context ={
                                'pre_otp':get_otp,
                            }
                        messages.info(request,'Enter Strong Password')
                        return render(request,'accounts/forgotpassword.html',context)
                    user.set_password(password1)
                    user.save()
                    UserOTP.objects.filter(user=usr).delete()
                    return redirect('user_login')
                else:
                    messages.error(request,"Password dosn't match")
            else:
                messages.warning(request,f'You Entered a wrong OTP')
                return render(request,'accounts/forgotpassword.html',{'otp':True,'usr':usr})
            
        # User rigistration validation
        else:
            email = request.POST['email']
            # null values checking
            check = [email]
            for values in check:
                if values == '':
                    context ={
                       'pre_email':email,
                    }
                    return render(request,'accounts/forgotpassword.html',context)
                else:
                    pass

            result = validateemail(email)
            if result is False:
                context ={
                        'pre_email':email,
                    }
                messages.info(request,'Enter valid email')
                return render(request,'accounts/forgotpassword.html',context)
            else:
                pass
            
            if User.objects.filter(email = email).exists():
                usr = User.objects.get(email=email) 
                user_otp=random.randint(100000,999999)
                UserOTP.objects.create(user=usr,otp=user_otp)
                mess=f'Hello\t{usr.username},\nYour OTP to verify your account for JUST watches is {user_otp}\nThanks!'
                send_mail(
                        "welcome to Molla  Verify your Email",
                        mess,
                        settings.EMAIL_HOST_USER,
                        [usr.email],
                        fail_silently=False
                    )
                return render(request,'accounts/forgotpassword.html',{'otp':True,'usr':usr})
            else:
                messages.info(request,'You have not an account')
                return render (request, 'accounts/forgotpassword.html')
    return render (request, 'accounts/forgotpassword.html')


