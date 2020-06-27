from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('get_stocks', views.get_stocks),
    path('get_recent_shares', views.get_recent_shares),
    path('rank_by_share_times', views.rank_by_share_times),
    path('get_share/<str:ts_code>', views.get_share),
]
