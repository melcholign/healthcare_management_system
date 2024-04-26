from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.home, name='index'),
    path('make_appointment', views.make_appointment, name='make_appointment'),
    path('appointment_list', views.appointment_list, name='appointment_list'),
]