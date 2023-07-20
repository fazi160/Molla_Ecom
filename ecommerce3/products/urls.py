from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.product, name='product'),
    path('createproduct/', views.createproduct, name='createproduct'),
    path('search_product/', views.search_product, name='search_product'),
    path('editproduct/<slug:editproduct_id>', views.editproduct, name='editproduct'),
    path('deleteproduct/<slug:deleteproduct_slug>', views.deleteproduct, name='deleteproduct'),
   
     
]
