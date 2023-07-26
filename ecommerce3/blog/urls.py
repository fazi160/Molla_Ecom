


from django.urls import path
from .views import *

urlpatterns = [
    path('', blog_show, name='blog_show'),
    path('blog/', blog, name='blog'),
    path('create_blog/', create_blog, name='create_blog'),
    path('delete_blog/<slug:deleteBlog_id>/', delete_blog, name='delete_blog'),  # Corrected the slug parameter name
    path('edit_blog/<slug:editBlog_id>/', edit_blog, name='edit_blog'),  # Corrected the slug parameter name
    path('search_Blog/', search_Blog, name='search_Blog'),
]
