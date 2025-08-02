# apps/code_editor/urls.py
from django.urls import path
from . import views

app_name = 'code_editor'

urlpatterns = [
    path('', views.code_editor, name='code_editor'),
    path('run/', views.run_code, name='run_code'),
    
    # Tutorial integration endpoints
    path('tutorial/<slug:slug>/<str:template_type>/', 
         views.get_tutorial_template, 
         name='get_tutorial_template'),
    path('tutorial/<slug:slug>/save-progress/', 
         views.save_tutorial_progress, 
         name='save_tutorial_progress'),
]