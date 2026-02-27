from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),         
    path("Home/", views.home, name="home"),
    path("AboutUs/", views.aboutus, name="aboutus"),
]