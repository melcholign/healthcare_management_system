# urls for individual views function inside this app
# """
from django.urls import path, include
from .import views

urlpatterns = [
    path('registerDoctor',views.registerDoctor,name='registerDoctor'),
    path('registerPatient',views.registerPatient,name='registerPatient'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('account_page', views.get_account_page, name='account_page'),
]