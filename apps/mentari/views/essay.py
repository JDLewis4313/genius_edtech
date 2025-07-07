from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.services.essay_feedback import EssayFeedbackService
import json

@csrf_exempt
def essay_feedback_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            essay_type = data.get('essay_type', 'personal_statement')
            
            service = EssayFeedbackService()
            result = service.analyze_college_essay(text, essay_type)
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'mentari/essay_feedback.html')
