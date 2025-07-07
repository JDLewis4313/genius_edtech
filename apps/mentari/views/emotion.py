from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.services.emotion_guide import EmotionGuideService
import json

@csrf_exempt
def emotion_support_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood = data.get('mood', 'neutral')
            stress_level = data.get('stress_level', 'low')
            situation = data.get('situation', '')
            
            service = EmotionGuideService()
            result = service.mood_check_in(mood, stress_level, situation)
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'mentari/emotion.html')
