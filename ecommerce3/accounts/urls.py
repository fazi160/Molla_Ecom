
from django.urls import path
from . views import *   

urlpatterns = [
    path('user_signup/',user_signup, name='user_signup'),
    path('user_login/',user_login, name='user_login'),
    
    path('forgot_password/',forgot_password, name='forgot_password'),
     
    
]