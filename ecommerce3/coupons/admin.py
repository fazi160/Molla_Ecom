from django.contrib import admin

# Register your models here.
from .models import Coupon,Usercoupon

admin.site.register(Coupon)
admin.site.register(Usercoupon)