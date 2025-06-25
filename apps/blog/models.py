# apps/blog/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

class BlogPost(models.Model):
    title = models.CharField(max_length=500)  # 🔄 Increased from 200
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = CKEditor5Field("default", config_name="default")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    # Enhanced fields for better content management
    reading_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    word_count = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def excerpt(self):
        from django.utils.html import strip_tags
        # Return the first 300 characters of plain text from the content (increased from 200)
        return strip_tags(self.content)[:300]
    
    def save(self, *args, **kwargs):
        # Auto-calculate reading metrics
        if self.content:
            from django.utils.html import strip_tags
            text = strip_tags(self.content)
            words = text.split()
            self.word_count = len(words)
            self.reading_time_minutes = max(1, len(words) // 200)  # ~200 words per minute
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class Post(models.Model):
    """Quick updates, announcements, and simple content"""
    CATEGORY_CHOICES = [
        ('announcement', 'Announcement'),
        ('update', 'Update'),
        ('news', 'News'),
        ('community', 'Community'),
        ('tutorial', 'Quick Tutorial'),
        ('tip', 'Tip'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=500)  # 🔄 Increased from 200
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Enhanced fields to match BlogPost capabilities
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='blog_posts')
    content_type = models.CharField(max_length=20, default='quick', editable=False)
    is_announcement = models.BooleanField(default=False, help_text="Featured prominently on homepage")
    reading_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    word_count = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-calculate reading metrics
        if self.content:
            words = self.content.split()
            self.word_count = len(words)
            self.reading_time_minutes = max(1, len(words) // 200)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quick Post"
        verbose_name_plural = "Quick Posts"

class ExternalArticle(models.Model):
    """Curated external science content"""
    SOURCE_CHOICES = [
        ('nasa', 'NASA'),
        ('noaa', 'NOAA'),
        ('nature', 'Nature'),
        ('science_daily', 'Science Daily'),
        ('mit_tech', 'MIT Technology Review'),
        ('chemistry_world', 'Chemistry World'),
        ('arxiv', 'arXiv'),
        ('pubmed', 'PubMed'),
        ('other', 'Other'),
    ]
    
    COMPLEXITY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    source_name = models.CharField(max_length=100)
    original_url = models.URLField(unique=True)
    title = models.CharField(max_length=600)  # 🔄 Increased from 300 for longer academic titles
    summary = models.TextField()
    
    # Enhanced content fields for longer articles
    full_content = models.TextField(blank=True, null=True, help_text="Complete article content for longer pieces")
    content_excerpt = models.TextField(blank=True, help_text="Short excerpt separate from summary")
    
    featured_image = models.URLField(blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    fetched_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    
    # Enhanced metadata for better content curation
    reading_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    word_count = models.PositiveIntegerField(null=True, blank=True)
    complexity_level = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, blank=True)
    content_type = models.CharField(max_length=20, default='external', editable=False)

    # Link to commentary/analysis – optionally connected to a BlogPost.
    commentary = models.ForeignKey(BlogPost, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name='external_articles')

    # Metadata stored as JSON.
    tags = models.JSONField(default=list, blank=True)
    
    def save(self, *args, **kwargs):
        content_to_analyze = self.full_content or self.summary
        if content_to_analyze:
            words = content_to_analyze.split()
            self.word_count = len(words)
            self.reading_time_minutes = max(1, len(words) // 200)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_date', '-fetched_date']
        verbose_name = "External Article"
        verbose_name_plural = "External Articles"
        indexes = [
            models.Index(fields=['source', 'is_featured']),
            models.Index(fields=['published_date']),
            models.Index(fields=['complexity_level']),
        ]

    def __str__(self):
        return f"{self.source_name}: {self.title}"
