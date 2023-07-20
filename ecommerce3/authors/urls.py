from django.urls import path

from .views import *

urlpatterns=[

    path('authors/', authors, name='authors'),
    path('search_author/',search_author, name='search_author'),
    path('createauthors/', createauthors, name='createauthors'),
    path('editauthors/<slug:editauthors_id>', editauthors, name='editauthors'),
    path('deleteauthors/<slug:deleteauthors_id>',deleteauthors, name='deleteauthors'),
   



]
