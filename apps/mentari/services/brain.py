# apps/mentari/services/brain.py

import re
import random
import logging
from datetime import datetime, timedelta

from sympy import symbols, Eq, solve, simplify, integrate, diff
from sympy.parsing.sympy_parser import parse_expr
from django.db.models import Avg

from apps.mentari.services.learning_brain import LearningBrain
from apps.mentari.services.nl_enhancer import get_nl_enhancer

logger = logging.getLogger(__name__)

class MentariBrain:
    def __init__(self):
        self.user = None
        self.session = None
        self.context = None
        self.nl_enhancer = None  # Lazy load

    def respond(self, message, user=None, session=None):
        """
        Main entry point for handling user messages.
        Enhanced with Natural Language Understanding.
        """
        self.user = user
        self.session = session

        # Initialize learning context for authenticated users
        if user and user.is_authenticated:
            self.context = LearningBrain(user.id)

        # NEW: Natural Language Enhancement with error handling
        try:
            enhanced_context = self._enhance_with_nl(message, user, session)
        except Exception as e:
            logger.warning(f"NL enhancement failed, using fallback: {e}")
            enhanced_context = {
                'original_message': message,
                'nl_available': False,
                'fallback_mode': True,
                'intent_analysis': {'primary_intent': 'general_inquiry'},
                'emotion_analysis': {'primary_emotion': 'neutral'}
            }

        original = message.strip()
        msg = original.lower()

        try:
            # 1. Greeting (enhanced with emotion)
            if self.is_greeting(msg, enhanced_context):
                return self._format_response(self.handle_greeting(enhanced_context))

            # 2. Learning progress query (enhanced with intent confidence)
            if self._is_progress_query(msg, enhanced_context):
                return self._format_response(self.provide_learning_guidance(enhanced_context))

            # 3. General encouragement request (enhanced with emotion detection)
            if self._needs_encouragement(msg, enhanced_context):
                return self._format_response(self.provide_encouragement(msg, enhanced_context))

            # 4. Arithmetic (enhanced with entity extraction)
            if self.is_arithmetic(msg, enhanced_context):
                return self._format_response(self.evaluate_arithmetic(msg, enhanced_context))

            # 5. Symbolic math (enhanced with entity recognition)
            if self.is_symbolic_math(msg, enhanced_context):
                return self._format_response(self.evaluate_symbolic_math(original, enhanced_context))

            # 6. Active quiz session (enhanced with intent understanding)
            if self.session and self.session.get("quiz_active") and not self.session.get("quiz_paused"):
                if self.is_quiz_answer(msg, original, enhanced_context):
                    from apps.mentari.services.quiz import handle_quiz_answer
                    result = handle_quiz_answer(original, user, session)
                    return self._format_response(result)

            # 7. Quiz management (enhanced)
            if self.session and (self.session.get("quiz_active") or self.session.get("quiz_paused")):
                if self._is_quiz_management(msg, enhanced_context):
                    return self.handle_quiz_management(msg, enhanced_context)

            # 8. Chemistry calculations (enhanced with entity extraction)
            if self._is_chemistry_request(msg, enhanced_context):
                from apps.mentari.services.chemistry import handle_chemistry_request
                result = handle_chemistry_request(original, user)
                return self._format_response(result)

            # 9. Community (enhanced with intent understanding)
            if self._is_community_request(msg, enhanced_context):
                return self.handle_community(original, enhanced_context)

            # 10. Quiz requests (enhanced with intent classification)
            if self._is_quiz_request(msg, enhanced_context):
                from apps.mentari.services.quiz import handle_quiz_request
                result = handle_quiz_request(original, user, session)
                return self._format_response(result)

            # 11. Reflection / journaling (enhanced with emotion detection)
            if self._is_reflection_request(msg, enhanced_context):
                return self._format_response(self.handle_reflection(original, user, enhanced_context))

            # 12. Blog / articles
            if any(k in msg for k in ["blog", "article", "news", "read"]):
                from apps.mentari.services.blog import handle_blog_request
                result = handle_blog_request(original, user)
                return self._format_response(result)

            # 13. Analytics / tracking
            if any(k in msg for k in ["log", "track", "stats"]):
                result = self.handle_analytics(original, user)
                return self._format_response(result)

            # 14. Fallback help (enhanced with better suggestions)
            return self._format_response(self.get_help_message(enhanced_context))

        except Exception as e:
            logger.error(f"MentariBrain error: {e}")
            error_message = {
                "text": (
                    f"<div class='alert alert-danger'>"
                    f"I encountered an error: {str(e)}<br>"
                    f"<small>Please try rephrasing your question or contact support if this persists.</small>"
                    "</div>"
                )
            }
            return self._format_response(error_message)

    def _enhance_with_nl(self, message, user, session):
        """NEW: Add Natural Language understanding to message"""
        try:
            if not self.nl_enhancer:
                self.nl_enhancer = get_nl_enhancer()
            
            # Build user context for NL enhancement
            user_context = {}
            if user and user.is_authenticated:
                user_context['user_id'] = user.id
                user_context['username'] = user.username
                
            if session:
                user_context['session_data'] = {
                    'quiz_active': session.get('quiz_active', False),
                    'quiz_paused': session.get('quiz_paused', False)
                }
            
            if self.context:
                # FIX: Use proper method call instead of getattr
                recent_topics = self.context.get_recent_topics()
                user_context['recent_topics'] = recent_topics
            
            # Get NL enhancement
            enhanced_context = self.nl_enhancer.enhance_message(message, user_context)
            
            # Update learning context with NL insights
            if self.context and enhanced_context.get('nl_available'):
                self.context.update_context_with_nl(message, enhanced_context)
            
            return enhanced_context
            
        except Exception as e:
            logger.warning(f"NL enhancement failed: {e}")
            # Graceful fallback
            return {
                'original_message': message,
                'nl_available': False,
                'fallback_mode': True,
                'intent_analysis': {'primary_intent': 'general_inquiry'},
                'emotion_analysis': {'primary_emotion': 'neutral'}
            }

    def _format_response(self, response):
        """Enhanced response formatting with NL insights"""
        if isinstance(response, dict):
            formatted_response = response
        elif isinstance(response, str):
            formatted_response = {"text": response}
        else:
            formatted_response = {"text": str(response)}
        
        # Add quiz status if applicable
        if self.session:
            if self.session.get("quiz_active") and not self.session.get("quiz_paused"):
                formatted_response["quiz_status"] = "active"
            elif self.session.get("quiz_paused"):
                formatted_response["quiz_status"] = "paused"
        
        return formatted_response

    # Enhanced condition checking methods

    def _is_progress_query(self, msg, enhanced_context):
        """Enhanced progress query detection"""
        # Original logic
        basic_check = any(phrase in msg for phrase in 
                         ["how am i doing", "my progress", "what should i learn", "my stats"])
        
        # NL enhancement
        if enhanced_context.get('nl_available'):
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            if intent == 'progress_inquiry':
                return True
        
        return basic_check

    def _needs_encouragement(self, msg, enhanced_context):
        """Enhanced encouragement detection"""
        # Original logic
        basic_check = any(phrase in msg for phrase in 
                         ["don't understand", "confused", "help me", "struggling", "difficult"])
        
        # NL enhancement
        if enhanced_context.get('nl_available'):
            emotion = enhanced_context.get('emotion_analysis', {}).get('primary_emotion')
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            
            if emotion in ['frustrated', 'confused', 'overwhelmed'] or intent == 'encouragement_needed':
                return True
        
        return basic_check

    def _is_chemistry_request(self, msg, enhanced_context):
        """Enhanced chemistry request detection"""
        # Original logic
        chemistry_calc_keywords = [
            "molar mass", "calculate molar", "molecular weight",
            "element info", "atomic number", "compound analysis",
            "tell me about", "analyze the molecule", "chemistry", 
            "element", "periodic table", "molecule", "compound"
        ]
        basic_check = any(k in msg for k in chemistry_calc_keywords)
        
        # NL enhancement
        if enhanced_context.get('nl_available'):
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            entities = enhanced_context.get('entity_analysis', {}).get('entities', {})
            
            if (intent == 'chemistry_help' or 
                'chemistry_topics' in entities or 
                'chemical_formulas' in entities):
                return True
        
        return basic_check

    def _is_quiz_request(self, msg, enhanced_context):
        """Enhanced quiz request detection"""
        # Original logic
        quiz_triggers = [
            "quiz on atoms", "quiz on molecules", "quiz on periodic",
            "atoms quiz", "molecules quiz", "periodic quiz",
            "take chemistry quiz", "start chemistry quiz", "chemistry test",
            "start a new quiz", "start quiz", "take a quiz"
        ]
        basic_check = any(phrase in msg for phrase in quiz_triggers) or msg.startswith("quiz on")
        
        # NL enhancement
        if enhanced_context.get('nl_available'):
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            if intent == 'quiz_request':
                return True
        
        return basic_check

    def _is_community_request(self, msg, enhanced_context):
        """Enhanced community request detection"""
        basic_check = any(k in msg for k in ["forum", "thread", "discussion", "community", "recent threads"])
        
        # NL enhancement could add intent detection here
        return basic_check

    def _is_reflection_request(self, msg, enhanced_context):
        """Enhanced reflection request detection"""
        basic_check = any(k in msg for k in ["reflect", "journal", "feeling", "thinking about", "recent reflections", "my reflections"])
        
        # NL enhancement
        if enhanced_context.get('nl_available'):
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            if intent == 'reflection':
                return True
        
        return basic_check

    def _is_quiz_management(self, msg, enhanced_context):
        """Enhanced quiz management detection"""
        return any(phrase in msg for phrase in ['pause quiz', 'stop quiz', 'end quiz', 'quit quiz', 'exit quiz', 'resume quiz'])

    # Enhanced existing methods

    def is_greeting(self, msg, enhanced_context=None):
        """Enhanced greeting detection"""
        basic_greeting = any(g in msg for g in [
            "hello", "hi", "hey", "good morning",
            "good afternoon", "good evening", "greetings"
        ])
        
        # NL enhancement
        if enhanced_context and enhanced_context.get('nl_available'):
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            if intent == 'greeting':
                return True
        
        return basic_greeting

    def is_arithmetic(self, msg, enhanced_context=None):
        """Enhanced arithmetic detection"""
        basic_check = re.fullmatch(r"[0-9\s\+\-\*\/\.\(\)]+", msg) is not None
        
        # NL enhancement - check for numbers in entities
        if enhanced_context and enhanced_context.get('nl_available'):
            entities = enhanced_context.get('entity_analysis', {}).get('entities', {})
            if 'numbers' in entities and len(entities['numbers']) >= 2:
                return True
        
        return basic_check

    def is_symbolic_math(self, msg, enhanced_context=None):
        """Enhanced symbolic math detection"""
        basic_check = any(k in msg for k in [
            "solve", "simplify", "integrate", "differentiate", "diff", "derivative"
        ])
        
        # NL enhancement
        if enhanced_context and enhanced_context.get('nl_available'):
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            entities = enhanced_context.get('entity_analysis', {}).get('entities', {})
            
            if intent == 'math_help' and 'math_expressions' in entities:
                return True
        
        return basic_check

    def is_quiz_answer(self, msg, original, enhanced_context=None):
        """Enhanced quiz answer detection"""
        # Direct letter answers
        if msg in ['a', 'b', 'c', 'd']:
            return True
        
        # Answer format detection
        if any(phrase in msg for phrase in ['answer:', 'answer is', 'my answer']):
            return True
        
        # Single letter check
        if len(original.strip()) == 1 and original.strip().upper() in ['A', 'B', 'C', 'D']:
            return True
        
        return False

    def handle_greeting(self, enhanced_context=None):
        """Enhanced greeting with emotion awareness"""
        # Detect user emotion for personalized greeting
        emotion = 'neutral'
        if enhanced_context and enhanced_context.get('nl_available'):
            emotion = enhanced_context.get('emotion_analysis', {}).get('primary_emotion', 'neutral')

        if not self.user or not self.user.is_authenticated:
            greeting_text = self._get_anonymous_greeting(emotion)
        else:
            greeting_text = self._get_personalized_greeting(emotion)

        return greeting_text

    def _get_anonymous_greeting(self, emotion):
        """Get greeting for anonymous users"""
        base_greeting = (
            "<div class='alert alert-info'>"
            "<strong>Hello!</strong> I'm Mentari, your personal learning companion. 🌟<br>"
        )
        
        # Add emotion-aware message
        if emotion == 'frustrated':
            base_greeting += "I can sense you might be having a tough time. Don't worry - I'm here to help make learning easier!<br><br>"
        elif emotion == 'excited':
            base_greeting += "I love your enthusiasm for learning! Let's explore something amazing together!<br><br>"
        elif emotion == 'confused':
            base_greeting += "Questions are the beginning of wisdom! I'm here to help clarify anything you need.<br><br>"
        else:
            base_greeting += "I'm here to help you learn and grow!<br><br>"
        
        base_greeting += (
            "I can help you with:<br>"
            "• 📐 Math problems & equations<br>"
            "• 🧪 Chemistry calculations & concepts<br>"
            "• 📝 Interactive quizzes<br>"
            "• 💻 Code examples & explanations<br>"
            "• 📚 Finding tutorials<br>"
            "• 💬 Community discussions<br>"
            "• 📊 Tracking your learning progress<br>"
            "• 💭 Personal reflections<br>"
            '<em>Try saying "Molar mass of H2O" or "Quiz on atoms"</em>'
            "</div>"
        )
        
        return {
            "text": base_greeting,
            "card": {
                "type": "help",
                "suggestions": [
                    "Start a quiz",
                    "Molar mass of H2O", 
                    "Solve x^2 - 4 = 0",
                    "Show recent threads",
                    "How am I doing?"
                ]
            }
        }

    def _get_personalized_greeting(self, emotion):
        """Get personalized greeting for authenticated users"""
        now = datetime.now()
        hour = now.hour
        if hour < 12:
            salutation = "Good morning"
        elif hour < 17:
            salutation = "Good afternoon"
        else:
            salutation = "Good evening"

        user_name = self.user.username
        
        # Emotion-aware personalized message
        if emotion == 'frustrated':
            message = f"I can tell you might be feeling a bit frustrated today. Remember, every expert was once a beginner! What can I help you work through?"
        elif emotion == 'excited':
            message = f"Your excitement for learning is wonderful! What would you like to explore today?"
        elif emotion == 'confused':
            message = f"I'm here to help clear up any confusion. What topic would you like me to explain?"
        else:
            message = "What would you like to explore today?"
        
        return {
            "text": (
                f"<div class='alert alert-info'>"
                f"<strong>{salutation}, {user_name}!</strong><br>"
                f"{message}"
                "</div>"
            ),
            "card": {
                "type": "help",
                "suggestions": [
                    "My progress",
                    "Start a quiz", 
                    "Show recent threads",
                    "Chemistry help"
                ]
            }
        }

    def provide_encouragement(self, msg, enhanced_context=None):
        """Enhanced encouragement with emotion awareness"""
        topic = self.extract_topic_from_message(msg)
        
        # Get emotion and struggle level from NL analysis
        emotion = 'neutral'
        struggle_level = 'medium'
        
        if enhanced_context and enhanced_context.get('nl_available'):
            emotion = enhanced_context.get('emotion_analysis', {}).get('primary_emotion', 'neutral')
            struggle_level = enhanced_context.get('learning_indicators', {}).get('struggle_level', 'medium')
        
        # Personalized encouragement based on emotion and struggle level
        if struggle_level == 'high':
            if emotion == 'frustrated':
                messages = [
                    f"I can feel your frustration with {topic}, and that's completely valid. Let's take this one small step at a time. 💙",
                    f"Feeling stuck with {topic}? That means you're pushing your boundaries - that's where real growth happens! 🌱",
                    f"I know {topic} feels overwhelming right now. Would it help if we broke it down into smaller, more manageable pieces? 🧩"
                ]
            else:
                messages = [
                    f"I know {topic} can feel really challenging. Remember, you don't have to master everything at once! 💪",
                    f"Every expert in {topic} was once exactly where you are now. You're on the right path! 🌟",
                    f"Struggling with {topic} shows you're tackling something important. Let's work through this together! 🤝"
                ]
        elif emotion == 'confused':
            messages = [
                f"Confusion is just your brain making room for new understanding in {topic}! 🧠✨",
                f"Questions about {topic} mean you're thinking critically. That's exactly what good learners do! 🎯",
                f"Let's untangle {topic} together. Sometimes a fresh perspective makes all the difference! 🔍"
            ]
        else:
            # Default encouraging messages
            messages = [
                f"I know {topic} can feel tricky—you're doing great! 💪",
                f"Let's break down {topic} step by step.",
                f"Don't worry, {topic} clicks for everyone at their own pace."
            ]
        
        selected_message = random.choice(messages)
        
        return (
            "<div class='alert alert-warning'>"
            + selected_message +
            "</div>"
        )

    def provide_learning_guidance(self, enhanced_context=None):
        """Enhanced learning guidance with NL insights"""
        from apps.quiz.models import QuizAttempt, Topic
        from apps.analytics.models import Event

        if not self.user or not self.user.is_authenticated:
            return "<div class='alert alert-warning'>Please log in to view your progress.</div>"

        # Get basic stats
        attempts = QuizAttempt.objects.filter(user=self.user)
        stats = []
        if attempts.exists():
            total = attempts.count()
            avg = attempts.aggregate(Avg("score"))["score__avg"]
            stats.append(f"• Total quizzes: {total}")
            stats.append(f"• Average score: {avg:.1f}%")

        try:
            recent = Event.objects.filter(
                user=self.user,
                timestamp__gte=datetime.now() - timedelta(days=7)
            )
            if recent.exists():
                stats.append(f"• Interactions last 7d: {recent.count()}")
        except:
            pass

        # Add NL-derived insights
        if enhanced_context and enhanced_context.get('nl_available'):
            emotion = enhanced_context.get('emotion_analysis', {}).get('primary_emotion')
            if emotion:
                stats.append(f"• Current mood: {emotion.title()}")

        body = "<br>".join(stats) or "No activity yet."
        
        return {
            "text": (
                "<div class='alert alert-info'>"
                f"<strong>📊 Your Learning Progress</strong><br>{body}"
                "</div>"
            ),
            "card": {
                "type": "progress",
                "stats": stats
            }
        }

    def handle_reflection(self, message, user, enhanced_context=None):
        """Enhanced reflection with emotion awareness"""
        from apps.mentari.services.reflection import ReflectionService
        
        reflection_service = ReflectionService(user=user, session=self.session)
        
        # FIX: Pass NL insights through parameters instead of non-existent method
        msg_lower = message.lower()
        
        if any(phrase in msg_lower for phrase in ["recent reflections", "my reflections", "show reflections"]):
            return self.show_recent_reflections(reflection_service)
        elif any(phrase in msg_lower for phrase in ["reflection prompt", "what to reflect on", "reflection help"]):
            # Pass enhanced context if available
            if enhanced_context:
                return reflection_service.get_reflection_prompt(enhanced_context)
            else:
                return reflection_service.get_reflection_prompt()
        else:
            # Pass enhanced context to handle reflection
            if enhanced_context:
                return reflection_service.handle_reflection_request(message, enhanced_context)
            else:
                return reflection_service.handle_reflection_request(message)

    def handle_community(self, message, enhanced_context=None):
        """Enhanced community handling"""
        try:
            msg_lower = message.lower()
            
            if "recent" in msg_lower and "thread" in msg_lower:
                return self._get_recent_threads()
            elif "popular" in msg_lower:
                return self._get_popular_threads()
            elif "boards" in msg_lower:
                return self._get_boards()
            else:
                return {
                    "text": (
                        "<div class='alert alert-info'>"
                        "Visit The Commons to join discussions! 💬<br>"
                        "• View recent threads<br>"
                        "• Join popular discussions<br>"
                        "• Explore topic boards"
                        "</div>"
                    ),
                    "card": {
                        "type": "community_help",
                        "actions": [
                            {"text": "Recent Threads", "action": "show recent threads"},
                            {"text": "Popular Discussions", "action": "show popular threads"},
                            {"text": "Visit Community", "url": "/community/"}
                        ]
                    }
                }
                
        except Exception as e:
            return {
                "text": (
                    f"<div class='alert alert-warning'>"
                    f"Could not load community data: {str(e)}<br>"
                    f"<a href='/community/' class='btn btn-sm btn-primary mt-2'>Visit Community Directly</a>"
                    "</div>"
                )
            }

    def get_help_message(self, enhanced_context=None):
        """Enhanced help message with personalized suggestions"""
        # Analyze user's likely interests from NL context
        suggestions = ["Start a quiz", "Molar mass of H2O", "Show recent threads", "How am I doing?", "Solve x^2 - 4 = 0"]
        
        if enhanced_context and enhanced_context.get('nl_available'):
            entities = enhanced_context.get('entity_analysis', {}).get('entities', {})
            intent = enhanced_context.get('intent_analysis', {}).get('primary_intent')
            
            # Customize suggestions based on detected interests
            if 'chemistry_topics' in entities or intent == 'chemistry_help':
                suggestions = ["Element Carbon", "Molar mass of H2O", "Quiz on atoms", "Periodic table", "Show recent threads"]
            elif 'math_topics' in entities or intent == 'math_help':
                suggestions = ["Solve x^2 - 4 = 0", "Integrate x^2", "Factor x^2 - 9", "Derivative of sin(x)", "Math help"]
            elif intent == 'quiz_request':
                suggestions = ["Start a quiz", "Quiz on chemistry", "Quiz on math", "How am I doing?", "My progress"]
        
        return {
            "text": (
                "<div class='alert alert-info'>"
                "<strong>🌟 I'm Mentari, your personal learning AI!</strong><br><br>"
                "I adapt to your style and help you master:<br>"
                "• 📐 Math (arithmetic, algebra, calculus)<br>"
                "• 🧪 Chemistry (elements, formulas)<br>"
                "• 💻 Code (examples & execution)<br>"
                "• 📝 Quizzes (adaptive, 5-question limit)<br>"
                "• 📚 Tutorials<br>"
                "• 💬 Community discussions<br>"
                "• 📊 Progress tracking<br>"
                "• 💭 Reflections and journaling<br><br>"
                '<em>Try saying "Molar mass of H2O" or "Quiz on atoms"</em>'
                "</div>"
            ),
            "card": {
                "type": "help",
                "suggestions": suggestions
            }
        }

    # Keep all existing methods unchanged
    def handle_quiz_management(self, message, enhanced_context=None):
        """Handle quiz pause, resume, end commands"""
        msg_lower = message.lower()
        
        if any(phrase in msg_lower for phrase in ['pause quiz', 'stop quiz']):
            self.session['quiz_paused'] = True
            return {
                "text": (
                    "<div class='alert alert-warning'>"
                    "<strong>⏸️ Quiz Paused</strong><br>"
                    "Your quiz progress has been saved. You can continue exploring other features.<br>"
                    "Say 'resume quiz' when you're ready to continue, or 'end quiz' to finish."
                    "</div>"
                ),
                "card": {
                    "type": "quiz_paused",
                    "actions": [
                        {"text": "Resume Quiz", "action": "resume quiz"},
                        {"text": "End Quiz", "action": "end quiz"},
                        {"text": "Show Recent Threads", "action": "show recent threads"}
                    ]
                }
            }
        
        elif any(phrase in msg_lower for phrase in ['end quiz', 'quit quiz', 'exit quiz']):
            self.session['quiz_active'] = False
            self.session['quiz_paused'] = False
            if 'quiz_data' in self.session:
                del self.session['quiz_data']
            
            return {
                "text": (
                    "<div class='alert alert-info'>"
                    "<strong>🏁 Quiz Ended</strong><br>"
                    "Thanks for practicing! You can start a new quiz anytime or explore other features."
                    "</div>"
                ),
                "card": {
                    "type": "help",
                    "suggestions": [
                        "Start a new quiz",
                        "Show recent threads",
                        "How am I doing?",
                        "Molar mass of H2O"
                    ]
                }
            }
        
        elif 'resume quiz' in msg_lower:
            self.session['quiz_paused'] = False
            return {
                "text": (
                    "<div class='alert alert-success'>"
                    "<strong>▶️ Quiz Resumed</strong><br>"
                    "Welcome back! Let's continue where you left off."
                    "</div>"
                )
            }
        
        return {
            "text": (
                "<div class='alert alert-info'>"
                "Quiz management options: 'pause quiz', 'resume quiz', 'end quiz'"
                "</div>"
            )
        }

    def evaluate_arithmetic(self, expr, enhanced_context=None):
        """Enhanced arithmetic evaluation"""
        try:
            result = eval(expr, {"__builtins__": {}})
            return (
                f"<div class='alert alert-success'>"
                f"The result is: <strong>{result}</strong>"
                "</div>"
            )
        except Exception as e:
            return (
                f"<div class='alert alert-danger'>"
                f"Could not evaluate: {str(e)}"
                "</div>"
            )

    def evaluate_symbolic_math(self, msg, enhanced_context=None):
        """Enhanced symbolic math evaluation"""
        x = symbols("x")
        expr = msg.replace("^", "**")
        try:
            if expr.startswith("solve"):
                part = re.sub(r"solve\s*", "", expr, flags=re.IGNORECASE)
                lhs, rhs = part.split("=")
                eq = Eq(parse_expr(lhs), parse_expr(rhs))
                sols = solve(eq, x)
                return (
                    f"<div class='alert alert-success'>"
                    f"Solution(s): <strong>{sols}</strong>"
                    "</div>"
                )
            if expr.startswith("simplify"):
                part = re.sub(r"simplify\s*", "", expr, flags=re.IGNORECASE)
                res = simplify(parse_expr(part))
                return (
                    f"<div class='alert alert-success'>"
                    f"Simplified: <strong>{res}</strong>"
                    "</div>"
                )
            if expr.startswith("integrate"):
                part = re.sub(r"integrate\s*", "", expr, flags=re.IGNORECASE)
                res = integrate(parse_expr(part), x)
                return (
                    f"<div class='alert alert-success'>"
                    f"∫({part})dx = <strong>{res} + C</strong>"
                    "</div>"
                )
            if any(w in msg for w in ["diff", "differentiate", "derivative"]):
                part = re.sub(r"(diff|differentiate|derivative)\s*", "", msg, flags=re.IGNORECASE)
                res = diff(parse_expr(part), x)
                return (
                    f"<div class='alert alert-success'>"
                    f"d/dx({part}) = <strong>{res}</strong>"
                    "</div>"
                )
        except Exception as e:
            return (
                f"<div class='alert alert-danger'>"
                f"Math error: {str(e)}"
                "</div>"
            )

        return (
            "<div class='alert alert-info'>"
            "I can solve, simplify, integrate, or differentiate expressions."
            "</div>"
        )

    def show_recent_reflections(self, reflection_service):
        """Show user's recent reflections"""
        reflections = reflection_service.get_recent_reflections()
        
        if not reflections:
            return (
                "<div class='alert alert-info'>"
                "You haven't saved any reflections yet. Try sharing what's on your mind!"
                "</div>"
            )
        
        html = "<div class='alert alert-primary'><strong>📝 Your Recent Reflections:</strong></div>"
        
        for reflection in reflections:
            html += f"""
            <div class="card mb-2">
                <div class="card-body">
                    <small class="text-muted">{reflection.timestamp.strftime('%b %d, %Y at %I:%M %p')}</small>
                    <p class="mb-1">{reflection.message}</p>
                    <small><span class="badge bg-secondary">Reflection</span></small>
                </div>
            </div>
            """
        
        return html

    def _get_recent_threads(self):
        """Get recent threads with proper data structure"""
        try:
            threads = [
                {
                    "id": 1,
                    "title": "Help with Chemistry Quiz",
                    "author": "student123",
                    "replies": 5,
                    "last_activity": "2 hours ago"
                },
                {
                    "id": 2, 
                    "title": "Calculus Study Group",
                    "author": "mathwiz",
                    "replies": 12,
                    "last_activity": "4 hours ago"
                },
                {
                    "id": 3,
                    "title": "FAFSA Application Tips",
                    "author": "advisor_jane",
                    "replies": 8,
                    "last_activity": "1 day ago"
                }
            ]
            
            return {
                "text": (
                    "<div class='alert alert-info'>"
                    "<strong>💬 Recent Community Threads</strong><br>"
                    "Here are the latest discussions in The Commons:"
                    "</div>"
                ),
                "card": {
                    "type": "thread_list",
                    "threads": threads
                }
            }
            
        except Exception as e:
            return {
                "text": f"<div class='alert alert-danger'>Could not load recent threads: {str(e)}</div>"
            }

    def _get_popular_threads(self):
        """Get popular threads"""
        return {
            "text": (
                "<div class='alert alert-info'>"
                "🔥 Popular discussions are heating up in The Commons! "
                "<a href='/community/' class='btn btn-sm btn-primary'>Join the conversation</a>"
                "</div>"
            )
        }

    def _get_boards(self):
        """Get discussion boards"""
        return {
            "text": (
                "<div class='alert alert-info'>"
                "📋 Available Discussion Boards:<br>"
                "• Math & Science<br>"
                "• Study Groups<br>"
                "• Financial Aid<br>"
                "• General Discussion"
                "</div>"
            )
        }

    def handle_analytics(self, message, user):
        """Handle analytics requests"""
        try:
            from apps.analytics.services import AnalyticsService
            service = AnalyticsService()
            result = service.handle_analytics_request(message, user)
            return self._format_response(result)
        except Exception as e:
            return {
                "text": f"<div class='alert alert-danger'>Analytics error: {str(e)}</div>"
            }

    def extract_topic_from_message(self, message):
        topic_map = {
            "atoms": "Atoms, Ions, and Isotopes",
            "molecule": "Molecules", 
            "reaction": "Chemical Reactions",
            "integrate": "Calculus",
            "solve": "Algebra",
            "chemistry": "Chemistry",
            "math": "Mathematics",
            "fafsa": "Financial Aid",
        }
        msg = message.lower()
        for key, val in topic_map.items():
            if key in msg:
                return val
        return "this topic"

    def extract_formula(self, message):
        match = re.search(r"\b([A-Z][a-z]?\d*)+\b", message)
        return match.group(0) if match else None