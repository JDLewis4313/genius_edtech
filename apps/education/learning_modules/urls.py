from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.module_detail, name='module_detail'),
]
