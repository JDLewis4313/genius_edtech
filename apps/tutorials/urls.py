# apps/tutorials/urls.py
from django.urls import path
from . import views

app_name = 'tutorials'

urlpatterns = [
    # Tutorial list and filtering
    path('', views.tutorial_list, name='tutorial_list'),
    path('category/<slug:category_slug>/', views.tutorial_list, name='tutorial_category'),
    
    # Tutorial detail
    path('tutorial/<slug:slug>/', views.tutorial_detail, name='tutorial_detail'),
    
    # User progress
    path('my-tutorials/', views.my_tutorials, name='my_tutorials'),
    path('tutorial/<slug:slug>/step/<int:step_id>/complete/', 
         views.mark_step_complete, name='mark_step_complete'),
    
    # API endpoints
    path('api/search/', views.tutorial_search_api, name='tutorial_search_api'),
    path('api/get-template/<slug:slug>/<str:template_type>/', 
         views.get_tutorial_template, name='get_tutorial_template'),
    path('api/save-progress/<slug:slug>/', 
         views.save_tutorial_progress, name='save_tutorial_progress'),
]