from django.urls import path
from .viewsets import elements_api, element_detail_api  # Temporarily until you convert to full ViewSet

urlpatterns = [
    path('elements/', elements_api, name='elements_api'),
    path('elements/<str:symbol>/', element_detail_api, name='element_detail_api'),
]
