from django.urls import path
from . import views  
from accounts import views as accounts_views 

urlpatterns = [
    path('', views.home, name='home'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('main/', views.main, name='main'),

    path('login/', accounts_views.user_login, name='login'),
    path('register/', accounts_views.user_register, name='register'),
    path('logout/', accounts_views.user_logout, name='logout'),
    path('myaccount/', accounts_views.myaccount, name='myaccount'),
]