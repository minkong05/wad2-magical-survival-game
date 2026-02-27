from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name ='accounts'

urlpatterns = [
    path("Register", views.user_register, name="register"),
    path("Login", views.user_login, name="login"),
    path("Logout", views.user_logout, name="logout"),
]