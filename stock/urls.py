from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<str:ts_code>', views.get_share, name='detail'),
    path('rank_by_share_times', views.rank_by_share_times, name='rank_by_share_times'),
    path('recent_shares', views.recent_shares, name='recent_shares'),
    path('recent_shares_api', views.recent_shares_api, name='recent_shares_api'),
    path('get_shares_by_time_point', views.get_shares_by_time_point, name='get_shares_by_time_point')
]
