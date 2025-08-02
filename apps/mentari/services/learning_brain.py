# apps/mentari/services/learning_brain.py
import json
import logging
from datetime import datetime, timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

class LearningBrain:
    """Manages conversation context and learning progress"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.cache_key = f"mentari_context_{user_id}"
        self.context = self.load_context()

    def load_context(self):
        """Load context from cache or initialize with error handling"""
        try:
            context = cache.get(self.cache_key, {})
            if not context:
                context = self._get_default_context()
            logger.debug(f"Loaded context for user {self.user_id}")
            return context
        except Exception as e:
            logger.error(f"Failed to load context for user {self.user_id}: {e}")
            return self._get_default_context()

    def _get_default_context(self):
        """Get default context structure"""
        return {
            'conversation_history': [],
            'current_topic': None,
            'learning_style': None,
            'knowledge_gaps': [],
            'strengths': [],
            'last_active': None,
            'mood': 'neutral',
            'preferences': {
                'difficulty_level': 'medium',
                'explanation_style': 'balanced',
                'encouragement_level': 'normal'
            },
            'nl_insights': []  # NEW: For storing NL insights
        }

    def save_context(self):
        """Save context to cache with error handling"""
        try:
            # FIX: Changed selfcontext to self.context
            cache.set(self.cache_key, self.context, 86400 * 7)  # 7 days
            logger.debug(f"Saved context for user {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to save context for user {self.user_id}: {e}")

    def add_interaction(self, message, response, topic=None):
        """Add interaction to history"""
        try:
            self.context['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'message': message[:200],  # Truncate for storage
                'response': response[:200],  # Truncate for storage
                'topic': topic
            })

            # Keep only last 50 interactions
            if len(self.context['conversation_history']) > 50:
                self.context['conversation_history'] = self.context['conversation_history'][-50:]

            self.context['last_active'] = datetime.now().isoformat()
            if topic:
                self.context['current_topic'] = topic

            self.save_context()
        except Exception as e:
            logger.error(f"Failed to add interaction for user {self.user_id}: {e}")

    def get_recent_topics(self):
        """Get recently discussed topics"""
        try:
            topics = []
            # FIX: Changed self.contex to self.context
            for interaction in self.context['conversation_history'][-10:]:
                if interaction.get('topic') and interaction['topic'] not in topics:
                    topics.append(interaction['topic'])
            return topics[:5]  # Return up to 5 recent topics
        except Exception as e:
            logger.error(f"Failed to get recent topics for user {self.user_id}: {e}")
            return []

    def update_learning_style(self, style_indicator):
        """Update user's learning style based on interactions"""
        try:
            # This could be expanded with ML in the future
            if 'visual' in style_indicator:
                self.context['learning_style'] = 'visual'
            elif 'step-by-step' in style_indicator:
                self.context['learning_style'] = 'sequential'
            elif 'examples' in style_indicator:
                self.context['learning_style'] = 'practical'
            elif 'conceptual' in style_indicator:
                self.context['learning_style'] = 'conceptual'
            elif 'procedural' in style_indicator:
                self.context['learning_style'] = 'procedural'

            self.save_context()
        except Exception as e:
            logger.error(f"Failed to update learning style for user {self.user_id}: {e}")

    def add_knowledge_gap(self, topic, score=None):
        """Track areas where user needs improvement"""
        try:
            gap = {'topic': topic, 'identified': datetime.now().isoformat()}
            if score:
                gap['score'] = score

            # Remove old entries for the same topic
            self.context['knowledge_gaps'] = [g for g in self.context['knowledge_gaps'] if g['topic'] != topic]
            self.context['knowledge_gaps'].append(gap)

            # Keep only recent gaps
            if len(self.context['knowledge_gaps']) > 10:
                self.context['knowledge_gaps'] = self.context['knowledge_gaps'][-10:]

            self.save_context()
        except Exception as e:
            logger.error(f"Failed to add knowledge gap for user {self.user_id}: {e}")

    def add_strength(self, topic, score=None):
        """Track areas where user excels"""
        try:
            strength = {'topic': topic, 'identified': datetime.now().isoformat()}
            if score:
                strength['score'] = score

            # Remove old entries for the same topic
            self.context['strengths'] = [s for s in self.context['strengths'] if s['topic'] != topic]
            self.context['strengths'].append(strength)

            # Keep only recent strengths
            if len(self.context['strengths']) > 10:
                self.context['strengths'] = self.context['strengths'][-10:]

            self.save_context()
        except Exception as e:
            logger.error(f"Failed to add strength for user {self.user_id}: {e}")

    def update_mood(self, indicators):
        """Update user's learning mood based on interaction patterns"""
        try:
            if any(word in indicators.lower() for word in ['confused', 'difficult', 'help', 'struggling']):
                self.context['mood'] = 'frustrated'
            elif any(word in indicators.lower() for word in ['great', 'excellent', 'understand', 'got it']):
                self.context['mood'] = 'confident'
            elif any(word in indicators.lower() for word in ['bored', 'easy', 'simple']):
                self.context['mood'] = 'unchallenged'
            else:
                self.context['mood'] = 'neutral'

            self.save_context()
        except Exception as e:
            logger.error(f"Failed to update mood for user {self.user_id}: {e}")

    def get_personalized_greeting(self):
        """Generate a greeting based on context"""
        try:
            last_active = self.context.get('last_active')
            if last_active:
                last_time = datetime.fromisoformat(last_active)
                time_diff = datetime.now() - last_time

                if time_diff < timedelta(hours=1):
                    return "Welcome back! Ready to continue?"
                elif time_diff < timedelta(days=1):
                    return "Good to see you again!"
                elif time_diff < timedelta(days=7):
                    return "Welcome back! It's been a few days."
                else:
                    return "Welcome back! It's been a while."

            return "Welcome! I'm excited to help you learn."
        except Exception as e:
            logger.error(f"Failed to get personalized greeting for user {self.user_id}: {e}")
            return "Welcome! I'm excited to help you learn."

    def get_learning_recommendations(self):
        """Get personalized recommendations based on context"""
        try:
            recommendations = []

            # Based on knowledge gaps
            if self.context['knowledge_gaps']:
                recent_gap = self.context['knowledge_gaps'][-1]
                recommendations.append(f"Review {recent_gap['topic']}")

            # Based on strengths
            if self.context['strengths']:
                recent_strength = self.context['strengths'][-1]
                recommendations.append(f"Challenge yourself with advanced {recent_strength['topic']}")

            # Based on mood
            if self.context['mood'] == 'frustrated':
                recommendations.append("Try some easier practice problems")
            elif self.context['mood'] == 'unchallenged':
                recommendations.append("Explore more advanced topics")

            return recommendations[:3]  # Return top 3 recommendations
        except Exception as e:
            logger.error(f"Failed to get learning recommendations for user {self.user_id}: {e}")
            return []

    # NEW METHODS for NL integration:

    def update_context_with_nl(self, message, enhanced_context):
        """Update context with Natural Language insights"""
        try:
            if not enhanced_context.get('nl_available'):
                return
            
            # Extract insights from NL analysis
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            emotion = enhanced_context.get('emotion_analysis', {}).get('primary_emotion')
            entities = enhanced_context.get('entity_analysis', {}).get('entities', {})
            learning_indicators = enhanced_context.get('learning_indicators', {})
            
            # Update mood based on emotion analysis
            if emotion and emotion != 'neutral':
                self.context['mood'] = emotion
            
            # Track learning struggles
            struggle_level = learning_indicators.get('struggle_level')
            if struggle_level == 'high':
                # Add to knowledge gaps if struggling
                topic = self._extract_topic_from_entities(entities)
                if topic:
                    self.add_knowledge_gap(topic)
            
            # Update learning style based on help type needed
            help_type = learning_indicators.get('help_type_needed')
            if help_type:
                self.update_learning_style(help_type)
            
            # Store recent NL insights
            if 'nl_insights' not in self.context:
                self.context['nl_insights'] = []
            
            self.context['nl_insights'].append({
                'timestamp': datetime.now().isoformat(),
                'intent': intent,
                'emotion': emotion,
                'struggle_level': struggle_level,
                'help_type': help_type
            })
            
            # Keep only last 10 insights
            if len(self.context['nl_insights']) > 10:
                self.context['nl_insights'] = self.context['nl_insights'][-10:]
            
            self.save_context()
            
        except Exception as e:
            logger.error(f"Failed to update context with NL for user {self.user_id}: {e}")

    def _extract_topic_from_entities(self, entities):
        """Extract the main topic from NL entities"""
        if 'chemistry_topics' in entities:
            return 'Chemistry'
        elif 'math_topics' in entities:
            return 'Mathematics'
        elif entities.get('chemical_formulas'):
            return 'Chemistry'
        elif entities.get('math_expressions'):
            return 'Mathematics'
        return None