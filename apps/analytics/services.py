# apps/analytics/services.py
from .models import Event
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

class AnalyticsService:
    def log_event(self, user, event_type, metadata=None):
        """Log any user event"""
        Event.objects.create(
            user=user,
            event_type=event_type,
            path='/ai/chat/',
            meta=metadata or {}
        )
    
    def get_user_analytics(self, user):
        """Get comprehensive user analytics"""
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        events = Event.objects.filter(user=user)
        recent_events = events.filter(timestamp__gte=week_ago)
        
        # Calculate metrics
        topics = []
        if events.filter(event_type='page_view', path__contains='quiz').exists():
            topics.append('Quizzes')
        if events.filter(event_type='page_view', path__contains='chemistry').exists():
            topics.append('Chemistry')
        if events.filter(event_type='page_view', path__contains='tutorial').exists():
            topics.append('Tutorials')
        
        # Learning streak
        dates = events.values_list('timestamp__date', flat=True).distinct()
        streak = self._calculate_streak(sorted(dates, reverse=True))
        
        return {
            'total_interactions': events.count(),
            'recent_interactions': recent_events.count(),
            'topics': topics[:5],
            'active_time': self._get_most_active_time(events),
            'streak': streak
        }
    
    def _calculate_streak(self, dates):
        """Calculate consecutive days streak"""
        if not dates:
            return 0
        
        streak = 1
        for i in range(1, len(dates)):
            if (dates[i-1] - dates[i]).days == 1:
                streak += 1
            else:
                break
        return streak
    
    def _get_most_active_time(self, events):
        """Find when user is most active"""
        if not events.exists():
            return "Not enough data"
        
        hour_counts = {}
        for event in events:
            hour = event.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if hour_counts:
            most_active_hour = max(hour_counts, key=hour_counts.get)
            return f"{most_active_hour}:00 - {most_active_hour + 1}:00"
        
        return "Not enough data"