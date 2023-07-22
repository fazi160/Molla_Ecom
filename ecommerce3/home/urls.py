from django.urls import path

from . import views

urlpatterns=[

    path('', views.home,name='home'),
    path('user_logout/',views.user_logout, name='user_logout'),
    # path('shoppingcart/',views.shoppingcart,name='shoppingcart'),
    path('product_show/',views.product_show, name='product_show'),
    path('sample/',views.sample,name='sample'),
    path('about/',views.about,name='about'),
    path('shop/',views.shop, name='shop'),
    path('products/<slug:product_id>/',views.product_detail,name='product_detail'),
    path('category_detail/<int:cat_id>/', views.category_detail, name='category_detail'),
    path('filter_products/', views.filter_products, name='filter_products'),
    path('search/', views.search_view, name='search'),
    # path('get_suggestions/', views.get_suggestions, name='get_suggestions'),
]