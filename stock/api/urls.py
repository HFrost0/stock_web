from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('get_shares', views.get_shares),
    path('get_stocks', views.get_stocks),
    path('get_stock', views.get_stock),
]
