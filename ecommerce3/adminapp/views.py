from accounts.models import UserOTP
from categories.models import category
from checkout.models import Order, OrderItem
from datetime import datetime,timedelta
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import DateField
from django.db.models import Sum
from django.db.models.functions import TruncDay, Cast
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import datetime, timedelta
from django.views.decorators.cache import cache_control
from itertools import groupby
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus.flowables import KeepInFrame
import csv
import random
import re
import io


# Create your views here.
def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Validation
        if username.strip() == '' or password.strip() == '':
            messages.error(request, "Fields can't be blank")
            return redirect('admin_login')

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect('dashboard')
            else:
                messages.error(request, "You are not a superuser")
                return redirect('admin_login')

        messages.error(request, "Invalid email or password")
        return redirect('admin_login')

    return render(request, 'adminapp/adminlogin.html')

# validations
def validateEmail(email):
    from django.core.validators import validate_email
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def ValidatePassword(password):
    from django.contrib.auth.password_validation import validate_password
    try:
        validate_password(password)
        return True
    except ValidationError:
        return False
    
def validate_name(value):
    if not re.match(r'^[a-zA-Z\s]*$', value):
        return 'Name should only contain alphabets and spaces'
    
    elif value.strip() == '':
        return 'Name field cannot be empty or contain only spaces' 
    elif User.objects.filter(username=value).exists():
        return 'Usename already exist'
    else:
        return False
    
def admin_signup(request):
    # OTP VERIFICATION

    if request.method == 'POST':
        get_otp = request.POST.get('otp')
        if get_otp:
            get_email = request.POST.get('email')
            usr = User.objects.get(email=get_email)
            if int(get_otp) == UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active = True
                usr.is_superuser = True
                usr.save()  # Save the changes to the user object
                auth.login(request, usr)
                messages.success(request, f'Account is created for {usr.email}')
                UserOTP.objects.filter(user=usr).delete()
                return redirect('dashboard')
            else:
                messages.warning(request, 'You Entered a wrong OTP')
                return render(request, 'adminapp/adminsignup.html', {'otp': True, 'usr': usr})

        # User registration validation
        else:
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']

            # Null values checking
            check = [email, password1, password2]
            for value in check:
                if value == '':
                    context = {
                        'pre_email': email,
                        'pre_password1': password1,
                        'pre_password2': password2,
                    }
                    messages.info(request, 'Some fields are empty')
                    return render(request, 'adminapp/adminsignup.html', context)

            result = validateEmail(email)
            if not result:
                context = {
                    'pre_email': email,
                    'pre_password1': password1,
                    'pre_password2': password2,
                }
                messages.info(request, 'Enter a valid email')
                return render(request, 'adminapp/adminsignup.html', context)

            Pass = ValidatePassword(password1)
            if not Pass:
                context = {
                    'pre_email': email,
                    'pre_password1': password1,
                    'pre_password2': password2,
                }
                messages.info(request, 'Enter a strong password')
                return render(request, 'adminapp/adminsignup.html', context)

            if password1 == password2:
                try:
                    User.objects.get(email=email)
                except User.DoesNotExist:
                    usr = User.objects.create_user(username=email, email=email, password=password1)
                    usr.is_active = False
                    usr.is_superuser = True
                    usr.save()
                    
                    user_otp = random.randint(100000, 999999)
                    UserOTP.objects.create(user=usr, otp=user_otp)
                    mess = f'Hello {usr.username},\nYour OTP to verify your account for just is {user_otp}\nThanks!'
                    send_mail(
                        "Welcome to just watches: Verify your Email",
                        mess,
                        settings.EMAIL_HOST_USER,
                        [usr.email],
                        fail_silently=False
                    )
                    return render(request, 'adminapp/adminsignup.html', {'otp': True, 'usr': usr})
                else:
                    context = {
                        'pre_email': email,
                        'pre_password1': password1,
                        'pre_password2': password2,
                    }
                    messages.error(request, 'Email already exists')
                    return render(request, 'adminapp/adminsignup.html', context)
            else:
                context = {
                    'pre_email': email,
                    'pre_password1': password1,
                    'pre_password2': password2,
                }
                messages.error(request, 'Password mismatch')
                return render(request, 'adminapp/adminsignup.html', context)
    else:
        return render(request, 'adminapp/adminsignup.html')




@login_required(login_url='admin_login')
def admin_logout(request):

    logout(request)
    return redirect('admin_login')

