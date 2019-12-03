from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.updateData, name='update'),
    path('sharing/', views.requestSharing, name='sharing'),
]