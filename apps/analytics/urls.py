from django.urls import path
from .views import analytics_overview

urlpatterns = [
    path('admin/overview/', analytics_overview, name='analytics_overview'),
]
