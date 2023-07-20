from django.urls import path
from .import views



urlpatterns = [
path('',views.cart,name='cart'),
path('add_cart',views.add_cart,name='add_cart'),
path('update_cart',views.update_cart,name='update_cart'),
path('deletecartitem/<int:product_id>',views.deletecartitem,name='deletecartitem')

]