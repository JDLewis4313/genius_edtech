from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('tutorials/', views.tutorials, name='tutorials'),
    path('', views.quiz, name='quiz'),
]
