# apps/blog/admin.py
from django.contrib import admin
from .models import BlogPost, Post, ExternalArticle

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ExternalArticle)
class ExternalArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'is_featured', 'commentary')
    list_filter = ('source', 'is_featured', 'fetched_date')
    search_fields = ('title', 'summary')
    list_editable = ('is_featured',)
    readonly_fields = ('fetched_date',)
    
    fieldsets = (
        ('Article Info', {
            'fields': ('source', 'source_name', 'title', 'original_url', 'published_date')
        }),
        ('Content', {
            'fields': ('summary', 'featured_image', 'tags')
        }),
        ('Curation', {
            'fields': ('is_featured', 'commentary')
        }),
        ('Metadata', {
            'fields': ('fetched_date',),
            'classes': ('collapse',)
        })
    )
