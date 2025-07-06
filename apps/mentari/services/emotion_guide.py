import random

class EmotionGuideService:
    def __init__(self):
        self.response_patterns = {
            "growth_mindset": [
                "Mistakes aren't failures—they're signals you're trying something bold.",
                "Each challenge is a chance to stretch your thinking. Let’s keep going.",
                "Your effort matters more than the outcome. Science is built on persistence.",
                "What did this experience teach you about your process?",
                "This is how real understanding is built—layer by layer."
            ],
            "frustration": [
                "Frustration often shows you're close to a breakthrough.",
                "Let’s slow down—what part feels most overwhelming?",
                "Even scientists hit walls. What’s the first small step forward?",
                "You don’t have to figure it all out right now. Let's breathe and reset."
            ],
            "curiosity": [
                "That question shows your brain is making connections. Explore it!",
                "Curiosity is the engine behind every discovery.",
                "What makes you wonder about this?",
                "Follow that thread—what might you find if you keep pulling it?"
            ],
            "confusion": [
                "Confusion is data—what's blurry is often what's important.",
                "Let’s sort through this together. Where should we start?",
                "Learning means feeling uncertain sometimes. You’re not alone in this.",
                "What questions do you have so far?"
            ],
            "confidence": [
                "That clarity you’re feeling? That’s earned.",
                "You're starting to own this understanding. Celebrate that!",
                "It feels good when things click—what got you here?",
                "Let's build from this momentum. What’s next?"
            ]
        }

        self.keyword_map = {
            "why": "curiosity",
            "how": "curiosity",
            "wonder": "curiosity",
            "confused": "confusion",
            "unclear": "confusion",
            "frustrated": "frustration",
            "stuck": "frustration",
            "success": "confidence",
            "worked": "confidence",
            "achieved": "confidence",
            "mistake": "growth_mindset",
            "failure": "growth_mindset",
            "try": "growth_mindset"
        }

    def analyze_emotion(self, message):
        lowered = message.lower()
        for keyword, emotion in self.keyword_map.items():
            if keyword in lowered:
                return emotion
        return "growth_mindset"

    def generate_response(self, emotion):
        return random.choice(self.response_patterns.get(emotion, self.response_patterns["growth_mindset"]))
