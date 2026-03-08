from django.urls import path
from . import views

app_name ='game'

urlpatterns = [
    path('main/', views.main, name='main'),
    path("shop/", views.shop, name="shop"),
    path("shop/buy/<int:item_id>/", views.buy_item, name="buy_item"),
]