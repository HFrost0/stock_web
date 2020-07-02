from django.urls import path
from . import views

urlpatterns = [
    path('get_shares', views.get_shares),
    path('get_stocks', views.get_stocks),
    path('get_stock', views.get_stock),
    path('get_daily_basic', views.get_daily_basic),
]
