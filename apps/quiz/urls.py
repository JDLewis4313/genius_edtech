from django.urls import path
from . import views

app_name = 'quiz'
urlpatterns = [
    path('', views.quiz, name='quiz'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('take/<int:topic_id>/', views.take_quiz, name='take_quiz'),
    path('results/<int:topic_id>/', views.quiz_results, name='quiz_results'),
    
    # API endpoints - KEEP ONLY THESE
    path('api/topics/<int:module_id>/', views.get_topics, name='get_topics'),
    path('api/questions/<int:topic_id>/', views.get_quiz_questions, name='get_quiz_questions'),
    path('submit-score/', views.submit_score, name='submit_score'),
]