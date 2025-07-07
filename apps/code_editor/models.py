from django.db import models

class CodeSnippet(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('sql', 'SQL'),
        ('html', 'HTML'),
        ('css', 'CSS'),
    ]

    # Use a string reference to avoid early app registry access
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='code_snippets',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200, default="Untitled")
    code = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.language})"
