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
        Returns a consistent response format: {"text": str, "card": dict, "redirect_url": str}
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

            # 2. Learning progress query
            if any(phrase in msg for phrase in 
                   ["how am i doing", "my progress", "what should i learn", "my stats"]):
                return self._format_response(self.provide_learning_guidance())

            # 3. General encouragement request
            if any(phrase in msg for phrase in 
                   ["don't understand", "confused", "help me", "struggling", "difficult"]):
                return self._format_response(self.provide_encouragement(msg))

            # 4. Arithmetic
            if self.is_arithmetic(msg):
                return self._format_response(self.evaluate_arithmetic(msg))

            # 5. Symbolic math
            if self.is_symbolic_math(msg):
                return self._format_response(self.evaluate_symbolic_math(original))

            # 6. Active quiz session (only handle explicit quiz answers)
            if self.session and self.session.get("quiz_active") and not self.session.get("quiz_paused"):
                if self.is_quiz_answer(msg, original):
                    from apps.mentari.services.quiz import handle_quiz_answer
                    result = handle_quiz_answer(original, user, session)
                    return self._format_response(result)

            # 7. Quiz management (pause, resume, end) - works for both active and paused quizzes
            if self.session and (self.session.get("quiz_active") or self.session.get("quiz_paused")):
                if any(phrase in msg for phrase in ['pause quiz', 'stop quiz', 'end quiz', 'quit quiz', 'exit quiz', 'resume quiz']):
                    return self.handle_quiz_management(msg)

            # 8. Chemistry calculations (specific)
            chemistry_calc_keywords = [
                "molar mass", "calculate molar", "molecular weight",
                "element info", "atomic number", "compound analysis"
            ]
            if any(k in msg for k in chemistry_calc_keywords):
                from apps.mentari.services.chemistry import handle_chemistry_request
                result = handle_chemistry_request(original, user)
                return self._format_response(result)

            # 9. Community (fixed)
            if any(k in msg for k in ["forum", "thread", "discussion", "community", "recent threads"]):
                return self.handle_community(original)

            # 10. General chemistry (non-quiz)
            if any(k in msg for k in ["tell me about", "analyze the molecule", "chemistry", "element", "periodic table", "molecule", "compound"]):
                from apps.mentari.services.chemistry import handle_chemistry_request
                result = handle_chemistry_request(original, user)
                return self._format_response(result)

            # 11. Explicit quiz requests (narrowed)
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

            # 12. Reflection / journaling
            if any(k in msg for k in ["reflect", "journal", "feeling", "thinking about", "recent reflections", "my reflections"]):
                return self._format_response(self.handle_reflection(original, user))

            # 13. Blog / articles
            if any(k in msg for k in ["blog", "article", "news", "read"]):
                from apps.mentari.services.blog import handle_blog_request
                result = handle_blog_request(original, user)
                return self._format_response(result)

            # 14. Analytics / tracking
            if any(k in msg for k in ["log", "track", "stats"]):
                result = self.handle_analytics(original, user)
                return self._format_response(result)

            # 15. Fallback help
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

    def get_help_message(self):
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
                '<em>Try "Molar mass of H2O" or "Quiz on atoms"</em>'
                "</div>"
            ),
            "card": {
                "type": "help",
                "suggestions": [
                    "Start a quiz",
                    "Molar mass of H2O",
                    "Show recent threads", 
                    "How am I doing?",
                    "Solve x^2 - 4 = 0"
                ]
            }
        }