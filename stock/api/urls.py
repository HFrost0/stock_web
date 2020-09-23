from django.urls import path
from . import views

urlpatterns = [
    path('get_shares', views.get_shares),
    path('get_stocks', views.get_stocks),
    path('get_stock', views.get_stock),
    path('get_daily_basics', views.get_daily_basics),
    path('get_range', views.get_range),

    path('login', views.login),
    path('registry', views.registry),
    path('test_auth', views.test_auth),
]
