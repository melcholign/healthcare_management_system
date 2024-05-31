from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.home, name='index'),
    path('prescribe/<str:appointmentID>', views.prescribe, name='prescirbe'),
    path('diagnosis/<str:appointmentID>', views.diagnosis, name='diagnosis'),
    path('attend_appointment/<int:appointment_id>', views.attend_appointment, name='attend_appointment')
]