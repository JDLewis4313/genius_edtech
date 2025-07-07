from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.services.advising import AdvisingService
import json

@csrf_exempt
def advising_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', 'checklist')
            
            service = AdvisingService()
            
            if action == 'fafsa_timeline':
                result = service.get_fafsa_timeline()
            elif action == 'efc_estimate':
                result = service.calculate_efc_estimate(
                    data.get('parent_income', 0),
                    data.get('student_income', 0),
                    data.get('assets', 0),
                    data.get('family_size', 4)
                )
            elif action == 'checklist':
                grade = data.get('grade_level', 'senior')
                result = service.get_application_checklist(grade)
            elif action == 'scholarships':
                result = service.scholarship_search_tips()
            else:
                result = {"error": "Unknown action"}
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'mentari/advising.html')
