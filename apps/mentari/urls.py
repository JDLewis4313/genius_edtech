from django.urls import path
from mentari.views.math import math_support_view, plot_expression_view
from mentari.views.advising import advising_view
from mentari.views.reflection import submit_reflection_view
from mentari.views.dashboard import dashboard_view
from mentari.views.essay import essay_feedback_view
from mentari.views.quantum import quantum_chat_view
from apps.mentari.views.chat import chat_page_view, mentari_chat_view

app_name = "mentari"

urlpatterns = [
    path("", chat_page_view, name="mentari_home"),
    path("chat/", chat_page_view, name="mentari_chat_page"),
    path("chat/api/", mentari_chat_view, name="mentari_chat"),  # ✅ API endpoint for JS fetch

    # Subject-specific views
    path("math/", math_support_view, name="math_support"),
    path("math/plot/", plot_expression_view, name="plot_expression"),
    path("advising/", advising_view, name="advising"),
    path("reflection/", submit_reflection_view, name="submit_reflection"),
    path("essay/", essay_feedback_view, name="essay_feedback"),
    path("quantum/", quantum_chat_view, name="quantum_chat"),

    # Optional: dashboard route if used
    path("dashboard/", dashboard_view, name="dashboard"),
]
