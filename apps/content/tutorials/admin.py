# apps/tutorials/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import TutorialCategory, Tutorial, TutorialStep, UserTutorialProgress

@admin.register(TutorialCategory)
class TutorialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'icon', 'tutorial_count']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 50px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def tutorial_count(self, obj):
        return obj.tutorial_set.count()
    tutorial_count.short_description = 'Tutorials'

class TutorialStepInline(admin.TabularInline):
    model = TutorialStep
    extra = 1
    fields = ['order', 'title', 'content', 'code_snippet', 'hint']

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'language', 'duration_minutes', 'is_published', 'created_at']
    list_filter = ['category', 'difficulty', 'language', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TutorialStepInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'difficulty', 'duration_minutes', 'description')
        }),
        ('Code Templates', {
            'fields': ('language', 'starter_code', 'solution_code'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('technologies', 'is_published'),
        })
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make code fields use a monospace font
        if 'starter_code' in form.base_fields:
            form.base_fields['starter_code'].widget.attrs['style'] = 'font-family: monospace; width: 100%;'
            form.base_fields['starter_code'].widget.attrs['rows'] = 20
        if 'solution_code' in form.base_fields:
            form.base_fields['solution_code'].widget.attrs['style'] = 'font-family: monospace; width: 100%;'
            form.base_fields['solution_code'].widget.attrs['rows'] = 20
        return form

@admin.register(UserTutorialProgress)
class UserTutorialProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'tutorial', 'progress_percentage', 'is_completed', 'completion_date']
    list_filter = ['is_completed', 'completion_date']
    search_fields = ['user__username', 'tutorial__title']
    readonly_fields = ['completed_steps', 'current_code']
    
    def progress_percentage(self, obj):
        total_steps = obj.tutorial.steps.count()
        if total_steps == 0:
            return "0%"
        completed = len(obj.completed_steps or [])
        percentage = (completed / total_steps) * 100
        return f"{percentage:.0f}%"
    progress_percentage.short_description = 'Progress'

# Quick setup for initial categories
def create_initial_categories():
    """Run this in Django shell to create initial categories"""
    categories = [
        {
            'name': 'Chemistry',
            'slug': 'chemistry',
            'icon': 'fas fa-flask',
            'color': '#ff6b6b',
            'description': 'Learn programming through chemistry concepts'
        },
        {
            'name': 'Biology',
            'slug': 'biology',
            'icon': 'fas fa-dna',
            'color': '#4ecdc4',
            'description': 'Explore bioinformatics and biological simulations'
        },
        {
            'name': 'Physics',
            'slug': 'physics',
            'icon': 'fas fa-atom',
            'color': '#45b7d1',
            'description': 'Model physical phenomena with code'
        },
        {
            'name': 'Environmental Science',
            'slug': 'environmental',
            'icon': 'fas fa-leaf',
            'color': '#96ceb4',
            'description': 'Analyze environmental data and climate models'
        },
        {
            'name': 'Computer Science',
            'slug': 'computer-science',
            'icon': 'fas fa-laptop-code',
            'color': '#9b59b6',
            'description': 'Core programming concepts for STEM'
        }
    ]
    
    for cat_data in categories:
        TutorialCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
