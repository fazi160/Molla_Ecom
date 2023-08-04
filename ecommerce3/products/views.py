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
from django.core.files.uploadedfile import SimpleUploadedFile
import re
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.paginator import Paginator

# Product
@login_required(login_url='admin_login')
def product(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    products_list = products.objects.all().order_by('id')
    paginator = Paginator(products_list, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category.objects.all(),
        'author': author.objects.all(),
        'offer': Offer.objects.all(),
    }
    return render(request, 'product/product.html', context)



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
            return messages.error(request, 'Product name already exists')

        try:
            is_available = request.POST.get('checkbox', False)
            if is_available == 'on':
                is_available = True
            else:
                is_available = False
        except:
            is_available = False

        if name == '' or price == '':
            return messages.error(request, 'Name or Price field is empty')

        if name.strip() == '':
            return messages.error(request, 'Image Not Found')

        if not image:
            return messages.error(request, 'Image not uploaded')

        try:
            category_obj = category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return messages.error(request, 'Category matching query does not exist')

        try:
            author_obj = author.objects.get(author_name=authorname)
        except ObjectDoesNotExist:
            return messages.error(request, 'Author matching query does not exist')

        # Check if offer is valid and discount_amount is less than product_price
        if offer_id:
            if offer_id.is_offer_expired():
                messages.error(request, 'Selected offer is not valid.')
                return redirect('product')
            if offer_id.discount_amount >= float(price):
                messages.error(request, 'Discount amount must be less than the product price.')
                return redirect('product')

        # Save the product
        product = products(
            product_name=name,
            product_price=price,
            product_image=image,
            product_description=description,
            product_description_detailed=detailed_description,
            is_available=is_available,
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
        detailed_description = request.POST.get('product_description_detailed')
        authorname = request.POST.get('author')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity')
        
        # validation
        offer_id = request.POST.get('original_offer_id')  # Retrieve original offer ID from the hidden field

        offer = request.POST.get('offer')
        if offer == 'No offer':
            offer_id = None
        else:
            try:
                offer_id = Offer.objects.get(id=offer)
            except Offer.DoesNotExist:
                messages.error(request, 'Selected offer does not exist')
                return redirect('product')

        if pname == '' or pprice == '':
            messages.error(request, "Name or Price field is empty")
            return redirect('product')

        if products.objects.filter(product_name=pname).exists():
            check = products.objects.get(slug=editproduct_id)
            if pname != check.product_name:
                messages.error(request, 'Product name already exists')
                return redirect('product')

        cates = category.objects.get(id=category_id)
        produc = author.objects.get(author_name=authorname)

        # Check if offer is valid and discount_amount is less than product_price
        if offer_id:
            try:
                if offer_id.discount_amount >= float(pprice):
                    messages.error(request, "Discount amount must be less than the product price.")
                    return redirect('product')
            except ValueError:
                messages.error(request, "Invalid price or discount amount.")
                return redirect('product')

        # Save the updates
        product.product_name = pname
        product.product_price = pprice
        product.product_description = cdescription
        product.product_description_detailed = detailed_description
        product.is_available = request.POST.get('checkbox', False) == 'on'
        product.quantity = quantity
        product.author = produc
        product.category = cates
        product.offer = offer_id
        product.save()

        messages.success(request, 'Product updated successfully')
        return redirect('product')


    # If it's not a POST request, render the edit product form
    categories = category.objects.all()
    authors = author.objects.all()
    offers = Offer.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'authors': authors,
        'offers': offers,
    }
    return render(request, 'product/editproduct.html', context)
    



@login_required(login_url='admin_login')
def search_product(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        print(keyword, "15151515151511511")
        if keyword:
            prod_list = products.objects.filter(product_name__icontains=keyword).order_by('id')
            paginator = Paginator(prod_list, 10)  # Show 10 products per page for search results
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            if prod_list.exists():
                context = {
                    'page_obj': page_obj,  # Use 'page_obj' for pagination in the template
                    'category': category.objects.all(),
                    'author': author.objects.all(),
                    'offer': Offer.objects.all(),
                }
                return render(request, 'product/product.html', context)
            else:
                message = "Product not found."
                return render(request, 'product/product.html', {'message': message})
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








