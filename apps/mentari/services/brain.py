# apps/mentari/services/brain.py

import re
import random
from datetime import datetime, timedelta

from sympy import symbols, Eq, solve, simplify, integrate, diff
from sympy.parsing.sympy_parser import parse_expr
from django.db.models import Avg

from apps.mentari.services.learning_brain import LearningContext


class MentariBrain:
    def __init__(self):
        self.user = None
        self.session = None
        self.context = None

    def respond(self, message, user=None, session=None):
        """
        Main entry point for handling user messages.
        Routes to ALL available services for comprehensive learning support.
        """
        self.user = user
        self.session = session

        # Initialize learning context for authenticated users
        if user and user.is_authenticated:
            self.context = LearningContext(user.id)

        original = message.strip()
        msg = original.lower()

        try:
            # 1. Greeting
            if self.is_greeting(msg):
                return self._format_response(self.handle_greeting())

            # 2. Social-Emotional Learning & Mental Health
            if any(phrase in msg for phrase in [
                "feeling", "stressed", "anxious", "overwhelmed", "sad", "frustrated", 
                "emotional", "mental health", "mood", "stress", "worry", "anxious"
            ]):
                return self.handle_emotional_support(original, user)

            # 3. College & FAFSA Advising
            if any(phrase in msg for phrase in [
                "fafsa", "college", "application", "financial aid", "scholarship", 
                "efc", "college prep", "admissions", "university"
            ]):
                return self.handle_advising(original, user)

            # 4. Essay & Writing Support
            if any(phrase in msg for phrase in [
                "essay", "writing", "personal statement", "college essay", 
                "essay help", "writing feedback", "grammar", "proofread"
            ]):
                return self.handle_essay_support(original, user)

            # 5. Advanced Math (Enhanced Services)
            if any(phrase in msg for phrase in [
                "factor", "expand", "derivative", "integral", "limit",
                "trigonometry", "sin", "cos", "tan", "triangle", "circle",
                "geometry", "pythagorean", "area", "perimeter"
            ]):
                return self.handle_advanced_math(original)

            # 6. Learning progress query
            if any(phrase in msg for phrase in 
                   ["how am i doing", "my progress", "what should i learn", "my stats"]):
                return self._format_response(self.provide_learning_guidance())

            # 7. General encouragement request
            if any(phrase in msg for phrase in 
                   ["don't understand", "confused", "help me", "struggling", "difficult"]):
                return self._format_response(self.provide_encouragement(msg))

            # 8. Code execution
            if any(phrase in msg for phrase in [
                "run code", "execute", "python code", "javascript", "programming"
            ]):
                return self.handle_code_execution(original, user)

            # 9. Tutorial recommendations
            if any(phrase in msg for phrase in [
                "tutorial", "learn about", "teach me", "how to", "guide"
            ]):
                return self.handle_tutorials(original, user)

            # 10. Basic arithmetic (keep existing)
            if self.is_arithmetic(msg):
                return self._format_response(self.evaluate_arithmetic(msg))

            # 11. Basic symbolic math (keep existing)
            if self.is_symbolic_math(msg):
                return self._format_response(self.evaluate_symbolic_math(original))

            # 12. Active quiz session (keep existing)
            if self.session and self.session.get("quiz_active") and not self.session.get("quiz_paused"):
                if self.is_quiz_answer(msg, original):
                    from apps.mentari.services.quiz import handle_quiz_answer
                    result = handle_quiz_answer(original, user, session)
                    return self._format_response(result)

            # 13. Quiz management (keep existing)
            if self.session and (self.session.get("quiz_active") or self.session.get("quiz_paused")):
                if any(phrase in msg for phrase in ['pause quiz', 'stop quiz', 'end quiz', 'quit quiz', 'exit quiz', 'resume quiz']):
                    return self.handle_quiz_management(msg)

            # 14. Chemistry calculations (keep existing)
            chemistry_calc_keywords = [
                "molar mass", "calculate molar", "molecular weight",
                "element info", "atomic number", "compound analysis"
            ]
            if any(k in msg for k in chemistry_calc_keywords):
                from apps.mentari.services.chemistry import handle_chemistry_request
                result = handle_chemistry_request(original, user)
                return self._format_response(result)

            # 15. General chemistry (keep existing)
            if any(k in msg for k in ["tell me about", "analyze the molecule", "chemistry", "element", "periodic table", "molecule", "compound"]):
                from apps.mentari.services.chemistry import handle_chemistry_request
                result = handle_chemistry_request(original, user)
                return self._format_response(result)

            # 16. Quiz requests (keep existing)
            quiz_triggers = [
                "quiz on atoms", "quiz on molecules", "quiz on periodic",
                "atoms quiz", "molecules quiz", "periodic quiz",
                "take chemistry quiz", "start chemistry quiz", "chemistry test",
                "start a new quiz", "start quiz", "take a quiz"
            ]
            if any(phrase in msg for phrase in quiz_triggers) or msg.startswith("quiz on"):
                from apps.mentari.services.quiz import handle_quiz_request
                result = handle_quiz_request(original, user, session)
                return self._format_response(result)

            # 17. Community (keep existing)
            if any(k in msg for k in ["forum", "thread", "discussion", "community", "recent threads"]):
                return self.handle_community(original)

            # 18. Reflection / journaling (keep existing)
            if any(k in msg for k in ["reflect", "journal", "thinking about", "recent reflections", "my reflections"]):
                return self._format_response(self.handle_reflection(original, user))

            # 19. Blog / articles (keep existing)
            if any(k in msg for k in ["blog", "article", "news", "read"]):
                from apps.mentari.services.blog import handle_blog_request
                result = handle_blog_request(original, user)
                return self._format_response(result)

            # 20. Analytics / tracking (keep existing)
            if any(k in msg for k in ["log", "track", "stats"]):
                result = self.handle_analytics(original, user)
                return self._format_response(result)

            # 21. Fallback help
            return self._format_response(self.get_help_message())

        except Exception as e:
            error_message = (
                f"<div class='alert alert-danger'>"
                f"I encountered an error: {str(e)}<br>"
                f"<small>Please try rephrasing your question or contact support if this persists.</small>"
                "</div>"
            )
            return self._format_response(error_message)

  
    def _format_response(self, response):
        """
        Ensures consistent response format for the frontend
        """
        if isinstance(response, dict):
            # Already properly formatted
            formatted_response = response
        elif isinstance(response, str):
            # Convert string to proper format
            formatted_response = {"text": response}
        else:
            # Fallback for unexpected types
            formatted_response = {"text": str(response)}
        
        # Add quiz status if applicable
        if self.session:
            if self.session.get("quiz_active") and not self.session.get("quiz_paused"):
                formatted_response["quiz_status"] = "active"
            elif self.session.get("quiz_paused"):
                formatted_response["quiz_status"] = "paused"
        
        return formatted_response

    def is_quiz_answer(self, msg, original):
        """
        Determine if the message is a quiz answer vs other input
        """
        # Direct letter answers
        if msg in ['a', 'b', 'c', 'd']:
            return True
        
        # Answer format: "answer: A", "answer is B", etc.
        if any(phrase in msg for phrase in ['answer:', 'answer is', 'my answer']):
            return True
        
        # Quiz control commands
        if any(phrase in msg for phrase in ['skip question', 'next question', 'end quiz', 'quit quiz', 'exit quiz']):
            return True
        
        # If it's just a single letter, probably a quiz answer
        if len(original.strip()) == 1 and original.strip().upper() in ['A', 'B', 'C', 'D']:
            return True
        
        return False

    def handle_quiz_management(self, message):
        """Handle quiz pause, resume, end commands"""
        msg_lower = message.lower()
        
        if any(phrase in msg_lower for phrase in ['pause quiz', 'stop quiz']):
            # Pause the quiz but keep session data
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
            # End the quiz session
            self.session['quiz_active'] = False
            self.session['quiz_paused'] = False
            # Clear quiz data
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
            # Resume paused quiz
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

    # -- Greeting --

    def is_greeting(self, msg):
        return any(g in msg for g in [
            "hello", "hi", "hey", "good morning",
            "good afternoon", "good evening", "greetings"
        ])

    def handle_greeting(self):
        if not self.user or not self.user.is_authenticated:
            return {
                "text": (
                    "<div class='alert alert-info'>"
                    "<strong>Hello!</strong> I'm Mentari, your personal learning companion. 🌟<br>"
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
                ),
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

        now = datetime.now()
        hour = now.hour
        if hour < 12:
            salutation = "Good morning"
        elif hour < 17:
            salutation = "Good afternoon"
        else:
            salutation = "Good evening"

        user_name = self.user.username
        return {
            "text": (
                f"<div class='alert alert-info'>"
                f"<strong>{salutation}, {user_name}!</strong><br>"
                "What would you like to explore today?"
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

    # -- Learning Guidance & Encouragement --

    def provide_learning_guidance(self):
        from apps.quiz.models import QuizAttempt, Topic
        from apps.analytics.models import Event

        if not self.user or not self.user.is_authenticated:
            return "<div class='alert alert-warning'>Please log in to view your progress.</div>"

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

    def provide_encouragement(self, msg):
        topic = self.extract_topic_from_message(msg)
        choices = [
            f"I know {topic} can feel tricky—you're doing great! 💪",
            f"Let's break down {topic} step by step.",
            f"Don't worry, {topic} clicks for everyone at their own pace.",
        ]
        return (
            "<div class='alert alert-warning'>"
            + random.choice(choices) +
            "</div>"
        )

    # -- Arithmetic & Symbolic Math --

    def is_arithmetic(self, msg):
        return re.fullmatch(r"[0-9\s\+\-\*\/\.\(\)]+", msg) is not None

    def evaluate_arithmetic(self, expr):
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

    def is_symbolic_math(self, msg):
        return any(k in msg for k in [
            "solve", "simplify", "integrate", "differentiate", "diff", "derivative"
        ])

    def evaluate_symbolic_math(self, msg):
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

    # -- Enhanced Reflection Handler --

    def handle_reflection(self, message, user):
        from apps.mentari.services.reflection import ReflectionService
        
        reflection_service = ReflectionService(user=user, session=self.session)
        
        msg_lower = message.lower()
        
        if any(phrase in msg_lower for phrase in ["recent reflections", "my reflections", "show reflections"]):
            return self.show_recent_reflections(reflection_service)
        elif any(phrase in msg_lower for phrase in ["reflection prompt", "what to reflect on", "reflection help"]):
            return reflection_service.get_reflection_prompt()
        else:
            return reflection_service.handle_reflection_request(message)

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

    # -- Fixed Community Handler --

    def handle_community(self, message):
        """Handle community/forum requests with proper error handling"""
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

    def _get_recent_threads(self):
        """Get recent threads with proper data structure"""
        try:
            # Mock data structure - replace with actual database queries
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

  # ========== NEW ENHANCED INTEGRATIONS ==========

    def handle_emotional_support(self, message, user):
        """Handle social-emotional learning requests"""
        try:
            from apps.mentari.services.emotion_guide import EmotionGuideService
            
            service = EmotionGuideService()
            msg_lower = message.lower()
            
            # Detect mood/emotion in message
            emotions = {
                "anxious": ["anxious", "anxiety", "nervous", "worried"],
                "stressed": ["stressed", "overwhelmed", "pressure"],
                "sad": ["sad", "down", "depressed", "upset"],
                "frustrated": ["frustrated", "angry", "mad"],
                "happy": ["happy", "excited", "good", "great"],
                "confused": ["confused", "lost", "don't understand"]
            }
            
            detected_emotion = "neutral"
            for emotion, keywords in emotions.items():
                if any(keyword in msg_lower for keyword in keywords):
                    detected_emotion = emotion
                    break
            
            # Determine stress level
            stress_indicators = ["overwhelmed", "can't handle", "too much", "breaking down"]
            if any(indicator in msg_lower for indicator in stress_indicators):
                stress_level = "high"
            elif detected_emotion in ["anxious", "stressed", "frustrated"]:
                stress_level = "moderate"
            else:
                stress_level = "low"
            
            # Get situation context
            situation = ""
            if "test" in msg_lower or "exam" in msg_lower:
                situation = "test anxiety"
            elif "college" in msg_lower:
                situation = "college stress"
            elif "friend" in msg_lower or "social" in msg_lower:
                situation = "social issues"
            
            response = service.mood_check_in(detected_emotion, stress_level, situation)
            
            # Format response
            formatted_text = f"""
            <div class='alert alert-primary'>
                <h5>💙 Emotional Support</h5>
                <p><strong>Acknowledgment:</strong> {response['acknowledgment']}</p>
                <p><strong>Validation:</strong> {response['validation']}</p>
            </div>
            
            <div class='alert alert-info'>
                <h6>🛠️ Coping Strategies:</h6>
                <ul>
                    {''.join([f'<li>{strategy}</li>' for strategy in response['strategies']])}
                </ul>
            </div>
            
            <div class='alert alert-success'>
                <p><strong>Follow-up:</strong> {response['follow_up']}</p>
            </div>
            """
            
            if 'situation_advice' in response:
                formatted_text += f"""
                <div class='alert alert-warning'>
                    <h6>💡 Situation-Specific Advice:</h6>
                    <p>{response['situation_advice']}</p>
                </div>
                """
            
            return {
                "text": formatted_text,
                "card": {
                    "type": "emotional_support",
                    "emotion": detected_emotion,
                    "stress_level": stress_level,
                    "strategies": response['strategies'][:3],
                    "actions": [
                        {"text": "Mindfulness Exercise", "action": "mindfulness exercise"},
                        {"text": "Goal Setting Help", "action": "help me set goals"},
                        {"text": "Talk to Counselor", "url": "/contact-counselor/"}
                    ]
                }
            }
            
        except Exception as e:
            return {
                "text": f"<div class='alert alert-warning'>I'm here to support you, though I encountered a technical issue: {str(e)}</div>"
            }

    def handle_advising(self, message, user):
        """Handle college and FAFSA advising requests"""
        try:
            from apps.mentari.services.advising import AdvisingService
            
            service = AdvisingService()
            msg_lower = message.lower()
            
            if "fafsa" in msg_lower:
                timeline = service.get_fafsa_timeline()
                
                timeline_html = "<ul>"
                for date, task in timeline.items():
                    timeline_html += f"<li><strong>{date}:</strong> {task}</li>"
                timeline_html += "</ul>"
                
                return {
                    "text": f"""
                    <div class='alert alert-info'>
                        <h5>📋 FAFSA Timeline</h5>
                        {timeline_html}
                    </div>
                    """,
                    "card": {
                        "type": "fafsa_timeline",
                        "timeline": timeline,
                        "actions": [
                            {"text": "Calculate EFC", "action": "calculate my efc"},
                            {"text": "Scholarship Search", "action": "scholarship tips"},
                            {"text": "FAFSA Website", "url": "https://studentaid.gov/"}
                        ]
                    }
                }
            
            elif "efc" in msg_lower or "calculate" in msg_lower:
                return {
                    "text": """
                    <div class='alert alert-info'>
                        <h5>💰 EFC Calculator</h5>
                        <p>To calculate your Expected Family Contribution, I need some information:</p>
                        <ul>
                            <li>Parent annual income</li>
                            <li>Student annual income (if any)</li>
                            <li>Family assets</li>
                            <li>Family size</li>
                        </ul>
                        <p>Try: "Calculate EFC with parent income 60000, student income 2000, assets 10000, family size 4"</p>
                    </div>
                    """,
                    "card": {
                        "type": "efc_calculator",
                        "actions": [
                            {"text": "FAFSA Timeline", "action": "fafsa timeline"},
                            {"text": "Scholarship Tips", "action": "scholarship search tips"}
                        ]
                    }
                }
            
            elif "scholarship" in msg_lower:
                tips = service.scholarship_search_tips()
                
                tips_html = f"""
                <div class='alert alert-success'>
                    <h5>🎓 Scholarship Search Tips</h5>
                    <h6>Where to Look:</h6>
                    <ul>{''.join([f'<li>{tip}</li>' for tip in tips['where_to_look']])}</ul>
                    
                    <h6>Application Tips:</h6>
                    <ul>{''.join([f'<li>{tip}</li>' for tip in tips['application_tips']])}</ul>
                </div>
                """
                
                return {
                    "text": tips_html,
                    "card": {
                        "type": "scholarship_tips",
                        "tips": tips,
                        "actions": [
                            {"text": "Essay Help", "action": "college essay help"},
                            {"text": "FAFSA Info", "action": "fafsa timeline"}
                        ]
                    }
                }
            
            elif "college" in msg_lower or "application" in msg_lower:
                # Determine grade level from context or default to senior
                grade_level = "senior"
                if "freshman" in msg_lower or "9th" in msg_lower:
                    grade_level = "freshman"
                elif "sophomore" in msg_lower or "10th" in msg_lower:
                    grade_level = "sophomore"
                elif "junior" in msg_lower or "11th" in msg_lower:
                    grade_level = "junior"
                
                checklist = service.get_application_checklist(grade_level)
                
                checklist_html = f"<h5>📚 {grade_level.title()} Year Checklist</h5><ul>"
                checklist_html += ''.join([f'<li>{item}</li>' for item in checklist])
                checklist_html += "</ul>"
                
                return {
                    "text": f"<div class='alert alert-primary'>{checklist_html}</div>",
                    "card": {
                        "type": "college_checklist",
                        "grade_level": grade_level,
                        "checklist": checklist,
                        "actions": [
                            {"text": "Essay Help", "action": "personal statement help"},
                            {"text": "FAFSA Info", "action": "fafsa timeline"},
                            {"text": "Scholarship Search", "action": "scholarship tips"}
                        ]
                    }
                }
            
            else:
                return {
                    "text": """
                    <div class='alert alert-info'>
                        <h5>🎓 College & Financial Aid Support</h5>
                        <p>I can help you with:</p>
                        <ul>
                            <li>📋 FAFSA timeline and requirements</li>
                            <li>💰 EFC (Expected Family Contribution) estimates</li>
                            <li>🎓 Scholarship search strategies</li>
                            <li>📚 College application checklists</li>
                            <li>✍️ Essay writing support</li>
                        </ul>
                        <p>Try asking: "Show me FAFSA timeline" or "Help with college applications"</p>
                    </div>
                    """,
                    "card": {
                        "type": "advising_help",
                        "actions": [
                            {"text": "FAFSA Timeline", "action": "fafsa timeline"},
                            {"text": "College Checklist", "action": "college application checklist"},
                            {"text": "Scholarship Tips", "action": "scholarship search tips"}
                        ]
                    }
                }
                
        except Exception as e:
            return {
                "text": f"<div class='alert alert-warning'>I'm here to help with college planning: {str(e)}</div>"
            }

    def handle_essay_support(self, message, user):
        """Handle essay writing and feedback requests"""
        try:
            from apps.mentari.services.essay_feedback import EssayFeedbackService
            
            service = EssayFeedbackService()
            msg_lower = message.lower()
            
            if "personal statement" in msg_lower or "college essay" in msg_lower:
                prompt_help = service.get_essay_prompts_help("personal_statement")
                
                return {
                    "text": f"""
                    <div class='alert alert-success'>
                        <h5>✍️ Personal Statement Guide</h5>
                        <p><strong>Purpose:</strong> {prompt_help['purpose']}</p>
                        <p><strong>Approach:</strong> {prompt_help['approach']}</p>
                        <p><strong>Structure:</strong> {prompt_help['structure']}</p>
                        
                        <h6>💡 Key Tips:</h6>
                        <ul>{''.join([f'<li>{tip}</li>' for tip in prompt_help['tips']])}</ul>
                    </div>
                    """,
                    "card": {
                        "type": "essay_guide",
                        "essay_type": "personal_statement",
                        "guide": prompt_help,
                        "actions": [
                            {"text": "Analyze My Essay", "action": "analyze my essay"},
                            {"text": "Challenge Essay Tips", "action": "challenge essay help"},
                            {"text": "Why Us Essay Help", "action": "why us essay help"}
                        ]
                    }
                }
            
            elif "analyze" in msg_lower or "feedback" in msg_lower:
                return {
                    "text": """
                    <div class='alert alert-info'>
                        <h5>📝 Essay Analysis</h5>
                        <p>I can analyze your essay for:</p>
                        <ul>
                            <li>📊 Structure and organization</li>
                            <li>📖 Readability and flow</li>
                            <li>💭 Content and personal voice</li>
                            <li>✨ Style and variety</li>
                            <li>🎯 Essay-type specific requirements</li>
                        </ul>
                        <p>To get started, please paste your essay text and I'll provide detailed feedback!</p>
                    </div>
                    """,
                    "card": {
                        "type": "essay_analyzer",
                        "actions": [
                            {"text": "Personal Statement Help", "action": "personal statement guide"},
                            {"text": "Grammar Tips", "action": "grammar and style tips"},
                            {"text": "Essay Examples", "action": "essay examples"}
                        ]
                    }
                }
            
            elif len(message.split()) > 50:  # If it looks like an essay
                # Analyze the essay
                analysis = service.analyze_college_essay(message, "personal_statement")
                
                feedback_html = f"""
                <div class='alert alert-primary'>
                    <h5>📊 Essay Analysis Results</h5>
                    <p><strong>Word Count:</strong> {analysis['word_count']}</p>
                    <p><strong>Readability:</strong> {analysis['readability'].get('description', 'N/A')}</p>
                    <p><strong>Paragraphs:</strong> {analysis['structure']['paragraph_count']}</p>
                </div>
                
                <div class='alert alert-info'>
                    <h6>🔍 Structure Feedback:</h6>
                    <ul>{''.join([f'<li>{feedback}</li>' for feedback in analysis['structure']['feedback']])}</ul>
                </div>
                
                <div class='alert alert-success'>
                    <h6>💡 Suggestions for Improvement:</h6>
                    <ul>{''.join([f'<li>{suggestion}</li>' for suggestion in analysis['suggestions']])}</ul>
                </div>
                """
                
                return {
                    "text": feedback_html,
                    "card": {
                        "type": "essay_analysis",
                        "analysis": analysis,
                        "actions": [
                            {"text": "Get More Tips", "action": "personal statement guide"},
                            {"text": "Grammar Check", "action": "grammar help"}
                        ]
                    }
                }
            
            else:
                # General essay help
                return {
                    "text": """
                    <div class='alert alert-info'>
                        <h5>✍️ Essay Writing Support</h5>
                        <p>I can help you with:</p>
                        <ul>
                            <li>📝 Personal statement guidance</li>
                            <li>🎯 "Why Us" essay tips</li>
                            <li>💪 Challenge/overcoming obstacles essays</li>
                            <li>📊 Essay analysis and feedback</li>
                            <li>📖 Grammar and style improvement</li>
                        </ul>
                        <p>What type of essay are you working on?</p>
                    </div>
                    """,
                    "card": {
                        "type": "essay_help",
                        "actions": [
                            {"text": "Personal Statement", "action": "personal statement help"},
                            {"text": "Analyze My Essay", "action": "essay analysis help"},
                            {"text": "Grammar Tips", "action": "grammar and writing tips"}
                        ]
                    }
                }
                
        except Exception as e:
            return {
                "text": f"<div class='alert alert-warning'>I'm here to help with your writing: {str(e)}</div>"
            }

    def handle_advanced_math(self, message):
        """Handle advanced math using specialized services"""
        try:
            msg_lower = message.lower()
            
            # Determine which math service to use
            if any(keyword in msg_lower for keyword in ["factor", "expand", "simplify", "equation", "solve"]):
                from apps.mentari.services.algebra import AlgebraSolver
                solver = AlgebraSolver()
                
                if "factor" in msg_lower:
                    expr = self._extract_expression(message, "factor")
                    result = solver.factor_expression(expr)
                elif "expand" in msg_lower:
                    expr = self._extract_expression(message, "expand")
                    result = solver.expand_expression(expr)
                elif "solve" in msg_lower and "=" in message:
                    result = solver.solve_equation(message)
                else:
                    expr = self._extract_expression(message)
                    result = solver.simplify_expression(expr)
                
                return {
                    "text": f"<div class='alert alert-success'><h5>📐 Algebra Solution</h5><p>{result}</p></div>",
                    "card": {
                        "type": "math_solution",
                        "subject": "algebra",
                        "result": result
                    }
                }
            
            elif any(keyword in msg_lower for keyword in ["derivative", "integral", "limit", "calculus"]):
                from apps.mentari.services.calculus import CalculusSolver
                solver = CalculusSolver()
                
                if "derivative" in msg_lower or "differentiate" in msg_lower:
                    expr = self._extract_expression(message, "derivative")
                    result = solver.differentiate(expr)
                elif "integral" in msg_lower or "integrate" in msg_lower:
                    expr = self._extract_expression(message, "integral")
                    result = solver.integrate_expr(expr)
                elif "limit" in msg_lower:
                    expr = self._extract_expression(message, "limit")
                    result = solver.calculate_limit(expr, "0")  # Default to limit as x approaches 0
                else:
                    return {
                        "text": """
                        <div class='alert alert-info'>
                            <h5>📈 Calculus Help</h5>
                            <p>I can help with:</p>
                            <ul>
                                <li>Derivatives: "Find derivative of x^2 + 3x"</li>
                                <li>Integrals: "Integrate x^2 + 1"</li>
                                <li>Limits: "Find limit of (x^2-1)/(x-1) as x approaches 1"</li>
                            </ul>
                        </div>
                        """
                    }
                
                return {
                    "text": f"<div class='alert alert-success'><h5>📈 Calculus Solution</h5><p>{result}</p></div>",
                    "card": {
                        "type": "math_solution",
                        "subject": "calculus",
                        "result": result
                    }
                }
            
            elif any(keyword in msg_lower for keyword in ["sin", "cos", "tan", "trigonometry", "degrees", "radians"]):
                from apps.mentari.services.trigonometry import TrigSolver
                solver = TrigSolver()
                
                if any(func in msg_lower for func in ["sin", "cos", "tan"]):
                    # Extract function and value
                    import re
                    match = re.search(r'(sin|cos|tan)\s*\(?\s*(\d+\.?\d*)', msg_lower)
                    if match:
                        func, value = match.groups()
                        unit = "degrees" if "degree" in msg_lower else "radians"
                        result = solver.evaluate_trig_function(func, value, unit)
                    else:
                        result = "Please specify a value, e.g., 'sin(30 degrees)' or 'cos(π/4)'"
                else:
                    expr = self._extract_expression(message)
                    result = solver.simplify_trig(expr)
                
                return {
                    "text": f"<div class='alert alert-success'><h5>📐 Trigonometry Solution</h5><p>{result}</p></div>",
                    "card": {
                        "type": "math_solution",
                        "subject": "trigonometry",
                        "result": result
                    }
                }
            
            elif any(keyword in msg_lower for keyword in ["triangle", "circle", "area", "perimeter", "pythagorean", "geometry"]):
                from apps.mentari.services.geometry import GeometryHelper
                helper = GeometryHelper()
                
                if "circle" in msg_lower and "area" in msg_lower:
                    radius = self._extract_number(message)
                    result = helper.area_of_circle(radius) if radius else "Please specify the radius"
                elif "circle" in msg_lower and ("circumference" in msg_lower or "perimeter" in msg_lower):
                    radius = self._extract_number(message)
                    result = helper.circumference_of_circle(radius) if radius else "Please specify the radius"
                elif "pythagorean" in msg_lower or ("triangle" in msg_lower and any(num in message for num in "0123456789")):
                    numbers = re.findall(r'\d+\.?\d*', message)
                    if len(numbers) >= 2:
                        result = helper.pythagorean_theorem(float(numbers[0]), float(numbers[1]))
                    else:
                        result = "Please provide two sides of the triangle"
                elif "triangle" in msg_lower and "area" in msg_lower:
                    numbers = re.findall(r'\d+\.?\d*', message)
                    if len(numbers) >= 2:
                        result = helper.triangle_area(numbers[0], numbers[1])
                    else:
                        result = "Please provide base and height"
                else:
                    return {
                        "text": """
                        <div class='alert alert-info'>
                            <h5>📐 Geometry Help</h5>
                            <p>I can help with:</p>
                            <ul>
                                <li>Circle area: "Find area of circle with radius 5"</li>
                                <li>Pythagorean theorem: "Find hypotenuse with sides 3 and 4"</li>
                                <li>Triangle area: "Triangle area with base 6 and height 8"</li>
                            </ul>
                        </div>
                        """
                    }
                
                return {
                    "text": f"<div class='alert alert-success'><h5>📐 Geometry Solution</h5><p>{result}</p></div>",
                    "card": {
                        "type": "math_solution",
                        "subject": "geometry",
                        "result": result
                    }
                }
            
            else:
                return {
                    "text": """
                    <div class='alert alert-info'>
                        <h5>🔢 Advanced Math Help</h5>
                        <p>I can help with:</p>
                        <ul>
                            <li>📐 <strong>Algebra:</strong> Factor, expand, solve equations</li>
                            <li>📈 <strong>Calculus:</strong> Derivatives, integrals, limits</li>
                            <li>📐 <strong>Trigonometry:</strong> Sin, cos, tan, conversions</li>
                            <li>📐 <strong>Geometry:</strong> Areas, perimeters, Pythagorean theorem</li>
                        </ul>
                        <p>Try: "Factor x^2 + 5x + 6" or "Find derivative of x^3"</p>
                    </div>
                    """,
                    "card": {
                        "type": "math_help",
                        "subjects": ["algebra", "calculus", "trigonometry", "geometry"],
                        "actions": [
                            {"text": "Algebra Help", "action": "algebra help"},
                            {"text": "Calculus Help", "action": "calculus help"},
                            {"text": "Geometry Help", "action": "geometry help"}
                        ]
                    }
                }
                
        except Exception as e:
            return {
                "text": f"<div class='alert alert-warning'>Math calculation error: {str(e)}</div>"
            }

    def handle_code_execution(self, message, user):
        """Handle code execution requests"""
        try:
            from apps.mentari.services.code import handle_code_request
            result = handle_code_request(message, user)
            return self._format_response(result)
        except Exception as e:
            return {
                "text": f"""
                <div class='alert alert-info'>
                    <h5>💻 Code Execution</h5>
                    <p>I can help you run Python code! Try:</p>
                    <ul>
                        <li>"Run code: print('Hello World')"</li>
                        <li>"Execute: for i in range(5): print(i)"</li>
                        <li>"Run code: import math; print(math.sqrt(16))"</li>
                    </ul>
                    <p><small>Error: {str(e)}</small></p>
                </div>
                """
            }

    def handle_tutorials(self, message, user):
        """Handle tutorial and learning resource requests"""
        try:
            from apps.mentari.services.tutorial import handle_tutorial_request
            result = handle_tutorial_request(message, user)
            return self._format_response(result)
        except Exception as e:
            return {
                "text": f"""
                <div class='alert alert-info'>
                    <h5>📚 Tutorial Recommendations</h5>
                    <p>I can recommend tutorials on various topics!</p>
                    <p>Try: "Tutorial on chemistry" or "Learn about calculus"</p>
                    <p><small>Error: {str(e)}</small></p>
                </div>
                """
            }

    # ========== HELPER METHODS ==========

    def _extract_expression(self, message, keyword=None):
        """Extract mathematical expression from message"""
        if keyword:
            # Remove the keyword and extract what follows
            parts = message.lower().split(keyword)
            if len(parts) > 1:
                expr = parts[1].strip()
                # Clean up common prefixes
                expr = re.sub(r'^(of|:|\s)+', '', expr)
                return expr
        
        # Extract expression after common math keywords
        patterns = [
            r'(?:factor|expand|simplify|derivative|integral|solve)\s+(.+)',
            r'(?:find|calculate)\s+(?:the\s+)?(?:derivative|integral|factor|solution)\s+(?:of\s+)?(.+)',
            r'(.+?)(?:\s+where|\s+as|\s+when|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return message

    def _extract_number(self, message):
        """Extract first number from message"""
        import re
        numbers = re.findall(r'\d+\.?\d*', message)
        return float(numbers[0]) if numbers else None


    def get_help_message(self):
        return {
            "text": (
                "<div class='alert alert-info'>"
                "<strong>🌟 I'm Mentari, your comprehensive learning AI!</strong><br><br>"
                "I can help you with:<br>"
                "• 📐 <strong>Advanced Math:</strong> Algebra, calculus, trigonometry, geometry<br>"
                "• 🧪 <strong>Chemistry:</strong> Elements, formulas, calculations<br>"
                "• 📝 <strong>Quizzes:</strong> Interactive assessment and practice<br>"
                "• 🎓 <strong>College Prep:</strong> FAFSA, applications, essays<br>"
                "• 💙 <strong>Emotional Support:</strong> Stress management, SEL<br>"
                "• ✍️ <strong>Writing Help:</strong> Essay feedback and guidance<br>"
                "• 💻 <strong>Code Execution:</strong> Run Python code<br>"
                "• 📚 <strong>Tutorials:</strong> Learning resources<br>"
                "• 💬 <strong>Community:</strong> Connect with peers<br>"
                "• 📊 <strong>Progress Tracking:</strong> Monitor your growth<br>"
                "• 💭 <strong>Reflections:</strong> Journaling and self-assessment<br><br>"
                '<em>Try: "I feel stressed about my exam" or "Factor x^2 + 5x + 6"</em>'
                "</div>"
            ),
            "card": {
                "type": "comprehensive_help",
                "categories": [
                    {"name": "Math Help", "action": "advanced math help"},
                    {"name": "College Prep", "action": "college application help"},
                    {"name": "Emotional Support", "action": "I'm feeling stressed"},
                    {"name": "Essay Writing", "action": "personal statement help"},
                    {"name": "Chemistry", "action": "molar mass of H2O"},
                    {"name": "Take Quiz", "action": "start a quiz"}
                ]
            }
        }
