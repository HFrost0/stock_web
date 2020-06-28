from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('get_recent_shares', views.get_recent_shares),
    path('get_stocks', views.get_stocks),
    path('get_stock_detail', views.get_stock_detail),
]
