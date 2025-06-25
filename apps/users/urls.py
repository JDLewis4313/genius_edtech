from django.urls import path
from . import views
from .views import login_view, register_view, logout_view, profile_view, edit_profile_view

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),

]