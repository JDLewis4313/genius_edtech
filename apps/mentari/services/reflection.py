# apps/mentari/services/reflection.py
"""
Reflection Service - Basic Implementation
"""

class ReflectionService:
    """Basic reflection and journaling service"""
    
    def __init__(self, user=None, session=None):
        self.user = user
        self.session = session
    
    def handle_reflection_request(self, message):
        """Handle reflection requests"""
        return (
            "<div class='alert alert-info'>"
            "<strong>💭 Reflection Space</strong><br>"
            "Your thoughts are valuable! Reflection features are being prepared.<br>"
            "Try sharing what you're learning or how you're feeling about your studies."
            "</div>"
        )
    
    def get_reflection_prompt(self):
        """Get a reflection prompt"""
        prompts = [
            "What did you learn today that surprised you?",
            "How do you feel about your progress this week?",
            "What topic would you like to explore more deeply?",
            "What study strategy has been working well for you?"
        ]
        import random
        return (
            "<div class='alert alert-primary'>"
            f"<strong>💭 Reflection Prompt:</strong><br>"
            f"{random.choice(prompts)}"
            "</div>"
        )
    
    def get_recent_reflections(self):
        """Get recent reflections (mock data)"""
        return []  # Return empty list for now

