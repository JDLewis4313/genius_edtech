from django.db import models
from django.contrib.auth.models import User

class Module(models.Model):
    """Learning module containing multiple topics"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # <-- add this slug!
    description = models.TextField()
    order = models.IntegerField(default=1)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']

class Topic(models.Model):
    """Topic within a module containing questions"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=1)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['module', 'order']

class Question(models.Model):
    """Quiz question"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    """Multiple choice option for a question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

class UserProgress(models.Model):
    """Track user progress through modules and topics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'topic']