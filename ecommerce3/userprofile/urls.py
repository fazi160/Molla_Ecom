

from django.urls import path
from .import views
urlpatterns = [
    path('', views.user_profile, name='user_profile'),
    path('addaddress/', views.add_address, name='add_address'),
    path('editprofiles/', views.editprofile, name='edit_profile'),
    path('changepassword/', views.changepassword, name='change_password'),
    path('deleteaddress/<int:delete_id>', views.deleteaddress, name='deleteaddress'),
    path('vieworderdetail/<orderitem_id>', views.view_order_detail, name='view_order_detail'),
    path('edit_address/<int:edit_id>', views.edit_address, name='edit_address'),
    path('referral_check/', views.referral_check, name='referral_check')

]
