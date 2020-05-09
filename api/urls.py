from django.urls import path

from . import views

urlpatterns = [
    path('validate', views.validate_hashes, name='validate'),
    path('create_document', views.create_document, name='create_document'),
    path('hash', views.index, name='hash'),
    path('hash_string', views.hash_string, name='hash_string')
]