from django.shortcuts import render, redirect
import logging
from .models import category
from django.contrib import messages 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator
# Create your views here.


@login_required(login_url='admin_login')
def categories(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    category_data = category.objects.all().order_by('id')

    # Number of categories per page
    categories_per_page = 10
    paginator = Paginator(category_data, categories_per_page)

    page = request.GET.get('page')
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        categories = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        categories = paginator.page(paginator.num_pages)

    return render(request, 'category/category.html', {'category': categories})

# Crete category
@login_required(login_url='admin_login')
def createcategory(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        image = request.FILES.get('image', None)
        name = request.POST['categories']
        description = request.POST['categories_discription']
    # validation
        if name.strip() =='':
            messages.error(request,'Image Not Fount')
            return redirect('categories')
        if not image:
            messages.error(request, "Image not uploaded")
            return redirect('categories')
        if category.objects.filter(categories=name).exists():
            messages.error(request, 'category name already exists')
            return redirect('categories')
    # Save
        categr = category(categories=name,categories_discription = description,categories_image=image)
        categr.save()
        return redirect('categories')
    

# Edit Category
@login_required(login_url='admin_login')
def editcategory(request, editcategory_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if request.method == 'POST':
        name = request.POST['categories']
        description = request.POST['categories_discription']

    # validation
        try:
            caterg = category.objects.get(slug=editcategory_id)
            image = request.FILES.get('image')
            if image:
                caterg.categories_image = image
                caterg.save()
        except category.DoesNotExist:
            messages.error(request,'Image Not Fount')
            return redirect('categories')
        if name.strip() == '':
            messages.error(request,'Name field is empty')
            return redirect('categories')
        if category.objects.filter(categories=name).exists():
            check = category.objects.get(slug = editcategory_id)
            if name == check.categories:
                pass
            else:
                messages.error(request, 'category name already exists')
                return redirect('categories')
        
        categr = category.objects.get(slug=editcategory_id)
        categr.categories = name
        categr.categories_discription = description
        categr.save()
        return redirect ('categories')

# Delete Category
@login_required(login_url='admin_login')
def deletecategory(request,deletecategory_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    categre = category.objects.get(id=deletecategory_id)
    categre.delete()
    return redirect('categories')

# Search Category
@login_required(login_url='admin_login')
def search_category(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            cate = category.objects.filter(categories__icontains=keyword).order_by('id')
            if cate.exists():
                context = {
                    'category': cate,
                }
                return render(request, 'category/category.html', context)
            else:
                message = "Category not found"
                return render(request, 'category/category.html', {'message': message})
        else:
            message = "Please enter a valid search keyword"
            return render(request, 'category/category.html', {'message': message})
    else:
        return render(request, '404.html')