from django.urls import path

from . import views

app_name = 'bmc'
urlpatterns = [
    path('search/', views.search, name='search'),
    path('search/afterselect/', views.afterselect, name='afterselect'),
    path('search/result/', views.result, name='result')
]
