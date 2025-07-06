# apps/users/services.py
from .models import Profile
from apps.quiz.models import QuizAttempt
from apps.community.models import Post
from apps.analytics.models import Event
from django.db.models import Count

class UserService:
    def get_profile(self, user):
        """Get or create user profile"""
        profile, created = Profile.objects.get_or_create(user=user)
        return profile
    
    def update_profile(self, user, data):
        """Update user profile"""
        profile = self.get_profile(user)
        
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.save()
        return profile
    
    def get_user_stats(self, user):
        """Get comprehensive user statistics"""
        if not user or not user.is_authenticated:
            return {}
        
        # Quiz stats
        quiz_attempts = QuizAttempt.objects.filter(user=user).count()
        
        # Forum stats
        forum_posts = Post.objects.filter(author=user).count()
        
        # Event stats
        total_events = Event.objects.filter(user=user).count()
        
        # Recent activity
        recent_events = Event.objects.filter(
            user=user
        ).order_by('-timestamp')[:5]
        
        return {
            'quiz_attempts': quiz_attempts,
            'forum_posts': forum_posts,
            'total_interactions': total_events,
            'recent_activity': [
                f"{e.event_type} at {e.timestamp.strftime('%Y-%m-%d %H:%M')}"
                for e in recent_events
            ]
        }
    
    def get_learning_path(self, user):
        """Get personalized learning path recommendations"""
        if not user or not user.is_authenticated:
            return []
        
        # This is a simple implementation - could be enhanced with ML
        completed_topics = QuizAttempt.objects.filter(
            user=user,
            score__gte=70
        ).values_list('topic__title', flat=True).distinct()
        
        recommendations = []
        
        if "Atoms, Ions, and Isotopes" in completed_topics:
            recommendations.append("Try 'The Periodic Table' next!")
        
        if len(completed_topics) < 3:
            recommendations.append("Complete more quizzes to unlock advanced topics.")
        
        return recommendations