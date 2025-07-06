from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.mentari.models import EssaySubmission
from apps.mentari.services.essay_feedback import EssayFeedbackService
import json

@csrf_exempt
def essay_feedback_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "")
        feedback = EssayFeedbackService().analyze(text)
        EssaySubmission.objects.create(text=text, feedback=feedback)
        return JsonResponse({"feedback": feedback})
    return render(request, "mentari/essay_feedback.html")
