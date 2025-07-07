from django.urls import path
from apps.mentari.views.math import math_support_view, plot_expression_view
from apps.mentari.views.reflection import submit_reflection_view
from apps.mentari.views.dashboard import dashboard_view
from apps.mentari.views.chat import chat_page_view, mentari_chat_view
from apps.mentari.views.emotion import emotion_support_view
from apps.mentari.views.advising import advising_view
from apps.mentari.views.essay import essay_feedback_view

app_name = "mentari"

urlpatterns = [
    path("", chat_page_view, name="mentari_home"),
    path("chat/", chat_page_view, name="mentari_chat_page"),
    path("chat/api/", mentari_chat_view, name="mentari_chat"),

    # Enhanced features
    path("math/", math_support_view, name="math_support"),
    path("math/plot/", plot_expression_view, name="plot_expression"),
    path("emotion/", emotion_support_view, name="emotion_support"),
    path("advising/", advising_view, name="advising"),
    path("essay/", essay_feedback_view, name="essay_feedback"),
    path("reflection/", submit_reflection_view, name="submit_reflection"),
    path("dashboard/", dashboard_view, name="dashboard"),
]
