from django.shortcuts import render
from apps.mentari.services.advising import AdvisingChecklistService

def advising_view(request):
    checklist = AdvisingChecklistService().get_checklist()
    return render(request, "mentari/advising.html", {"checklist": checklist})
