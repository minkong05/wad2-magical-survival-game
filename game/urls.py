from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('api/attack/', views.perform_attack, name='api_attack'),
]