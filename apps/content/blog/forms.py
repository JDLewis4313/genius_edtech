# apps/blog/forms.py
from django import forms
from .models import BlogPost, Post
from django_ckeditor_5.widgets import CKEditor5Widget

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget())

    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'content']

class QuickPostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 6,
        'placeholder': "Write your quick post content..."
    }))

    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'is_announcement']

class ShareToCommonsForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': "Add your thoughts before sharing..."
        }),
        required=False,
        label="Your Comment"
    )
