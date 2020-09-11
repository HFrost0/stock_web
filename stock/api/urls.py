from django.urls import path
from . import views

urlpatterns = [
    path('get_shares', views.SharesView.as_view()),
    path('get_stocks', views.StocksView.as_view()),
    path('get_stock', views.StockView.as_view()),
    path('get_daily_basics', views.DailyBasicsView.as_view()),

    path('login', views.LoginView.as_view()),
    path('test_auth', views.TestAuthView.as_view()),
]
