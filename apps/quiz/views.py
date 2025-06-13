from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Module, Topic, Question, Choice, UserProgress

def tutorials(request):
    modules = Module.objects.all().prefetch_related('topics')
    return render(request, 'quiz/tutorials.html', {'modules': modules})

def quiz(request):
    modules = Module.objects.all().prefetch_related('topics')
    return render(request, 'quiz/quiz.html', {'modules': modules})

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    questions = Question.objects.filter(topic=topic)
    return render(request, 'quiz/topic_detail.html', {
        'topic': topic,
        'questions': questions
    })

def get_topics(request, module_id):
    """API endpoint to get topics for a module"""
    module = get_object_or_404(Module, id=module_id)
    topics = Topic.objects.filter(module=module)
    
    # Format topics for JSON response
    topics_data = []
    for topic in topics:
        question_count = Question.objects.filter(topic=topic).count()
        
        # Get the most common difficulty from questions, or default to 'medium'
        difficulty = 'medium'  # Default value
        if question_count > 0:
            # Try to determine difficulty from questions
            difficulty_counts = {}
            for question in Question.objects.filter(topic=topic):
                if question.difficulty in difficulty_counts:
                    difficulty_counts[question.difficulty] += 1
                else:
                    difficulty_counts[question.difficulty] = 1
            
            if difficulty_counts:
                # Find the most common difficulty
                difficulty = max(difficulty_counts.items(), key=lambda x: x[1])[0]
        
        topics_data.append({
            'id': topic.id,
            'title': topic.title,
            'description': topic.description,
            'difficulty': difficulty,  # Use the calculated difficulty
            'question_count': question_count
        })
    
    return JsonResponse({
        'module': {
            'id': module.id,
            'title': module.title,
            'description': module.description
        },
        'topics': topics_data
    })

def get_quiz_questions(request, topic_id):
    """API endpoint to get questions for a topic"""
    topic = get_object_or_404(Topic, id=topic_id)
    questions = Question.objects.filter(topic=topic).prefetch_related('choices')
    
    # Calculate difficulty based on questions
    difficulty = 'medium'  # Default
    if questions:
        difficulty_counts = {}
        for question in questions:
            if question.difficulty in difficulty_counts:
                difficulty_counts[question.difficulty] += 1
            else:
                difficulty_counts[question.difficulty] = 1
        
        if difficulty_counts:
            difficulty = max(difficulty_counts.items(), key=lambda x: x[1])[0]
    
    # Format questions for JSON response
    questions_data = []
    for question in questions:
        choices = []
        for choice in question.choices.all():
            choices.append({
                'id': choice.id,
                'text': choice.text,
                'is_correct': choice.is_correct
            })
        
        questions_data.append({
            'id': question.id,
            'text': question.text,
            'explanation': question.explanation,
            'choices': choices
        })
    
    return JsonResponse({
        'topic': {
            'id': topic.id,
            'title': topic.title,
            'module': topic.module.title,
            'difficulty': difficulty  # Use calculated difficulty
        },
        'questions': questions_data
    })

@login_required
def take_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    questions = Question.objects.filter(topic=topic).prefetch_related('choices')
    
    return render(request, 'quiz/take_quiz.html', {
        'topic': topic,
        'questions': questions
    })

@login_required
def submit_score(request):
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        score = request.POST.get('score')
        
        topic = get_object_or_404(Topic, id=topic_id)
        
        # Create or update user progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
            defaults={'module': topic.module}
        )
        
        progress.score = score
        progress.completed = True
        progress.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

def quiz_results(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.user.is_authenticated:
        try:
            progress = UserProgress.objects.get(user=request.user, topic=topic)
        except UserProgress.DoesNotExist:
            progress = None
    else:
        progress = None
    
    return render(request, 'quiz/quiz_results.html', {
        'topic': topic,
        'progress': progress
    })