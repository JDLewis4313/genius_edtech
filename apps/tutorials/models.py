# apps/tutorials/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

class TutorialCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50)  # FontAwesome class
    color = models.CharField(max_length=7)  # Hex color
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Tutorial Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Tutorial(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('sql', 'SQL'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(TutorialCategory, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.IntegerField()
    description = models.TextField()
    learning_objectives = models.JSONField(default=list, help_text="Learning objectives for this tutorial")  # ADDED FIELD
    technologies = models.JSONField(default=list)  # ["Python", "NumPy", etc.]

    # Code templates that can be loaded in the editor
    starter_code = models.TextField(help_text="Initial code template for students")
    solution_code = models.TextField(help_text="Complete solution code")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['category', 'difficulty', 'title']

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

    def get_difficulty_color(self):
        colors = {
            'beginner': 'success',
            'intermediate': 'warning',
            'advanced': 'danger'
        }
        return colors.get(self.difficulty, 'secondary')

class TutorialStep(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Markdown content explaining the step")
    code_snippet = models.TextField(blank=True, help_text="Example code for this step")
    hint = models.TextField(blank=True, help_text="Hint to help students if they get stuck")

    class Meta:
        ordering = ['order']
        unique_together = ['tutorial', 'order']

    def __str__(self):
        return f"{self.tutorial.title} - Step {self.order}: {self.title}"

class UserTutorialProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    # Track completed steps
    completed_steps = models.JSONField(default=list)

    # Store the user's current code
    current_code = models.TextField(blank=True)

    # Completion tracking
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    # Performance metrics
    execution_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'tutorial']
        verbose_name_plural = "User Tutorial Progress"

    def __str__(self):
        return f"{self.user.username} - {self.tutorial.title}"

    def mark_completed(self):
        """Mark the tutorial as completed"""
        self.is_completed = True
        self.completion_date = timezone.now()
        self.save()

    def get_progress_percentage(self):
        """Calculate progress percentage based on completed steps"""
        total_steps = self.tutorial.steps.count()
        if total_steps == 0:
            return 0
        completed = len(self.completed_steps or [])
        return int((completed / total_steps) * 100)
