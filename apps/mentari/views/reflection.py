from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.models import ReflectionEntry
import json

@csrf_exempt
def submit_reflection_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "").strip()
        if message:
            ReflectionEntry.objects.create(message=message)
            return JsonResponse({"status": "success", "message": "Reflection saved."})
        return JsonResponse({"status": "error", "message": "Empty reflection."}, status=400)
