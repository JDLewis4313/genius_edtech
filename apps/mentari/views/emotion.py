from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.models import ConversationEntry
from apps.mentari.services.emotion_guide import EmotionGuideService
import json

guide = EmotionGuideService()

@csrf_exempt
def emotion_chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "")
        emotion = guide.analyze_emotion(message)
        bot_response = guide.generate_response(emotion)

        ConversationEntry.objects.create(
            user_message=message,
            bot_response=bot_response,
            emotion=emotion
        )

        return JsonResponse({
            "response": bot_response,
            "conversation_stats": {
                "total_interactions": ConversationEntry.objects.count(),
                "growth_indicators": ConversationEntry.objects.filter(emotion="growth_mindset").count(),
                "support_needed": ConversationEntry.objects.filter(emotion__in=["frustration", "confusion"]).count()
            }
        })
    return render(request, "mentari/chat.html")
