# apps/mentari/services/learning_analytics.py
from apps.quiz.models import QuizAttempt, Topic
from apps.analytics.models import Event
from apps.tutorials.models import UserTutorialProgress
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class LearningAnalytics:
    """Enhanced analytics with Natural Language insights"""

    def __init__(self, user):
        self.user = user

    def get_comprehensive_stats(self):
        """Get all learning statistics enhanced with NL insights"""
        try:
            base_stats = {
                'performance': self.get_performance_stats(),
                'activity': self.get_activity_stats(),
                'progress': self.get_progress_stats(),
            }
            
            # Add NL-enhanced insights
            nl_insights = self._get_nl_insights()
            
            return {**base_stats, **nl_insights}
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive stats: {e}")
            return self.get_basic_stats()

    def get_performance_stats(self):
        """Analyze quiz and learning performance"""
        try:
            attempts = QuizAttempt.objects.filter(user=self.user)
            
            if not attempts.exists():
                return {
                    'total_quizzes': 0,
                    'average_score': 0,
                    'improvement_trend': 'no_data'
                }
            
            # Basic performance metrics
            total_quizzes = attempts.count()
            avg_score = attempts.aggregate(Avg('score'))['score__avg']
            
            # Performance trend analysis
            recent_attempts = attempts.filter(
                completed_at__gte=datetime.now() - timedelta(days=30)
            ).order_by('completed_at')
            
            if recent_attempts.count() >= 3:
                recent_scores = list(recent_attempts.values_list('score', flat=True))
                first_half = recent_scores[:len(recent_scores)//2]
                second_half = recent_scores[len(recent_scores)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg + 5:
                    trend = 'improving'
                elif second_avg < first_avg - 5:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            # Subject performance breakdown
            subject_performance = {}
            for attempt in attempts:
                topic_name = attempt.topic.title
                if topic_name not in subject_performance:
                    subject_performance[topic_name] = {'scores': [], 'count': 0}
                subject_performance[topic_name]['scores'].append(attempt.score)
                subject_performance[topic_name]['count'] += 1
            
            # Calculate averages
            for subject in subject_performance:
                scores = subject_performance[subject]['scores']
                subject_performance[subject]['average'] = sum(scores) / len(scores)
            
            return {
                'total_quizzes': total_quizzes,
                'average_score': round(avg_score, 1) if avg_score else 0,
                'improvement_trend': trend,
                'subject_performance': subject_performance,
                'recent_activity': recent_attempts.count()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {'error': 'Could not calculate performance stats'}

    def get_activity_stats(self):
        """Analyze user activity patterns"""
        try:
            # Get events from last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_events = Event.objects.filter(
                user=self.user,
                timestamp__gte=thirty_days_ago
            )
            
            if not recent_events.exists():
                return {
                    'total_interactions': 0,
                    'daily_average': 0,
                    'most_active_day': 'no_data'
                }
            
            # Daily activity breakdown
            daily_activity = defaultdict(int)
            for event in recent_events:
                day = event.timestamp.strftime('%A')
                daily_activity[day] += 1
            
            # Time-based patterns
            hourly_activity = defaultdict(int)
            for event in recent_events:
                hour = event.timestamp.hour
                hourly_activity[hour] += 1
            
            # Find peak activity time
            if hourly_activity:
                peak_hour = max(hourly_activity, key=hourly_activity.get)
                if 6 <= peak_hour < 12:
                    peak_time = 'morning'
                elif 12 <= peak_hour < 17:
                    peak_time = 'afternoon'
                elif 17 <= peak_hour < 21:
                    peak_time = 'evening'
                else:
                    peak_time = 'night'
            else:
                peak_time = 'unknown'
            
            return {
                'total_interactions': recent_events.count(),
                'daily_average': recent_events.count() / 30,
                'most_active_day': max(daily_activity, key=daily_activity.get) if daily_activity else 'no_data',
                'peak_activity_time': peak_time,
                'activity_by_day': dict(daily_activity),
                'activity_by_hour': dict(hourly_activity)
            }
            
        except Exception as e:
            logger.error(f"Failed to get activity stats: {e}")
            return {'error': 'Could not calculate activity stats'}

    def get_progress_stats(self):
        """Analyze learning progress across different areas"""
        try:
            # Quiz progress
            quiz_progress = self._analyze_quiz_progress()
            
            # Tutorial progress (if available)
            tutorial_progress = self._analyze_tutorial_progress()
            
            # Topic mastery analysis
            mastery_analysis = self._analyze_topic_mastery()
            
            return {
                'quiz_progress': quiz_progress,
                'tutorial_progress': tutorial_progress,
                'mastery_analysis': mastery_analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to get progress stats: {e}")
            return {'error': 'Could not calculate progress stats'}

    def _analyze_quiz_progress(self):
        """Analyze quiz-specific progress"""
        try:
            attempts = QuizAttempt.objects.filter(user=self.user)
            
            if not attempts.exists():
                return {'total_topics_attempted': 0, 'mastered_topics': 0}
            
            # Group by topic
            topic_attempts = defaultdict(list)
            for attempt in attempts:
                topic_attempts[attempt.topic.title].append(attempt.score)
            
            # Analyze mastery (topics with consistent high scores)
            mastered_topics = 0
            struggling_topics = []
            
            for topic, scores in topic_attempts.items():
                if len(scores) >= 2:  # Need at least 2 attempts
                    recent_scores = scores[-3:]  # Last 3 attempts
                    avg_recent = sum(recent_scores) / len(recent_scores)
                    
                    if avg_recent >= 80:
                        mastered_topics += 1
                    elif avg_recent < 60:
                        struggling_topics.append(topic)
            
            return {
                'total_topics_attempted': len(topic_attempts),
                'mastered_topics': mastered_topics,
                'struggling_topics': struggling_topics,
                'mastery_rate': (mastered_topics / len(topic_attempts)) * 100 if topic_attempts else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze quiz progress: {e}")
            return {}

    def _analyze_tutorial_progress(self):
        """Analyze tutorial completion progress"""
        try:
            # This would integrate with tutorial system
            # For now, return placeholder
            return {
                'tutorials_started': 0,
                'tutorials_completed': 0,
                'completion_rate': 0
            }
        except Exception as e:
            logger.error(f"Failed to analyze tutorial progress: {e}")
            return {}

    def _analyze_topic_mastery(self):
        """Analyze mastery across different topics"""
        try:
            attempts = QuizAttempt.objects.filter(user=self.user)
            
            if not attempts.exists():
                return {}
            
            # Calculate mastery score for each topic
            topic_mastery = {}
            
            for topic in Topic.objects.all():
                topic_attempts = attempts.filter(topic=topic)
                
                if topic_attempts.exists():
                    scores = list(topic_attempts.values_list('score', flat=True))
                    
                    # Mastery calculation: recent performance + consistency + improvement
                    recent_score = scores[-1] if scores else 0
                    avg_score = sum(scores) / len(scores)
                    consistency = 1 - (max(scores) - min(scores)) / 100 if len(scores) > 1 else 1
                    
                    # Simple improvement calculation
                    if len(scores) >= 2:
                        improvement = (scores[-1] - scores[0]) / 100
                    else:
                        improvement = 0
                    
                    # Weighted mastery score
                    mastery_score = (recent_score * 0.5 + avg_score * 0.3 + 
                                   consistency * 100 * 0.1 + improvement * 100 * 0.1)
                    
                    topic_mastery[topic.title] = {
                        'mastery_score': round(mastery_score, 1),
                        'attempts': len(scores),
                        'average_score': round(avg_score, 1),
                        'recent_score': recent_score,
                        'trend': 'improving' if improvement > 0.1 else 'stable' if improvement > -0.1 else 'declining'
                    }
            
            return topic_mastery
            
        except Exception as e:
            logger.error(f"Failed to analyze topic mastery: {e}")
            return {}

    def _get_nl_insights(self):
        """NEW: Get Natural Language derived insights"""
        try:
            # Get learning context for NL insights
            from apps.mentari.services.learning_brain import LearningBrain
            context = LearningBrain(self.user.id)
            learning_insights = context.get_learning_insights()
            
            return {
                'nl_insights': learning_insights,
                'conversation_patterns': self._analyze_conversation_patterns(context),
                'emotional_intelligence': self._analyze_emotional_patterns(context),
                'learning_style_analysis': self._analyze_learning_style(context),
                'personalized_recommendations': self._generate_smart_recommendations(context)
            }
            
        except Exception as e:
            logger.error(f"Failed to get NL insights: {e}")
            return {'nl_insights': {}}

    def _analyze_conversation_patterns(self, context):
        """Analyze conversation patterns from NL data"""
        try:
            conversation_data = context.context.get('conversation_history', [])
            
            if not conversation_data:
                return {}
            
            # Analyze intent patterns
            intent_frequency = defaultdict(int)
            emotion_frequency = defaultdict(int)
            
            for interaction in conversation_data[-20:]:  # Last 20 interactions
                intent = interaction.get('intent')
                emotion = interaction.get('emotion')
                
                if intent:
                    intent_frequency[intent] += 1
                if emotion:
                    emotion_frequency[emotion] += 1
            
            # Analyze help-seeking patterns
            help_seeking_count = sum(1 for i in conversation_data 
                                   if i.get('intent') == 'help_seeking')
            
            return {
                'dominant_intents': dict(sorted(intent_frequency.items(), 
                                              key=lambda x: x[1], reverse=True)[:3]),
                'emotional_distribution': dict(emotion_frequency),
                'help_seeking_frequency': help_seeking_count,
                'conversation_engagement': len(conversation_data),
                'avg_interactions_per_session': len(conversation_data) / max(1, len(set(
                    i.get('session_id', 'default') for i in conversation_data
                )))
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze conversation patterns: {e}")
            return {}

    def _analyze_emotional_patterns(self, context):
        """Analyze emotional patterns in learning"""
        try:
            conversation_data = context.context.get('conversation_history', [])
            
            if not conversation_data:
                return {}
            
            # Track emotional journey
            emotions_over_time = []
            stress_indicators = 0
            positive_indicators = 0
            
            for interaction in conversation_data[-10:]:  # Last 10 interactions
                emotion = interaction.get('emotion', 'neutral')
                emotions_over_time.append(emotion)
                
                if emotion in ['frustrated', 'overwhelmed', 'anxious']:
                    stress_indicators += 1
                elif emotion in ['confident', 'happy', 'excited']:
                    positive_indicators += 1
            
            # Calculate emotional wellness score
            total_emotional_data = len(emotions_over_time)
            if total_emotional_data > 0:
                wellness_score = ((positive_indicators - stress_indicators) / total_emotional_data + 1) * 50
                wellness_score = max(0, min(100, wellness_score))  # Clamp to 0-100
            else:
                wellness_score = 50  # Neutral
            
            return {
                'recent_emotions': emotions_over_time,
                'stress_level': 'high' if stress_indicators > total_emotional_data * 0.6 else 
                              'moderate' if stress_indicators > total_emotional_data * 0.3 else 'low',
                'emotional_wellness_score': round(wellness_score, 1),
                'support_needed': stress_indicators > positive_indicators,
                'emotional_trend': 'improving' if emotions_over_time and 
                                 emotions_over_time[-1] in ['confident', 'happy'] else 'needs_attention'
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze emotional patterns: {e}")
            return {}

    def _analyze_learning_style(self, context):
        """Analyze learning style preferences from conversation patterns"""
        try:
            conversation_data = context.context.get('conversation_history', [])
            
            if not conversation_data:
                return {}
            
            # Analyze learning preferences
            visual_indicators = 0
            practical_indicators = 0
            theoretical_indicators = 0
            social_indicators = 0
            
            for interaction in conversation_data:
                message = interaction.get('message', '').lower()
                
                # Visual learning indicators
                if any(word in message for word in ['show', 'see', 'graph', 'chart', 'visual', 'picture']):
                    visual_indicators += 1
                
                # Practical learning indicators
                if any(word in message for word in ['practice', 'example', 'try', 'hands-on', 'do']):
                    practical_indicators += 1
                
                # Theoretical learning indicators
                if any(word in message for word in ['explain', 'theory', 'why', 'understand', 'concept']):
                    theoretical_indicators += 1
                
                # Social learning indicators
                if any(word in message for word in ['group', 'discussion', 'community', 'forum', 'together']):
                    social_indicators += 1
            
            # Determine dominant learning style
            indicators = {
                'visual': visual_indicators,
                'practical': practical_indicators, 
                'theoretical': theoretical_indicators,
                'social': social_indicators
            }
            
            if any(indicators.values()):
                dominant_style = max(indicators, key=indicators.get)
                confidence = indicators[dominant_style] / sum(indicators.values())
            else:
                dominant_style = 'unknown'
                confidence = 0
            
            return {
                'dominant_learning_style': dominant_style,
                'confidence': round(confidence, 2),
                'style_indicators': indicators,
                'recommendations': self._get_style_recommendations(dominant_style)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze learning style: {e}")
            return {}

    def _get_style_recommendations(self, style):
        """Get recommendations based on learning style"""
        recommendations = {
            'visual': [
                'Try using the chemistry periodic table visualization',
                'Request graphs and charts when solving math problems',
                'Use color-coding for different concepts'
            ],
            'practical': [
                'Take more practice quizzes to reinforce learning',
                'Try step-by-step problem solving',
                'Focus on real-world applications'
            ],
            'theoretical': [
                'Ask for detailed explanations of concepts',
                'Explore the underlying principles',
                'Connect new learning to broader theories'
            ],
            'social': [
                'Participate in community discussions',
                'Form study groups',
                'Share your learning journey with others'
            ]
        }
        return recommendations.get(style, ['Continue exploring different learning approaches'])

    def _generate_smart_recommendations(self, context):
        """Generate personalized recommendations based on all analytics"""
        try:
            recommendations = []
            
            # Performance-based recommendations
            performance_stats = self.get_performance_stats()
            if isinstance(performance_stats, dict) and 'improvement_trend' in performance_stats:
                if performance_stats['improvement_trend'] == 'declining':
                    recommendations.append({
                        'type': 'performance',
                        'priority': 'high',
                        'message': 'Your quiz scores have been declining. Let\'s focus on reviewing challenging topics.',
                        'action': 'review_weak_areas'
                    })
                elif performance_stats['improvement_trend'] == 'improving':
                    recommendations.append({
                        'type': 'performance', 
                        'priority': 'positive',
                        'message': 'Great job! Your scores are improving. Keep up the excellent work!',
                        'action': 'continue_current_approach'
                    })
            
            # Emotional well-being recommendations
            emotional_data = self._analyze_emotional_patterns(context)
            if emotional_data.get('support_needed'):
                recommendations.append({
                    'type': 'emotional',
                    'priority': 'high',
                    'message': 'I notice you might be feeling stressed. Would you like some study tips or a break?',
                    'action': 'emotional_support'
                })
            
            # Learning style recommendations
            style_data = self._analyze_learning_style(context)
            dominant_style = style_data.get('dominant_learning_style')
            if dominant_style and dominant_style != 'unknown':
                recommendations.append({
                    'type': 'learning_style',
                    'priority': 'medium',
                    'message': f'Based on your interactions, you seem to prefer {dominant_style} learning. Here are some tailored suggestions.',
                    'action': f'optimize_for_{dominant_style}'
                })
            
            # Activity-based recommendations
            activity_stats = self.get_activity_stats()
            if isinstance(activity_stats, dict) and activity_stats.get('total_interactions', 0) < 5:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'medium', 
                    'message': 'Try exploring more features! Take a quiz, ask chemistry questions, or join community discussions.',
                    'action': 'increase_engagement'
                })
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []

    def get_basic_stats(self):
        """Fallback basic stats if enhanced analytics fail"""
        try:
            attempts = QuizAttempt.objects.filter(user=self.user)
            events = Event.objects.filter(user=self.user)
            
            return {
                'total_quizzes': attempts.count(),
                'total_interactions': events.count(),
                'average_score': attempts.aggregate(Avg('score'))['score__avg'] or 0,
                'status': 'basic_analytics_only'
            }
        except Exception as e:
            logger.error(f"Failed to get basic stats: {e}")
            return {'error': 'Analytics temporarily unavailable'}

    def handle_analytics_request(self, message, user):
        """Handle analytics requests from brain.py"""
        try:
            msg_lower = message.lower()
            
            if 'comprehensive' in msg_lower or 'detailed' in msg_lower:
                return self.get_comprehensive_stats()
            elif 'performance' in msg_lower:
                return {'performance': self.get_performance_stats()}
            elif 'activity' in msg_lower:
                return {'activity': self.get_activity_stats()}
            elif 'progress' in msg_lower:
                return {'progress': self.get_progress_stats()}
            else:
                # Default comprehensive view
                return self.get_comprehensive_stats()
                
        except Exception as e:
            logger.error(f"Failed to handle analytics request: {e}")
            return self.get_basic_stats()