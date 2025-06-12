from django.shortcuts import render
from .models import Module, Topic, Question

def tutorials(request):
    return render(request, 'quiz/tutorials.html')

def quiz(request):
    modules = Module.objects.all().prefetch_related('topics')
    return render(request, 'quiz/quiz.html', {'modules': modules})
