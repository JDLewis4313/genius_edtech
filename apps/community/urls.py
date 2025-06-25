from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path('', views.board_index, name='board_index'),
    path('board/new/', views.create_board, name='create_board'),
    path('board/<slug:slug>/', views.board_detail, name='board_detail'),
    path('board/<slug:board_slug>/new/', views.create_thread, name='create_thread'),
    path('thread/<slug:slug>/', views.thread_detail, name='thread_detail'),
    path('thread/<slug:slug>/reply/', views.post_reply, name='post_reply'),
]
