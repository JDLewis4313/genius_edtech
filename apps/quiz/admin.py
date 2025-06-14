from django.contrib import admin
from .models import Module, Topic, Question, Choice, UserProgress

class ChoiceInline(admin.TabularInline):
    """
    Allows inline editing of Choices within a Question.
    """
    model = Choice
    extra = 2

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'difficulty', 'question_type')
    list_filter = ('difficulty', 'question_type', 'topic')
    inlines = [ChoiceInline]
    search_fields = ('text',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module',)
    ordering = ('module', 'order')
    search_fields = ('title',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)
    search_fields = ('title',)

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'topic', 'completed', 'score', 'last_activity')
    list_filter = ('module', 'completed')
    search_fields = ('user__username',)