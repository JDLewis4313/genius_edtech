from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', blank=True)
    bio = models.TextField(blank=True)
    banner = models.ImageField(upload_to='banners/', default='banners/default.jpg', blank=True)
    element = models.CharField(max_length=10, blank=True)  # For fun "My Element is..." vibes
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
