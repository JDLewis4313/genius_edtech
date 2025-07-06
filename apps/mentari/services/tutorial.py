# apps/mentari/services/tutorial.py
from apps.tutorials.services import TutorialService
from django.urls import reverse

def handle_tutorial_request(message, user=None):
    """Handle tutorial requests"""
    try:
        service = TutorialService()
        
        # Extract topic
        words = message.lower().split()
        topic_words = [w for w in words if w not in ['tutorial', 'learn', 'teach', 'about', 'me']]
        topic = ' '.join(topic_words) if topic_words else 'chemistry'
        
        tutorials = service.recommend(topic)
        
        if tutorials:
            text = f"📚 **Tutorials on {topic}:**\n\n"
            for t in tutorials:
                text += f"• **{t['title']}**\n"
                text += f"  Difficulty: {t['difficulty']} | Steps: {t['step_count']}\n"
                text += f"  {t['description']}\n\n"
            
            return {
                "text": text,
                "card": {
                    "type": "tutorial_list",
                    "tutorials": tutorials
                }
            }
        else:
            return {
                "text": f"No tutorials found for '{topic}'. Browse all tutorials:",
                "redirect_url": "/tutorials/"
            }
            
    except Exception as e:
        return {"text": f"Tutorial error: {str(e)}"}