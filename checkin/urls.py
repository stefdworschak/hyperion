from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('checkin/', views.checkin, name='post_checkin')
]