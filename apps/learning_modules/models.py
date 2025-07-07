from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class LearningPath(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'), 
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    estimated_hours = models.IntegerField()
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def get_completion_rate(self, user):
        """Calculate completion rate for a user"""
        if not user.is_authenticated:
            return 0
        
        total_modules = self.modules.count()
        if total_modules == 0:
            return 0
            
        completed = UserModuleProgress.objects.filter(
            user=user,
            module__learning_path=self,
            completed=True
        ).count()
        
        return (completed / total_modules) * 100

class LearningModule(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('text', 'Text/Reading'),
        ('simulation', 'Interactive Simulation'),
        ('quiz', 'Quiz/Assessment'),
        ('lab', 'Virtual Lab'),
        ('code', 'Coding Exercise'),
    ]
    
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField()  # JSON or HTML content
    order = models.IntegerField(default=0)
    estimated_minutes = models.IntegerField()
    learning_objectives = models.TextField()
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['learning_path', 'order']
    
    def __str__(self):
        return f"{self.learning_path.title} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('learning_modules:module_detail', kwargs={'pk': self.pk})

class UserModuleProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    time_spent_minutes = models.IntegerField(default=0)
    score = models.FloatField(null=True, blank=True)  # For assessments
    attempts = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'module']
    
    def mark_completed(self, score=None):
        from django.utils import timezone
        self.completed = True
        self.completed_at = timezone.now()
        if score is not None:
            self.score = score
        self.save()

class LearningPathEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    target_completion_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'learning_path']
    
    def get_progress_percentage(self):
        return self.learning_path.get_completion_rate(self.user)

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('completion', 'Path Completion'),
        ('streak', 'Learning Streak'),
        ('mastery', 'Subject Mastery'),
        ('speed', 'Fast Learner'),
        ('explorer', 'Explorer'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=50, default='🏆')
    requirements = models.JSONField()  # Store achievement criteria
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
