from django.urls import path
from django.conf.urls import handler404, handler500

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.update_data, name='update'),
    path('sharing/', views.request_sharing, name='sharing'),
    path('patient/<str:session_id>', views.view_patient, name='patient'),
    path('create_session', views.create_session, name='create_session'),
]

handler404 = 'healthcare.views.hp_handle_404'