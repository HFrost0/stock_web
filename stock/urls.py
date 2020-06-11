from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:ts_code>', views.get_share, name='detail')
]
