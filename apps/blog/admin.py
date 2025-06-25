# apps/blog/admin.py - CORRECTED VERSION
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import BlogPost, Post, ExternalArticle

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'reading_time_display', 'word_count_display', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('word_count', 'reading_time_minutes', 'created_at', 'updated_at')  # Removed content_type
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content'),
            'description': 'Rich editorial content with full authoring capabilities'
        }),
        ('Publishing', {
            'fields': ('author', 'is_published'),
            'description': 'Author and publication status'
        }),
        ('Metrics', {
            'fields': ('word_count', 'reading_time_minutes'),
            'classes': ('collapse',),
            'description': 'Auto-calculated content metrics'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),  # Removed content_type
            'classes': ('collapse',),
            'description': 'System information'
        }),
    )
    
    actions = ['publish_posts', 'unpublish_posts', 'recalculate_metrics']
    
    def reading_time_display(self, obj):
        if obj.reading_time_minutes:
            return format_html(
                '<span style="color: #00B894; font-weight: bold;">📖 {} min</span>',
                obj.reading_time_minutes
            )
        return "—"
    reading_time_display.short_description = "Reading Time"
    reading_time_display.admin_order_field = 'reading_time_minutes'
    
    def word_count_display(self, obj):
        if obj.word_count:
            return format_html(
                '<span style="color: #8FA8B2;">📝 {} words</span>',
                obj.word_count
            )
        return "—"
    word_count_display.short_description = "Word Count"
    word_count_display.admin_order_field = 'word_count'
    
    def publish_posts(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} blog posts published successfully.")
    publish_posts.short_description = "Publish selected blog posts"
    
    def unpublish_posts(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} blog posts unpublished.")
    unpublish_posts.short_description = "Unpublish selected blog posts"
    
    def recalculate_metrics(self, request, queryset):
        updated = 0
        for post in queryset:
            post.save()  # Triggers metric recalculation
            updated += 1
        self.message_user(request, f"Recalculated metrics for {updated} blog posts.")
    recalculate_metrics.short_description = "Recalculate reading metrics"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_display', 'author_display', 'is_announcement', 'reading_time_display', 'published', 'created_at')
    list_filter = ('category', 'published', 'is_announcement', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('word_count', 'reading_time_minutes', 'content_type', 'created_at')
    date_hierarchy = 'created_at'
    list_editable = ('is_announcement', 'published')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'content'),
            'description': 'Quick content for announcements, updates, and simple posts'
        }),
        ('Publishing', {
            'fields': ('author', 'published', 'is_announcement'),
            'description': 'Publication settings and special flags'
        }),
        ('Metrics', {
            'fields': ('word_count', 'reading_time_minutes'),
            'classes': ('collapse',),
            'description': 'Auto-calculated content metrics'
        }),
        ('Metadata', {
            'fields': ('content_type', 'created_at'),
            'classes': ('collapse',),
            'description': 'System information'
        }),
    )
    
    actions = ['make_announcement', 'remove_announcement', 'publish_posts', 'unpublish_posts']
    
    def category_display(self, obj):
        colors = {
            'announcement': '#E17055',
            'update': '#00B894', 
            'news': '#FDCB6E',
            'community': '#8FA8B2',
            'tutorial': '#00B894',
            'tip': '#FDCB6E',
            'other': '#C8D5E3'
        }
        color = colors.get(obj.category, '#C8D5E3')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_display.short_description = "Category"
    category_display.admin_order_field = 'category'
    
    def author_display(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return format_html('<em style="color: #8FA8B2;">System</em>')
    author_display.short_description = "Author"
    author_display.admin_order_field = 'author'
    
    def reading_time_display(self, obj):
        if obj.reading_time_minutes:
            return format_html(
                '<span style="color: #00B894;">⚡ {} min</span>',
                obj.reading_time_minutes
            )
        return "—"
    reading_time_display.short_description = "Reading Time"
    reading_time_display.admin_order_field = 'reading_time_minutes'
    
    def make_announcement(self, request, queryset):
        count = queryset.update(is_announcement=True)
        self.message_user(request, f"{count} posts marked as announcements.")
    make_announcement.short_description = "Mark as announcement"
    
    def remove_announcement(self, request, queryset):
        count = queryset.update(is_announcement=False)
        self.message_user(request, f"{count} posts removed from announcements.")
    remove_announcement.short_description = "Remove announcement status"
    
    def publish_posts(self, request, queryset):
        count = queryset.update(published=True)
        self.message_user(request, f"{count} posts published.")
    publish_posts.short_description = "Publish selected posts"
    
    def unpublish_posts(self, request, queryset):
        count = queryset.update(published=False)
        self.message_user(request, f"{count} posts unpublished.")
    unpublish_posts.short_description = "Unpublish selected posts"

@admin.register(ExternalArticle)
class ExternalArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_display', 'complexity_display', 'reading_time_display', 'is_featured', 'published_date')
    list_filter = ('source', 'complexity_level', 'is_featured', 'fetched_date', 'published_date')
    search_fields = ('title', 'summary', 'full_content', 'source_name')
    readonly_fields = ('fetched_date', 'word_count', 'reading_time_minutes', 'content_type')
    date_hierarchy = 'published_date'
    list_editable = ('is_featured',)
    
    fieldsets = (
        ('Article Information', {
            'fields': ('source', 'source_name', 'title', 'original_url', 'published_date'),
            'description': 'Basic article information and source details'
        }),
        ('Content', {
            'fields': ('summary', 'full_content', 'content_excerpt', 'featured_image', 'tags'),
            'description': 'Article content - use full_content for complete articles, excerpt for previews'
        }),
        ('Curation', {
            'fields': ('is_featured', 'complexity_level', 'commentary'),
            'description': 'Content curation and editorial features'
        }),
        ('Metrics', {
            'fields': ('word_count', 'reading_time_minutes'),
            'classes': ('collapse',),
            'description': 'Auto-calculated content metrics'
        }),
        ('Metadata', {
            'fields': ('content_type', 'fetched_date'),
            'classes': ('collapse',),
            'description': 'System information and timestamps'
        }),
    )
    
    actions = ['make_featured', 'remove_featured', 'calculate_reading_time', 'set_complexity_beginner', 'set_complexity_advanced']
    
    def source_display(self, obj):
        colors = {
            'nasa': '#1f77b4',
            'noaa': '#ff7f0e', 
            'nature': '#2ca02c',
            'science_daily': '#d62728',
            'mit_tech': '#9467bd',
            'chemistry_world': '#8c564b',
            'arxiv': '#e377c2',
            'pubmed': '#7f7f7f',
            'other': '#17a2b8'
        }
        color = colors.get(obj.source, '#17a2b8')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">{}</span>',
            color,
            obj.source_name
        )
    source_display.short_description = "Source"
    source_display.admin_order_field = 'source'
    
    def complexity_display(self, obj):
        if not obj.complexity_level:
            return "—"
        
        colors = {
            'beginner': '#28a745',
            'intermediate': '#ffc107', 
            'advanced': '#fd7e14',
            'expert': '#dc3545'
        }
        color = colors.get(obj.complexity_level, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em;">{}</span>',
            color,
            obj.get_complexity_level_display()
        )
    complexity_display.short_description = "Complexity"
    complexity_display.admin_order_field = 'complexity_level'
    
    def reading_time_display(self, obj):
        if obj.reading_time_minutes:
            if obj.reading_time_minutes > 10:
                color = '#E17055'  # Long read
                icon = '📚'
            elif obj.reading_time_minutes > 5:
                color = '#FDCB6E'  # Medium read
                icon = '📖'
            else:
                color = '#00B894'  # Quick read
                icon = '⚡'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {} min</span>',
                color, icon, obj.reading_time_minutes
            )
        return "—"
    reading_time_display.short_description = "Reading Time"
    reading_time_display.admin_order_field = 'reading_time_minutes'
    
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} articles marked as featured.")
    make_featured.short_description = "⭐ Mark as featured"
    
    def remove_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f"{count} articles removed from featured.")
    remove_featured.short_description = "Remove featured status"
    
    def calculate_reading_time(self, request, queryset):
        updated = 0
        for article in queryset:
            article.save()  # Triggers metric recalculation
            updated += 1
        self.message_user(request, f"Recalculated reading time for {updated} articles.")
    calculate_reading_time.short_description = "🔄 Recalculate reading time"
    
    def set_complexity_beginner(self, request, queryset):
        count = queryset.update(complexity_level='beginner')
        self.message_user(request, f"{count} articles set to beginner level.")
    set_complexity_beginner.short_description = "Set complexity: Beginner"
    
    def set_complexity_advanced(self, request, queryset):
        count = queryset.update(complexity_level='advanced')
        self.message_user(request, f"{count} articles set to advanced level.")
    set_complexity_advanced.short_description = "Set complexity: Advanced"

# Admin site customization
admin.site.site_header = "GeNiUS EdTech Administration"
admin.site.site_title = "GeNiUS Admin"
admin.site.index_title = "Content Management Dashboard"
