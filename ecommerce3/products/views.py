from django.shortcuts import render,redirect
from categories.models import category
from django.contrib import messages
from .models import Product as products 
from .models import Product
from authors.models import author
import logging
from django.http import HttpResponse
from image_cropping import ImageRatioField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.contrib.auth.decorators import login_required
# from image_cropping import get_backend
from PIL import Image
from io import BytesIO

# Create your views here.

@login_required(login_url='admin_login')
def createproduct(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    if request.method == 'POST':
        name = request.POST['product_name']
        price = request.POST['product_price']
        quantit = request.POST.get('quantity')
        image = request.FILES.get('product_image', None)
        authorname = request.POST.get('author')
        category_id = request.POST.get('category')
        description = request.POST['product_description']
        detailed_description = request.POST['product_description_detailed']

        # Validation here

        if Product.objects.filter(product_name=name).exists():
            messages.error(request, 'Product name already exists')
            return redirect('product')

        try:
            is_available = request.POST.get('checkbox', False)
            if is_available == 'on':
                is_available = True
            else:
                is_available = False
        except:
            is_available = False

        if name == '' or price == '':
            messages.error(request, "Name or Price field are empty")
            return redirect('product')

        if not image:
            messages.error(request, "Image not uploaded")
            return redirect('product')

        category_id = int(category_id)
        try:
            category_instance = category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Invalid Category selected")
            return redirect('product')

        try:
            author_instance = author.objects.get(author_name=authorname)
        except Author.DoesNotExist:
            messages.error(request, "Invalid Author selected")
            return redirect('product')

        # Automatically crop the image and save the cropping data
        if image:
            with Image.open(image) as img:
                img = img.resize((200, 200), Image.ANTIALIAS)
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                buffer.seek(0)

        # Save the cropped image and other data to the model
        product = Product(
            product_name=name,
            product_price=price,
            product_image=image,
            product_description=description,
            product_description_detailed=detailed_description,
            is_available=is_available,
            author=author_instance,
            category=category_instance,
            quantity=quantit,
        )
        product.save()
        return redirect('product')

    return render(request, 'product/product.html', {
        'category': Category.objects.all(),
        'author': Author.objects.all(),
    })

# Product
@login_required(login_url='admin_login')
def product(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    prodec = products.objects.all().order_by('id')
    dict_list={
        'prod' : prodec,
        'category' : category.objects.all(),
        'author': author.objects.all(),
        
       
    }
    return render(request , 'product/product.html', dict_list)






@login_required(login_url='admin_login')
def editproduct(request, editproduct_id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    try:
        product = products.objects.get(slug=editproduct_id)
    except products.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('product')

    if request.method == 'POST':
        pname = request.POST['product_name']
        pprice = request.POST['product_price']
        cdescription = request.POST['product_description']
        detaile_description = request.POST['product_description_detailed']
        authorname = request.POST.get('author')
        category_id = request.POST.get('category')
        quantit = request.POST.get('quantity')

        # Validation and saving the changes
        try:
            pro = products.objects.get(slug=editproduct_id)
            image = request.FILES.get('product_image')
            if image:
                pro.product_image = image
                pro.save()
        except products.DoesNotExist:
            messages.error(request, 'Image not found')
            return redirect('product')

        try:
            is_availables = request.POST.get('checkbox', False)
            if is_availables == 'on':
                is_availables = True
            else:
                is_availables = False
        except:
            is_availables = False

        if pname == '' or pprice == '':
            messages.error(request, 'Name or Price field is empty')
            return redirect('product')

        if products.objects.filter(product_name=pname).exists():
            check = products.objects.get(slug=editproduct_id)
            if pname != check.product_name:
                messages.error(request, 'Product name already exists')
                return redirect('product')

        cates = category.objects.get(id=category_id)
        produc = author.objects.get(author_name=authorname)
        

        cat = products.objects.get(slug=editproduct_id)
        cat.product_name = pname
        cat.quantity = quantit
        cat.product_price = pprice
        cat.product_description = cdescription
        cat.product_description_detailed = detaile_description
        cat.is_available = is_availables
        cat.author = produc
        cat.category = cates
        cat.save()

        return redirect('product')
    else:
        # Pre-fill the form with the existing values
        dict_list = {
            'product': product,
            'category': category.objects.all(),
            'author': author.objects.all(),
            
        }
        return render(request, 'product/edit_product.html', dict_list)

    

# # Search Product
@login_required(login_url='admin_login')
def search_product(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            Prod = products.objects.filter(product_name__icontains=keyword).order_by('id')
            if Prod.exists():
                context = {
                    'prod': Prod,
                }
                return render(request, 'product/product.html',context)
            else:
                message = "Product not found."
                return render(request,'product/product.html', {'message': message})
        else:
            message = "Please enter a valid search keyword"
            return render(request, 'product/product.html', {'message': message})
    else:
        return render(request, '404.html')




def deleteproduct(request,deleteproduct_slug):
    if not request.user.is_superuser:
        return redirect('admin_login')
    pro = products.objects.get(slug=deleteproduct_slug)
    
    pro.delete()

    return redirect('product')









