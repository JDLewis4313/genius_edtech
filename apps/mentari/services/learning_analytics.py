# apps/mentari/services/learning_analytics.py
from apps.quiz.models import QuizAttempt, Topic
from apps.analytics.models import Event
from apps.tutorials.models import UserTutorialProgress
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from collections import defaultdict

class LearningAnalytics:
    """Advanced analytics for personalized learning insights"""
    
    def __init__(self, user):
        self.user = user
    
    def get_comprehensive_stats(self):
        """Get all learning statistics for a user"""
        return {
            'performance': self.get_performance_stats(),
            'activity': self.get_activity_stats(),
            'progress': self.get_progress_stats(),
            'patterns': self.get_learning_patterns(),
            'recommendations': self.get_personalized_recommendations()
        }
    
    def get_performance_stats(self):
        """Analyze quiz and assessment performance"""
        attempts = QuizAttempt.objects.filter(user=self.user)
        
        if not attempts.exists():
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'improvement_rate': 0,
                'best_topic': None,
                'weakest_topic': None
            }
        
        # Overall stats
        total = attempts.count()
        avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
        
        # Topic performance
        topic_stats = []
        for topic in Topic.objects.all():
            topic_attempts = attempts.filter(topic=topic)
            if topic_attempts.exists():
                avg = topic_attempts.aggregate(Avg('score'))['score__avg']
                count = topic_attempts.count()
                
                # Calculate improvement (compare first half to second half)
                if count >= 2:
                    first_half = topic_attempts.order_by('timestamp')[:count//2]
                    second_half = topic_attempts.order_by('timestamp')[count//2:]
                    
                    first_avg = sum(a.score for a in first_half) / len(first_half)
                    second_avg = sum(a.score for a in second_half) / len(second_half)
                    improvement = second_avg - first_avg
                else:
                    improvement = 0
                
                topic_stats.append({
                    'topic': topic.title,
                    'average': avg,
                    'attempts': count,
                    'improvement': improvement
                })
        
        # Sort by performance
        topic_stats.sort(key=lambda x: x['average'])
        
        weakest = topic_stats[0] if topic_stats else None
        best = topic_stats[-1] if topic_stats else None
        
        # Calculate overall improvement rate
        if total >= 4:
            recent = attempts.order_by('-timestamp')[:total//2]
            older = attempts.order_by('timestamp')[:total//2]
            
            recent_avg = sum(a.score for a in recent) / len(recent)
            older_avg = sum(a.score for a in older) / len(older)
            improvement_rate = recent_avg - older_avg
        else:
            improvement_rate = 0
        
        return {
            'total_quizzes': total,
            'average_score': round(avg_score, 1),
            'improvement_rate': round(improvement_rate, 1),
            'best_topic': best,
            'weakest_topic': weakest,
            'all_topics': topic_stats
        }
    
    def get_activity_stats(self):
        """Analyze user activity patterns"""
        now = datetime.now()
        
        # Get events from last 30 days
        events = Event.objects.filter(
            user=self.user,
            timestamp__gte=now - timedelta(days=30)
        )
        
        if not events.exists():
            return {
                'total_sessions': 0,
                'avg_session_length': 0,
                'most_active_time': None,
                'streak': 0,
                'last_active': None
            }
        
        # Activity by hour
        hour_activity = defaultdict(int)
        day_activity = defaultdict(int)
        
        for event in events:
            hour_activity[event.timestamp.hour] += 1
            day_activity[event.timestamp.date()] += 1
        
        # Most active time
        if hour_activity:
            peak_hour = max(hour_activity.items(), key=lambda x: x[1])[0]
            most_active_time = f"{peak_hour}:00 - {(peak_hour + 1) % 24}:00"
        else:
            most_active_time = None
        
        # Calculate streak
        dates = sorted(day_activity.keys(), reverse=True)
        streak = 0
        if dates and dates[0] >= (now.date() - timedelta(days=1)):
            streak = 1
            for i in range(1, len(dates)):
                if dates[i] == dates[i-1] - timedelta(days=1):
                    streak += 1
                else:
                    break
        
        # Session analysis
        total_sessions = len(set(event.timestamp.date() for event in events))
        
        return {
            'total_sessions': total_sessions,
            'avg_session_length': '~30 min',  # This would need session tracking
            'most_active_time': most_active_time,
            'streak': streak,
            'last_active': events.order_by('-timestamp').first().timestamp if events else None,
            'daily_activity': dict(day_activity)
        }
    
    def get_progress_stats(self):
        """Track learning progress across different areas"""
        # Tutorial progress
        tutorial_progress = UserTutorialProgress.objects.filter(
            user=self.user,
            completed=True
        ).count()
        
        # Topics mastered (>80% average)
        attempts = QuizAttempt.objects.filter(user=self.user)
        mastered_topics = []
        
        for topic in Topic.objects.all():
            topic_attempts = attempts.filter(topic=topic)
            if topic_attempts.count() >= 2:  # At least 2 attempts
                avg = topic_attempts.aggregate(Avg('score'))['score__avg']
                if avg >= 80:
                    mastered_topics.append(topic.title)
        
        # Learning velocity (topics per week)
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        recent_attempts = attempts.filter(timestamp__gte=four_weeks_ago)
        unique_topics = recent_attempts.values('topic').distinct().count()
        velocity = unique_topics / 4.0
        
        return {
            'tutorials_completed': tutorial_progress,
            'topics_mastered': mastered_topics,
            'mastery_count': len(mastered_topics),
            'learning_velocity': round(velocity, 1),
            'total_topics_attempted': attempts.values('topic').distinct().count()
        }
    
    def get_learning_patterns(self):
        """Identify learning patterns and preferences"""
        attempts = QuizAttempt.objects.filter(user=self.user)
        
        patterns = {
            'preferred_difficulty': 'medium',
            'learning_pace': 'steady',
            'consistency': 'regular',
            'improvement_areas': []
        }
        
        if not attempts.exists():
            return patterns
        
        # Analyze score distribution
        scores = [a.score for a in attempts]
        if scores:
            avg_score = sum(scores) / len(scores)
            
            if avg_score > 85:
                patterns['preferred_difficulty'] = 'challenging'
            elif avg_score < 60:
                patterns['preferred_difficulty'] = 'foundational'
        
        # Analyze pace
        if attempts.count() > 10:
            time_span = (attempts.last().timestamp - attempts.first().timestamp).days
            attempts_per_week = (attempts.count() / time_span) * 7 if time_span > 0 else 0
            
            if attempts_per_week > 10:
                patterns['learning_pace'] = 'intensive'
            elif attempts_per_week < 2:
                patterns['learning_pace'] = 'relaxed'
        
        # Identify improvement areas
        topic_performance = {}
        for topic in Topic.objects.all():
            topic_attempts = attempts.filter(topic=topic)
            if topic_attempts.exists():
                avg = topic_attempts.aggregate(Avg('score'))['score__avg']
                if avg < 70:
                    patterns['improvement_areas'].append(topic.title)
        
        return patterns
    
    def get_personalized_recommendations(self):
        """Generate personalized learning recommendations"""
        performance = self.get_performance_stats()
        activity = self.get_activity_stats()
        patterns = self.get_learning_patterns()
        
        recommendations = []
        
        # Based on weakest topics
        if performance['weakest_topic']:
            recommendations.append({
                'type': 'practice',
                'priority': 'high',
                'action': f"Practice {performance['weakest_topic']['topic']}",
                'reason': f"Your average is {performance['weakest_topic']['average']:.0f}%"
            })
        
        # Based on streak
        if activity['streak'] == 0:
            recommendations.append({
                'type': 'motivation',
                'priority': 'medium',
                'action': "Start a new learning streak today",
                'reason': "Consistency is key to mastery"
            })
        elif activity['streak'] > 7:
            recommendations.append({
                'type': 'achievement',
                'priority': 'low',
                'action': f"Keep your {activity['streak']}-day streak going!",
                'reason': "You're building great habits"
            })
        
        # Based on improvement rate
        if performance['improvement_rate'] < 0:
            recommendations.append({
                'type': 'support',
                'priority': 'high',
                'action': "Review fundamentals",
                'reason': "Let's strengthen your foundation"
            })
        elif performance['improvement_rate'] > 10:
            recommendations.append({
                'type': 'challenge',
                'priority': 'medium',
                'action': "Try advanced problems",
                'reason': "You're improving rapidly!"
            })
        
        # Based on learning patterns
        if patterns['preferred_difficulty'] == 'foundational':
            recommendations.append({
                'type': 'guidance',
                'priority': 'high',
                'action': "Start with tutorial reviews",
                'reason': "Build confidence with guided learning"
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations[:5]  # Return top 5 recommendations