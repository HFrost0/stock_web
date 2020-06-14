from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<str:ts_code>', views.get_share, name='detail'),
    path('rank_by_share_times', views.rank_by_share_times, name='rank_by_share_times')
]
