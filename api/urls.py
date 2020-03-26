from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hash', views.hash_page, name='hash'),
    path('hash_string', views.hash, name='hash_sting')
]