from django.urls import path
from . import views

app_name = 'chemistry'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('calculator/', views.calculator, name='calculator'),
    path('molecular-viewer/', views.molecular_viewer, name='molecular_viewer'),
    path('periodic-table/', views.periodic_table, name='periodic_table'),
]

