from django.urls import path

from . import views

app_name = 'bmc'
urlpatterns = [
    path('search/', views.search, name='search'),
    path('search/afterselect/', views.after_select, name='afterselect'),
    path('search/result/', views.result, name='result'),
    path('search/save/', views.save, name='save'),
    path('search/download/', views.download_pdf, name='download'),
    path('search/static/', views.static_result, name='static')
]
