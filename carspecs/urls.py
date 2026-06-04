from django.urls import path
from . import views

app_name = 'carspecs'

urlpatterns = [
    path('', views.search_home, name='search_home'),
    path('search/ymm/', views.search_ymm, name='search_ymm'),
    path('search/vin/', views.search_vin, name='search_vin'),
]