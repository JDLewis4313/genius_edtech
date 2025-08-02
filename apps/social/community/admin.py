# apps/community/admin.py
from django.contrib import admin
from .models import Board, Thread, Post

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Thread) 
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'author', 'linked_post')
    list_filter = ('board', 'linked_post')
    search_fields = ('title',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')
    list_filter = ('created_at',)