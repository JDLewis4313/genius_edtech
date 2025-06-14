from django.contrib import admin
from .models import Module, Topic, Question, Choice, UserProgress

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'difficulty', 'question_type')
    list_filter = ('difficulty', 'question_type', 'topic')
    inlines = [ChoiceInline]

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module',)
    ordering = ('module', 'order')

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'topic', 'completed', 'score', 'last_activity')
    list_filter = ('module', 'completed')

admin.site.register(Module, ModuleAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(UserProgress, UserProgressAdmin)