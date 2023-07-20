from django.urls import path

from .views import *

urlpatterns=[

    path('admin_login/',admin_login,name='admin_login'),
    path('admin_signup/',admin_signup,name='admin_signup'),
    path('',dashboard,name='dashboard'),
    path('admin_logout/',admin_logout,name='admin_logout'),
    path('user/',user, name='user'),
    path('user/blockuser/<int:user_id>',blockuser, name='blockuser'),
    path('user/searchuser/',searchuser, name='searchuser'),
    path('salesreport/',salesreport, name="salesreport"),
    path('export_csv/',export_csv, name="export_csv"),
    path('export_pdf/',export_pdf, name="export_pdf"),
   



]
