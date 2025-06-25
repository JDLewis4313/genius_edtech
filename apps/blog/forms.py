# apps/blog/forms.py
from django import forms
from .models import BlogPost
from django_ckeditor_5.widgets import CKEditor5Widget

class BlogPostForm(forms.ModelForm):
    # Override the content field to use a rich text editor.
    content = forms.CharField(widget=CKEditor5Widget())
    
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'content']
class ShareToCommonsForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': "Add your thoughts before sharing..."
        }),
        required=False,
        label="Your Comment"
    )