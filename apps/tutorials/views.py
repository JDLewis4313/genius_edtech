from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from collections import Counter

from apps.tutorials.models import Tutorial, TutorialCategory, TutorialStep, UserTutorialProgress
from apps.interactions.models import Comment, Reaction
from django.contrib.contenttypes.models import ContentType
from apps.analytics.models import Event

REACTION_CHOICES = [
    ("like", "👍"),
    ("fire", "🔥"),
    ("wow", "🤯"),
    ("rocket", "🚀"),
]

def tutorial_list(request, category_slug=None):
    tutorials = Tutorial.objects.filter(is_published=True)
    categories = TutorialCategory.objects.all()
    current_category = None

    if category_slug:
        current_category = get_object_or_404(TutorialCategory, slug=category_slug)
        tutorials = tutorials.filter(category=current_category)

    search_query = request.GET.get('q')
    if search_query:
        tutorials = tutorials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(technologies__icontains=search_query)
        )

    difficulty = request.GET.get('difficulty')
    if difficulty in ['beginner', 'intermediate', 'advanced']:
        tutorials = tutorials.filter(difficulty=difficulty)

    user_progress = {}
    if request.user.is_authenticated:
        progress_records = UserTutorialProgress.objects.filter(
            user=request.user,
            tutorial__in=tutorials
        ).select_related('tutorial')

        for progress in progress_records:
            user_progress[progress.tutorial.id] = {
                'is_completed': progress.is_completed,
                'progress_percentage': progress.get_progress_percentage()
            }

    return render(request, 'tutorials/tutorial_list.html', {
        'tutorials': tutorials,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
        'user_progress': user_progress,
        'total_count': tutorials.count()
    })

def tutorial_detail(request, slug):
    tutorial = get_object_or_404(Tutorial, slug=slug, is_published=True)
    steps = tutorial.steps.all().order_by('order')
    content_type = ContentType.objects.get_for_model(tutorial)

    # Log tutorial start
    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='tutorial_start',
            path=request.path,
            meta={'tutorial_id': tutorial.id, 'title': tutorial.title}
        )

    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        reaction = request.POST.get("reaction")

        if content:
            Comment.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=tutorial.id,
                content=content
            )
            return redirect(request.path)

        if reaction:
            Reaction.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=tutorial.id,
                reaction=reaction
            )
            return redirect(request.path)

    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=tutorial.id
    ).order_by("-created_at")

    reactions = Reaction.objects.filter(
        content_type=content_type,
        object_id=tutorial.id
    )

    reaction_summary = Counter(r.reaction for r in reactions)

    user_progress = None
    if request.user.is_authenticated:
        user_progress, _ = UserTutorialProgress.objects.get_or_create(
            user=request.user,
            tutorial=tutorial
        )

    related_tutorials = Tutorial.objects.filter(
        category=tutorial.category,
        is_published=True
    ).exclude(id=tutorial.id)[:3]

    return render(request, 'tutorials/tutorial_detail.html', {
        'tutorial': tutorial,
        'steps': steps,
        'user_progress': user_progress,
        'related_tutorials': related_tutorials,
        'total_steps': steps.count(),
        'completed_steps': len(user_progress.completed_steps) if user_progress else 0,
        'progress_percentage': user_progress.get_progress_percentage() if user_progress else 0,
        'comments': comments,
        'reactions': reactions,
        'reaction_summary': reaction_summary,
        'REACTION_CHOICES': REACTION_CHOICES
    })

@login_required
@require_http_methods(["POST"])
def mark_step_complete(request, slug, step_id):
    tutorial = get_object_or_404(Tutorial, slug=slug)
    step = get_object_or_404(TutorialStep, tutorial=tutorial, id=step_id)

    progress, _ = UserTutorialProgress.objects.get_or_create(
        user=request.user,
        tutorial=tutorial
    )

    completed_steps = progress.completed_steps or []
    if step_id not in completed_steps:
        completed_steps.append(step_id)
        progress.completed_steps = completed_steps
        if len(completed_steps) == tutorial.steps.count():
            progress.mark_completed()
            # 🔍 Log completion
            Event.objects.create(
                user=request.user,
                event_type='tutorial_complete',
                path=request.path,
                meta={'tutorial_id': tutorial.id, 'title': tutorial.title}
            )
        progress.save()

    return JsonResponse({
        'success': True,
        'progress_percentage': progress.get_progress_percentage(),
        'is_completed': progress.is_completed
    })

def get_tutorial_template(request, slug, template_type='starter'):
    return redirect('code_editor:get_tutorial_template', slug=slug, template_type=template_type)

def save_tutorial_progress(request, slug):
    return redirect('code_editor:save_tutorial_progress', slug=slug)

def tutorial_search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    tutorials = Tutorial.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        is_published=True
    )[:5]

    results = [{
        'title': t.title,
        'slug': t.slug,
        'category': t.category.name,
        'difficulty': t.get_difficulty_display(),
        'url': f'/tutorials/tutorial/{t.slug}/'
    } for t in tutorials]

    return JsonResponse({'results': results})

@login_required
def my_tutorials(request):
    progress_records = UserTutorialProgress.objects.filter(
        user=request.user
    ).select_related('tutorial', 'tutorial__category').order_by('-last_accessed')

    completed = progress_records.filter(is_completed=True)
    in_progress = progress_records.filter(is_completed=False)

    completed_categories = completed.values_list('tutorial__category', flat=True)

    recommended = Tutorial.objects.filter(
        category__in=completed_categories,
        is_published=True
    ).exclude(
        id__in=progress_records.values_list('tutorial', flat=True)
    )[:3]

    return render(request, 'tutorials/my_tutorials.html', {
        'completed': completed,
        'in_progress': in_progress,
        'recommended': recommended,
        'total_completed': completed.count(),
        'total_in_progress': in_progress.count()
    })
