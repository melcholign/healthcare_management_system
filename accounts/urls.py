# urls for individual views function inside this app
# """
from django.urls import path, include
from .import views

urlpatterns = [
    path('registerDoctor',views.registerDoctor,name='registerDoctor'),
    path('registerPatient',views.registerPatient,name='registerPatient'),
    path('account_login', views.account_login, name='account_login'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('account_page', views.get_account_page, name='account_page'),
]