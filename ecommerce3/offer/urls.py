from django.urls import path
from .import views
urlpatterns = [
 
 path('adminoffer/',views.adminoffer,name='adminoffer'),
 path('addoffer/',views.addoffer,name='addoffer'),
 path('editoffer/<int:offer_id>',views.editoffer,name='editoffer'),
 path('deleteoffer/<int:delete_id>',views.deleteoffer,name='deleteoffer'),
 


]