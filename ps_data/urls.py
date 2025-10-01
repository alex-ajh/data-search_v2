from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'ps_data'
urlpatterns = [
    path('', views.index, name='ps_data_index'),
    path('help/', views.help, name='ps_data_help'),
]