def user(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    user_data = User.objects.all().order_by('id')
    return render(request,'adminapp/users.html',{'users': user_data})

# Block User
def blockuser(request,user_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    user = User.objects.get(id=user_id)
    if user.is_active:
        user.is_active = False
        user.save()
    else:
        user.is_active = True
        user.save()
    return redirect('user')

# Search User
def searchuser(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            users = User.objects.filter(username__icontains=keyword).order_by('id')
            if users.exists():
                context = {
                    'users': users,
                }
                return render(request, 'adminapp/users.html', context)
            else:
                message = "User not found."
                return render(request, 'adminapp/user.html', {'message': message})
        else:
            message = "Please enter a valid search keyword"
            return render(request, 'adminapp/users.html', {'message': message})
    else:
        return render(request, '404.html')

def dashboard(request):
    if not request.user.is_superuser:
        return redirect('adminsignin')

    delivered_items = OrderItem.objects.filter(status='Delivered')

    revenue = 0
    for item in delivered_items:
        revenue += item.price * item.quantity

    top_selling = OrderItem.objects.annotate(total_quantity=Sum('quantity')).order_by('-total_quantity').distinct()[:5]

    recent_sale = OrderItem.objects.all().order_by('-id')[:5]

    today = timezone.now()
    date_range = 7
    four_days_ago = today - timedelta(days=date_range)

    orders = Order.objects.filter(created_at__gte=four_days_ago, created_at__lte=today)
    sales_by_day = orders.annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('total_price')).order_by('day')
    # formatted_dates = [item['day'].strftime('%Y-%m-%dT%H:%M:%S.%fZ') for item in sales_by_day]

    filter_value = request.GET.get('filter', 'all')  # Get the selected filter from the request query parameter

    # Determine the date range based on the selected filter
    if filter_value == 'today':
        today = timezone.now().date()
        sales_by_day = orders.filter(created_at__date=today).annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('total_price')).order_by('day')
    elif filter_value == '3_days':
        three_days_ago = today - timedelta(days=3)
        sales_by_day = orders.filter(created_at__gte=three_days_ago, created_at__lte=today).annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('total_price')).order_by('day')
    elif filter_value == '7_days':
        seven_days_ago = today - timedelta(days=7)
        sales_by_day = orders.filter(created_at__gte=seven_days_ago, created_at__lte=today).annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('total_price')).order_by('day')
    elif filter_value == '30_days':
        thirty_days_ago = today - timedelta(days=30)
        sales_by_day = orders.filter(created_at__gte=thirty_days_ago, created_at__lte=today).annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('total_price')).order_by('day')
    else:
        sales_by_day = orders.annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('total_price')).order_by('day')


    revenue += revenue * 0.18

    context = {
        'total_users': User.objects.count(),
        'sales': OrderItem.objects.count(),
        'revenue': revenue,
        'top_selling': top_selling,
        'recent_sales': recent_sale,
        'sales_by_day': sales_by_day,
    }
    return render(request, 'adminapp/dashboard.html', context)





def salesreport(request):
    if not request.user.is_superuser:
        return redirect('adminsignin')

    # Retrieve all orders in descending order of 'created_at'
    orders = Order.objects.all().order_by('-created_at')
    order_items = {}

    for order in orders:
        # Get all OrderItems for the current order
        items = OrderItem.objects.filter(order=order.id)
        order_items[order.id] = items

    context = {
        'orders': orders,
        'order_items': order_items
    }

    if request.method == 'POST':
        start_date = request.POST.get('start-date')
        end_date = request.POST.get('end-date')
        
        if start_date == '' or end_date == '':
            messages.error(request, 'Give date first')
            return redirect(salesreport)
            
        if start_date == end_date:
            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            order_items = OrderItem.objects.filter(order__created_at__date=date_obj.date()).select_related('order')
            if order_items:
                context.update(sales=order_items, s_date=start_date, e_date=end_date)
                return render(request, 'admin/salesreport.html', context)
            else:
                messages.error(request, 'No data found')
                return redirect(salesreport)

        order_items = OrderItem.objects.filter(order__created_at__date__gte=start_date, order__created_at__date__lte=end_date).select_related('order')

        if order_items:
            # Calculate total sales during the period
            total_sales = order_items.aggregate(Sum('price'))['price__sum']
            context.update(sales=order_items, s_date=start_date, e_date=end_date, total_sales=total_sales)
        else:
            messages.error(request, 'No data found')
    
    return render(request, 'adminapp/salesreport.html', context)


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['user', 'total_price', 'payment_mode', 'tracking_no', 'Orderd at', 'product_name', 'product_price', 'product_quantity'])

    orders = Order.objects.all()
    for order in orders:
        order_items = OrderItem.objects.filter(order=order).select_related('product')  # Use select_related to optimize DB queries
        grouped_order_items = groupby(order_items, key=lambda x: x.order_id)
        for order_id, items_group in grouped_order_items:
            items_list = list(items_group)
            for order_item in items_list:
                writer.writerow([
                    order.user if order_item == items_list[0] else "",
                    order.total_price if order_item == items_list[0] else "",
                    order.payment_mode if order_item == items_list[0] else "",
                    order.tracking_no if order_item == items_list[0] else "",
                    order.created_at if order_item == items_list[0] else "",  # Only include date in the first row
                    order_item.product.product_name,  # Replace 'product_name' with the actual attribute in your Product model
                    order_item.price,
                    order_item.quantity,
                ])

    return response




def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.now()) + '.pdf'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    styles = getSampleStyleSheet()

    # Header Information
    elements.append(Paragraph('Order Details Report', styles['Heading1']))
    elements.append(Paragraph(str(datetime.now()), styles['Normal']))

    # Table Data
    data = [['User', 'Total Price', 'Payment Mode', 'Tracking No', 'Ordered At', 'Product Name', 'Product Price', 'Product Quantity']]

    orders = Order.objects.all()
    for order in orders:
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        for i, order_item in enumerate(order_items):
            if i == 0:
                user = order.user.username
                total_price = str(order.total_price)
                payment_mode = order.payment_mode
                tracking_no = order.tracking_no
                ordered_at = str(order.created_at.date())
            else:
                user = ''
                total_price = ''
                payment_mode = ''
                tracking_no = ''
                ordered_at = ''
            product_name = Paragraph(order_item.product.product_name, styles['Normal'])
            product_price = str(order_item.price)
            product_quantity = str(order_item.quantity)
            data.append([user, total_price, payment_mode, tracking_no, ordered_at, product_name, product_price, product_quantity])

    # Create Table
    table = Table(data, hAlign='CENTER', colWidths=[60, 60, 60, 60, 60, 140, 60, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response