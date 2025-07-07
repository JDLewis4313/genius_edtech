from django.apps import AppConfig


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    
    name = "apps.quiz"     # Full dotted path
    label = "quiz"         # Used in app_label and get_app_config()
