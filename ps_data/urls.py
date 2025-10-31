from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'ps_data'
urlpatterns = [
    path('', views.index, name='ps_data_index'),
    path('help/', views.help, name='ps_data_help'),
    path('download/folder-opener/<str:filename>/', views.download_folder_opener, name='download_folder_opener'),
    path('visit-stats/', views.visit_stats, name='visit_stats'),
    path('api/visit-chart-data/', views.visit_chart_data, name='visit_chart_data'),
    path('search-stats/', views.search_stats, name='search_stats'),
    path('api/search-chart-data/', views.search_chart_data, name='search_chart_data'),
]
