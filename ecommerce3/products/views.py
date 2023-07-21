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
from tkinter import Image
from .models import Product as products, Offer
from django.http import JsonResponse
# Create your views here.
from django.core.files.uploadedfile import SimpleUploadedFile
import re
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

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
        'offer' : Offer.objects.all(),
       
    }
    return render(request ,'product/product.html',dict_list)
    


@login_required(login_url='admin_login')
def createproduct(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    if request.method == 'POST':
        name = request.POST['product_name']
        price = request.POST['product_price']
        image = request.FILES.get('product_image', None)
        authorname = request.POST.get('author')
        category_id = request.POST.get('category')
        description = request.POST['product_description']
        quantity = request.POST['quantity']
        detailed_description = request.POST.get('product_description_detailed', '')  # Use get with a default value
        # Validation
        offer = request.POST.get('offer')
        if offer == 'No offer':
            offer_id = None
        else:
            try:
                offer_id = Offer.objects.get(id=offer)
            except ObjectDoesNotExist:
                return messages.error(request, 'Offer matching query does not exist')

        if products.objects.filter(product_name=name).exists():
            return messages.error(request,'product name already exist')

        try:
            is_availables = request.POST.get('checkbox', False)
            if is_availables == 'on':
                is_availables = True
            else:
                is_availables = False
        except:
            is_availables = False

        if name == '' or price == '':
            
            return messages.error(request,' Name or Price field is empty')

        if name.strip() == '':
            return messages.error(request,'Image Not Found')

        if not image:
            
            return messages.error(request,'Image not uploaded')

        try:
            category_obj = category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return messages.error(request,'Category matching query does not exist')

        try:
            author_obj = author.objects.get(author_name=authorname)
            
        except ObjectDoesNotExist:
            return messages.error(request,'Author matching query does not exist')

        # Save the product
        product = products(
            product_name=name,
            product_price=price,
            product_image=image,
            product_description=description,
            product_description_detailed=detailed_description,
            is_available=is_availables,
            author=author_obj,
            category=category_obj,
            quantity=quantity,
            offer=offer_id
        )
        product.save()

        messages.success(request, 'Product created successfully')
        return redirect('product')

    return render(request, 'product/product.html')



# Edit Product
@login_required(login_url='admin_login')
def editproduct(request,editproduct_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        pname = request.POST['product_name']
        pprice = request.POST['product_price']
        cdescription = request.POST['product_description']
        authorname = request.POST.get('author')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity')
        
    # validation
        offer = request.POST.get('offer')
        if offer == 'No offer':
            offer_id = None
        else:
            offer_id = Offer.objects.get(id=offer)
        try:
            pro = products.objects.get(slug=editproduct_id)
            image = request.FILES.get('product_image')
            if image:
                pro.product_image = image
                pro.save()
        except products.DoesNotExist:
            messages.error(request,'Image Not Found')
            return redirect('product')
    #  one here
        try:
            is_availables = request.POST.get('checkbox', False)
            if is_availables == 'on':
                is_availables = True
            else:
                is_availables = False
        except:
            is_availables = False

        if pname == '' or pprice =='' :
            messages.error(request, "Name or Price field are empty")
            return redirect('product')
        if products.objects.filter(product_name=pname).exists() :
            check = products.objects.get(slug = editproduct_id)
            if pname == check.product_name:
                pass
            else:
                messages.error(request, 'Product name already exists')
                return redirect('product')
        
        cates = category.objects.get(id=category_id)
        produc = author.objects.get(author_name=authorname)
        
    # Save       
        cat = products.objects.get(slug=editproduct_id)
        cat.product_name = pname
        
        cat.product_price = pprice
        cat.product_description = cdescription
        cat.is_available = is_availables
        cat.quantity=quantity
        cat.author = produc
        cat.category = cates
        cat.offer = offer_id
       
        cat.save()
        return redirect('product')
    

# Search Product
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








