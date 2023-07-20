from django.urls import path
from .import views
urlpatterns = [

    path('',views.wishlist,name='wishlist'),
    path('add_wishlist/',views.add_wishlist,name='add_wishlist'),
    path('delete_wishlist/<int:product_id>',views.delete_wishlist,name='delete_wishlist'),


]