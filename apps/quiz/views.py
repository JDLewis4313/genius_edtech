from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Module, Topic, Question, Choice, UserProgress
from apps.interactions.models import Comment, Reaction
from django.contrib.contenttypes.models import ContentType
from collections import Counter
from apps.analytics.models import Event

REACTION_CHOICES = [
    ("like", "👍"),
    ("fire", "🔥"),
    ("wow", "🤯"),
    ("rocket", "🚀"),
]

def quiz(request):
    modules = Module.objects.all().prefetch_related('topics')
    return render(request, 'quiz/quiz.html', {'modules': modules})

def quiz_detail(request, module_slug):
    module = get_object_or_404(Module, slug=module_slug)
    content_type = ContentType.objects.get_for_model(module)

    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        reaction = request.POST.get("reaction")

        if content:
            Comment.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=module.id,
                content=content
            )
            return redirect(request.path)

        if reaction:
            Reaction.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=module.id,
                reaction=reaction
            )
            return redirect(request.path)

    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=module.id
    ).order_by("-created_at")

    reactions = Reaction.objects.filter(
        content_type=content_type,
        object_id=module.id
    )

    reaction_summary = Counter(r.reaction for r in reactions)

    return render(request, 'quiz/quiz_detail.html', {
        'module': module,
        'comments': comments,
        'reactions': reactions,
        'reaction_summary': reaction_summary,
        'REACTION_CHOICES': REACTION_CHOICES
    })

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    questions = Question.objects.filter(topic=topic)
    content_type = ContentType.objects.get_for_model(topic)

    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        reaction = request.POST.get("reaction")

        if content:
            Comment.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=topic.id,
                content=content
            )
            return redirect(request.path)

        if reaction:
            Reaction.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=topic.id,
                reaction=reaction
            )
            return redirect(request.path)

    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=topic.id
    ).order_by("-created_at")

    reactions = Reaction.objects.filter(
        content_type=content_type,
        object_id=topic.id
    )

    reaction_summary = Counter(r.reaction for r in reactions)

    return render(request, 'quiz/topic_detail.html', {
        'topic': topic,
        'questions': questions,
        'comments': comments,
        'reactions': reactions,
        'reaction_summary': reaction_summary,
        'REACTION_CHOICES': REACTION_CHOICES
    })

def get_topics(request, module_id):
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)

    topics = Topic.objects.filter(module=module)
    topics_data = []
    for topic in topics:
        question_count = Question.objects.filter(topic=topic).count()
        difficulty = 'medium'
        if question_count > 0:
            difficulty_counts = {}
            for question in Question.objects.filter(topic=topic):
                difficulty_counts[question.difficulty] = difficulty_counts.get(question.difficulty, 0) + 1
            difficulty = max(difficulty_counts.items(), key=lambda x: x[1])[0]
        topics_data.append({
            'id': topic.id,
            'title': topic.title,
            'description': topic.description,
            'difficulty': difficulty,
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
    topic = get_object_or_404(Topic, id=topic_id)
    questions = Question.objects.filter(topic=topic).prefetch_related('choices')

    difficulty = 'medium'
    if questions:
        difficulty_counts = {}
        for question in questions:
            difficulty_counts[question.difficulty] = difficulty_counts.get(question.difficulty, 0) + 1
        if difficulty_counts:
            difficulty = max(difficulty_counts.items(), key=lambda x: x[1])[0]

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
            'difficulty': difficulty
        },
        'questions': questions_data
    })

def take_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    questions = topic.questions.prefetch_related("choices").all()

    if request.method == "POST":
        if request.user.is_authenticated:
            # Save progress or score
            ...
        else:
            # Optionally show a message or skip saving
            pass

    return render(request, "quiz/take_quiz.html", {
        "topic": topic,
        "questions": questions
    })

def submit_score(request):
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        score = request.POST.get('score')
        topic = get_object_or_404(Topic, id=topic_id)
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
            defaults={'module': topic.module}
        )
        progress.score = score
        progress.completed = True
        progress.save()

        # 🔍 Log analytics
        Event.objects.create(
            user=request.user,
            event_type='quiz_complete',
            path=request.path,
            meta={
                'topic': topic.title,
                'module': topic.module.title,
                'score': score
            }
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def quiz_results(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    progress = None
    if request.user.is_authenticated:
        try:
            progress = UserProgress.objects.get(user=request.user, topic=topic)
        except UserProgress.DoesNotExist:
            pass
    return render(request, 'quiz/quiz_results.html', {
        'topic': topic,
        'progress': progress
    })
