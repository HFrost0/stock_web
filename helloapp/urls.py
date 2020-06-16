from django.urls import path, include
from . import views

app_name = 'helloapp'
urlpatterns = [
    path('', views.hello, name='index'),
    path('your_name/', views.get_name, name='your_name')
]
