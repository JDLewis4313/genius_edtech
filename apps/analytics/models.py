from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    EVENT_CHOICES = [
        ('page_view', 'Page View'),
        ('quiz_start', 'Quiz Started'),
        ('quiz_complete', 'Quiz Completed'),
        ('tutorial_start', 'Tutorial Started'),
        ('tutorial_complete', 'Tutorial Completed'),
        ('tool_open', 'Tool Opened'),
        ('tool_use', 'Tool Used'),
        ('post_reply', 'Community Reply'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    path = models.CharField(max_length=255, blank=True)  # e.g. /tutorials/acid-base/
    meta = models.JSONField(blank=True, null=True)       # topic/module/score/formula/etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.event_type} @ {self.timestamp}"

    class Meta:
        app_label = 'analytics'  # ✅ Ensure Django knows what app this model belongs to
        ordering = ['-timestamp']
