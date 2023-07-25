from django.urls import path
from .import views
urlpatterns = [
    path('checkout/',views.checkout,name='checkout'),
    path('add_checkout_address/',views.add_checkout_address,name='add_checkout_address'),
    path('placeorder/',views.placeorder,name='placeorder'),
    path('proceedtopay/', views.razarypaycheck, name = 'razarypaycheck'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),

]