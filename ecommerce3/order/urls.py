from django.urls import path
from .import views
urlpatterns = [
 
 path('orders/',views.admin_orders,name='admin_orders'),
 path('changestatus/',views.changestatus,name='changestatus'),
 path('change_od_status/',views.change_od_status,name='change_od_status'),
 path('search_orders/', views.search_orders, name='search_orders'),
 path('ordercancel/',views.ordercancel,name='ordercancel'),
 path('orderreturn/<int:return_id>',views.orderreturn,name='orderreturn'),



]