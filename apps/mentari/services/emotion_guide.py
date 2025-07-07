import random
from datetime import datetime

class EmotionGuideService:
    """Enhanced social-emotional learning and mental wellness support"""
    
    def __init__(self):
        self.stress_levels = ["low", "moderate", "high", "overwhelming"]
        self.emotions = ["happy", "sad", "anxious", "excited", "frustrated", "confident", "overwhelmed"]
    
    def mood_check_in(self, mood, stress_level, situation=""):
        """Process mood check-in and provide support"""
        response = {
            "acknowledgment": self._acknowledge_feeling(mood),
            "validation": self._validate_emotion(mood, stress_level),
            "strategies": self._get_coping_strategies(mood, stress_level),
            "follow_up": self._suggest_follow_up(stress_level)
        }
        
        if situation:
            response["situation_advice"] = self._situation_specific_advice(mood, situation)
        
        return response
    
    def _acknowledge_feeling(self, mood):
        """Acknowledge the student's current emotional state"""
        acknowledgments = {
            "happy": "It's wonderful that you're feeling positive! 😊",
            "sad": "I hear that you're feeling sad right now. That's okay - all feelings are valid. 💙",
            "anxious": "Feeling anxious can be really challenging. You're not alone in this. 🤗",
            "excited": "Your excitement is contagious! It's great to feel enthusiastic! ⭐",
            "frustrated": "Frustration can be tough to handle. Let's work through this together. 💪",
            "confident": "Confidence looks good on you! Keep that positive energy flowing! ✨",
            "overwhelmed": "Feeling overwhelmed is completely understandable. Let's break things down. 🌱"
        }
        return acknowledgments.get(mood.lower(), "Thank you for sharing how you're feeling. Your emotions matter.")
    
    def _validate_emotion(self, mood, stress_level):
        """Provide emotional validation"""
        if stress_level in ["high", "overwhelming"]:
            return "What you're experiencing sounds really difficult. It takes courage to acknowledge when things feel tough."
        elif mood.lower() in ["sad", "anxious", "frustrated"]:
            return "These feelings are a normal part of the human experience. It's okay to not be okay sometimes."
        else:
            return "It's important to recognize and appreciate these positive feelings too."
    
    def _get_coping_strategies(self, mood, stress_level):
        """Provide appropriate coping strategies"""
        strategies = []
        
        if stress_level == "overwhelming":
            strategies.extend([
                "Take 5 deep breaths: in for 4, hold for 4, out for 4",
                "Try the 5-4-3-2-1 grounding technique",
                "Consider talking to a trusted adult, counselor, or friend",
                "Break large tasks into tiny, manageable steps"
            ])
        elif stress_level == "high":
            strategies.extend([
                "Take a 10-minute walk or do light exercise",
                "Practice progressive muscle relaxation",
                "Write down what's worrying you",
                "Use positive self-talk"
            ])
        elif mood.lower() == "anxious":
            strategies.extend([
                "Focus on what you can control",
                "Challenge negative thoughts with evidence",
                "Practice mindfulness or meditation",
                "Talk to someone you trust"
            ])
        elif mood.lower() == "frustrated":
            strategies.extend([
                "Take a break from the frustrating situation",
                "Do something physical to release energy",
                "Practice problem-solving steps",
                "Remember that frustration often means you care"
            ])
        else:
            strategies.extend([
                "Keep a gratitude journal",
                "Share your positive energy with others",
                "Set small, achievable goals",
                "Practice self-compassion"
            ])
        
        return strategies
    
    def _suggest_follow_up(self, stress_level):
        """Suggest appropriate follow-up actions"""
        if stress_level in ["high", "overwhelming"]:
            return "If these feelings persist or get worse, please reach out to a school counselor, trusted adult, or mental health professional."
        else:
            return "Check in with yourself regularly. Your mental health matters as much as your academic success."
    
    def _situation_specific_advice(self, mood, situation):
        """Provide advice based on specific situations"""
        situation_lower = situation.lower()
        
        if "test" in situation_lower or "exam" in situation_lower:
            return "Test anxiety is very common. Try studying in small chunks, get enough sleep, and remember that one test doesn't define you."
        elif "college" in situation_lower or "application" in situation_lower:
            return "College applications can feel overwhelming. Break the process into small steps and remember that there are many paths to success."
        elif "friend" in situation_lower or "social" in situation_lower:
            return "Social situations can be challenging. Remember that healthy relationships involve mutual respect and support."
        elif "family" in situation_lower:
            return "Family dynamics can be complex. Consider having an open, honest conversation or seeking help from a trusted adult."
        else:
            return "Remember that challenges are opportunities for growth. You have the strength to work through this."
    
    def get_mindfulness_exercise(self, time_available=5):
        """Provide quick mindfulness exercises"""
        exercises = {
            1: "Take one deep breath. Breathe in slowly, hold briefly, breathe out slowly.",
            3: "3-Minute Body Scan: Close your eyes and slowly scan from your toes to your head, noticing any tension.",
            5: "5-4-3-2-1 Grounding: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            10: "Loving-Kindness Meditation: Send good wishes to yourself, loved ones, neutral people, and even difficult people."
        }
        
        # Find the best exercise for available time
        available_times = sorted([t for t in exercises.keys() if t <= time_available])
        if available_times:
            chosen_time = max(available_times)
            return f"{chosen_time}-Minute Exercise: {exercises[chosen_time]}"
        else:
            return exercises[1]  # Default to 1-minute exercise
    
    def goal_setting_support(self, goal_type="academic"):
        """Help students set and achieve goals"""
        frameworks = {
            "academic": {
                "specific": "What exactly do you want to achieve? (e.g., 'Improve my math grade to a B+')",
                "measurable": "How will you track progress? (e.g., quiz scores, assignment grades)",
                "achievable": "Is this realistic given your current situation and timeline?",
                "relevant": "How does this connect to your larger academic or life goals?",
                "time_bound": "When do you want to achieve this by?"
            },
            "personal": {
                "specific": "What personal skill or habit do you want to develop?",
                "measurable": "How will you know you're making progress?",
                "achievable": "What small steps can you take starting today?",
                "relevant": "Why is this important to you right now?",
                "time_bound": "What's a realistic timeline for this change?"
            }
        }
        
        return frameworks.get(goal_type, frameworks["academic"])
