from django.contrib import admin
from .models import (
    LearningPath, LearningModule, UserModuleProgress, 
    LearningPathEnrollment, Achievement, UserAchievement
)

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'estimated_hours', 'is_active']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['title', 'description']

@admin.register(LearningModule)
class LearningModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'learning_path', 'content_type', 'order', 'estimated_minutes']
    list_filter = ['content_type', 'learning_path', 'is_required']
    search_fields = ['title', 'description']
    ordering = ['learning_path', 'order']

@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'completed', 'score', 'attempts']
    list_filter = ['completed', 'module__content_type']
    search_fields = ['user__username', 'module__title']

@admin.register(LearningPathEnrollment)
class LearningPathEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_path', 'enrolled_at', 'completed']
    list_filter = ['completed', 'learning_path']
    search_fields = ['user__username', 'learning_path__title']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_type', 'points', 'is_active']
    list_filter = ['achievement_type', 'is_active']

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['achievement', 'earned_at']
    search_fields = ['user__username', 'achievement__name']
