from django.shortcuts import render,redirect
from django.views.decorators.cache import cache_control,never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout as dj_logout
from products.models import Product
from categories.models import category
from authors.models import author
from django.contrib.auth.models import User
from wishlist.models import Wishlist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.models import Count
from cart.models import Cart
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
  

def home(request):

    pro=Product.objects.all()
    cate=category.objects.all()
    auth = author.objects.all()
    last_added = Product.objects.latest('id')

    return render(request,'home.html',{'products_list':pro, 'categories':cate, 'authors':auth, 'last_added':last_added})

def shop(request):
    cate=category.objects.all()

    return render(request,'catagory.html',{'categories':cate})

def category_detail(request, cat_id):
    all_categories = category.objects.all()
    all_authors = author.objects.all()

    # Pass the filtered products and all categories/authors to the template
    
    
    products = Product.objects.select_related('category').filter(category__id=cat_id)
    context = {
        'products': products,
        'cate': all_categories,
        'author': all_authors,
    }
    return render(request, 'product.html', context)







def filter_products(request):
    if request.method == 'POST':
        
        selected_categories = request.POST.getlist('categories[]')
        selected_authors = request.POST.getlist('authors[]')
        
        

        # Filter products based on selected categories and authors
        filtered_products = Product.objects.all()

        if selected_categories:
            
            filtered_products = filtered_products.filter(category__categories__in=selected_categories)

        if selected_authors:
            filtered_products = filtered_products.filter(author__author_name__in=selected_authors)

        context = {
            'products': filtered_products,
        }

        # Render the HTML template for the filtered products
        product_list_html = render_to_string('filtered_product_list.html', context)

        # Return the JSON response with the filtered product list HTML
        return JsonResponse({'product_list_html': product_list_html})
    else:
        # Handle the GET request
        return JsonResponse({})



def product_show(request):
    # Get the selected sorting option from the URL query parameters
    sort = request.GET.get('sort')

    # Sort products based on the selected option
    if sort == 'atoz':
        products = Product.objects.all().order_by('product_name')
    elif sort == 'ztoa':
        products = Product.objects.all().order_by('-product_name')
    elif sort == 'ltoh':
        products = Product.objects.all().order_by('product_price')
    elif sort == 'htol':
        products = Product.objects.all().order_by('-product_price')
    else:
        products = Product.objects.all()

    # Get the selected categories and authors from the URL query parameters
    selected_categories = request.GET.getlist('categories')
    selected_authors = request.GET.getlist('authors')

    # Filter products based on selected categories and authors
    if 'all' not in selected_categories and selected_categories:
        products = products.filter(category__categories__in=selected_categories)

    if 'all' not in selected_authors and selected_authors:
        products = products.filter(author__author_name__in=selected_authors)

    # Retrieve all categories and authors for the sidebar filter
    all_categories = category.objects.all()
    all_authors = author.objects.all()

    # Pass the filtered products and all categories/authors to the template
    context = {
        'products': products,
        'cate': all_categories,
        'author': all_authors,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render the filtered product list template and return it as JSON response
        product_list_html = render_to_string('filtered_product_list.html', context)
        return JsonResponse({'product_list_html': product_list_html})
    else:
        # For regular non-AJAX requests, render the entire page with the product list
        return render(request, 'product.html', context)

def product_detail(request,product_id):


    prod=Product.objects.get(id=product_id)
    # related=product.objects.all()
    related = Product.objects.order_by('?')[:5]

    return render(request,'inner_product.html', {'pro_detail':prod ,'allpro':related})

@login_required(login_url='user_login')
def user_logout(request):
    if request.user.is_authenticated:
        
        dj_logout(request)
        return redirect('user_login')
    else:
        return redirect('home')

@login_required(login_url='user_login')
def shoppingcart(request):

    return render(request,'shoping-cart.html')

def about(request):

    return render(request,'about.html')



def search_view(request):
    query = request.GET.get('q')
    products = []
    categories = []
    

    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) | 
            Q(product_description__icontains=query) |
            Q(author__author_name__icontains=query)  |
            Q(product_description_detailed__icontains=query)
        )

        categories = category.objects.filter(
            Q(categories__icontains=query) |
            Q(categories_discription__icontains=query)
           
        )

       

    return render(request, 'search.html', {'query': query, 'products': products, 'categories': categories})

def update_counts(request):
    wishlist_count = 0
    cart_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()

    return JsonResponse({"wishlist_count": wishlist_count, "cart_count": cart_count})
