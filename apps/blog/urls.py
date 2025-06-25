# apps/blog/urls.py
from django.urls import path
from .views import (
    blog_index, 
    blog_detail, 
    create_post, 
    edit_post, 
    external_article_detail, 
    take_external_to_commons
)

app_name = 'blog'

urlpatterns = [
    path('', blog_index, name='index'),
    path('create/', create_post, name='create_post'),
    path('<slug:slug>/edit/', edit_post, name='edit_post'),
    path('<slug:slug>/', blog_detail, name='detail'),
    # External article detail using primary key.
    path('external/<int:pk>/', external_article_detail, name='external_detail'),
    # URL for sharing an external article to The Commons.
    path('external/<int:pk>/take_to_commons/', take_external_to_commons, name='take_external_to_commons'),
]
