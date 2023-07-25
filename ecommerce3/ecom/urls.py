"""
URL configuration for ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    path('accounts/', include('accounts.urls')),
    path('owner/', include('adminapp.urls')),
    path('author/', include('authors.urls')),
    path('cart/', include('cart.urls')),
    path('categories/', include('categories.urls')),
    path('checkout/', include('checkout.urls')),
    path('', include('home.urls')),
    path('order/', include('order.urls')),
    path('products/',include('products.urls')),
    # path('shop/',include('shop.urls')),
    path('user/',include('userprofile.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('blog/', include('blog.urls')),
    path('offer/',include('offer.urls')),
    path('coupon/',include('coupons.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   