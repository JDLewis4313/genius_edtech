# apps/blog/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = CKEditor5Field("default", config_name="default")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    @property
    def excerpt(self):
        from django.utils.html import strip_tags
        # Return the first 200 characters of plain text from the content.
        return strip_tags(self.content)[:200]
    
    class Meta:
        ordering = ['-created_at']

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ExternalArticle(models.Model):
    """Curated external science content"""
    SOURCE_CHOICES = [
        ('nasa', 'NASA'),
        ('noaa', 'NOAA'), 
        ('nature', 'Nature'),
        ('science_daily', 'Science Daily'),
        ('mit_tech', 'MIT Technology Review'),
        ('chemistry_world', 'Chemistry World'),
        ('other', 'Other'),
    ]
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    source_name = models.CharField(max_length=100)  # Full source name
    original_url = models.URLField(unique=True)
    title = models.CharField(max_length=300)
    summary = models.TextField()
    featured_image = models.URLField(blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    fetched_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    
    # Link to commentary/analysis – optionally connected to a BlogPost.
    commentary = models.ForeignKey(BlogPost, null=True, blank=True, 
                                 on_delete=models.SET_NULL,
                                 related_name='external_articles')
    
    # Metadata stored as JSON.
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-published_date', '-fetched_date']
    
    def __str__(self):
        return f"{self.source_name}: {self.title}"
