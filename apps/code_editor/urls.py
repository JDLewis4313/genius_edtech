from django.urls import path
from . import views

app_name = "code_editor"

urlpatterns = [
    path('', views.code_editor, name='code_editor'),
]