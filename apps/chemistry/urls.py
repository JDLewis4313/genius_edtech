from django.urls import path
from . import views

app_name = 'chemistry'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('calculator/', views.calculator, name='calculator'),
    path('molecular-viewer/', views.molecular_viewer, name='molecular_viewer'),
    path('periodic-table/', views.periodic_table, name='periodic_table'),
    path('element/<int:atomic_number>/', views.element_detail, name='element_detail'),
    path('ajax/calculate-molar-mass/', views.calculate_molar_mass, name='ajax_calculate_molar_mass'), 
]
# API endpoints
from .api_views import elements_api, element_detail_api

urlpatterns += [
    path('api/elements/', elements_api, name='elements_api'),
    path('api/elements/<str:symbol>/', element_detail_api, name='element_detail_api'),
]
