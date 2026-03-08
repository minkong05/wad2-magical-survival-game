from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path('main/', views.main, name='main'),
    path("character-select/", views.character_select, name="character_select"),
]