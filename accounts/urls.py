# urls for individual views function inside this app
# """
from django.urls import path, include
from . import views
from index import views as index_views

urlpatterns = [
    path('registerDoctor',views.registerDoctor,name='registerDoctor'),
    path('registerPatient',views.registerPatient,name='registerPatient'),
    path('account_login', views.account_login, name='account_login'),
    path('account_logout', views.account_logout, name='account_logout'),
    path('account_page', views.get_account_page, name='account_page'),
]

urlpatterns += [
    path('account_page/change_availability', views.change_availability, name='change_availability'),
    path('account_page/make_appointment', index_views.make_appointment, name='make_appointment'),
    path('account_page/patient_appointment_list', index_views.patient_appointment_list, name='patient_appointment_list'),
    path('account_page/doctor_appointment_list', index_views.doctor_appointment_list, name='doctor_appointment_list')
]

urlpatterns += [
    path('schedules', views.schedules, name='schedules')
]