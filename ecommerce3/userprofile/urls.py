

from django.urls import path
from .import views
urlpatterns = [
    path('', views.user_profile, name='profile'),
    path('addaddress/', views.add_address, name='addaddress'),
    path('editprofiles/', views.editprofile, name='editprofiles'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('deleteaddress/<int:delete_id>', views.deleteaddress, name='deleteaddress'),
    path('vieworderdetail/<orderitem_id>', views.view_order_detail, name='view_order_detail'),

]
