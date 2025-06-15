# apps/tutorials/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from .models import Tutorial, TutorialCategory, TutorialStep, UserTutorialProgress
import json

def tutorial_list(request, category_slug=None):
    """List all tutorials, optionally filtered by category"""
    tutorials = Tutorial.objects.filter(is_published=True)
    categories = TutorialCategory.objects.all()
    current_category = None
    
    # Filter by category if provided
    if category_slug:
        current_category = get_object_or_404(TutorialCategory, slug=category_slug)
        tutorials = tutorials.filter(category=current_category)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        tutorials = tutorials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(technologies__icontains=search_query)
        )
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty in ['beginner', 'intermediate', 'advanced']:
        tutorials = tutorials.filter(difficulty=difficulty)
    
    # Get user progress if authenticated
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
    
    context = {
        'tutorials': tutorials,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
        'user_progress': user_progress,
        'total_count': tutorials.count()
    }
    
    return render(request, 'tutorials/tutorial_list.html', context)

def tutorial_detail(request, slug):
    """Display a single tutorial with all its steps"""
    tutorial = get_object_or_404(Tutorial, slug=slug, is_published=True)
    steps = tutorial.steps.all().order_by('order')
    
    # Get or create user progress if authenticated
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserTutorialProgress.objects.get_or_create(
            user=request.user,
            tutorial=tutorial
        )
    
    # Get related tutorials
    related_tutorials = Tutorial.objects.filter(
        category=tutorial.category,
        is_published=True
    ).exclude(id=tutorial.id)[:3]
    
    context = {
        'tutorial': tutorial,
        'steps': steps,
        'user_progress': user_progress,
        'related_tutorials': related_tutorials,
        'total_steps': steps.count(),
        'completed_steps': len(user_progress.completed_steps) if user_progress else 0,
        'progress_percentage': user_progress.get_progress_percentage() if user_progress else 0
    }
    
    return render(request, 'tutorials/tutorial_detail.html', context)

@login_required
@require_http_methods(["POST"])
def mark_step_complete(request, slug, step_id):
    """Mark a tutorial step as completed"""
    tutorial = get_object_or_404(Tutorial, slug=slug)
    step = get_object_or_404(TutorialStep, tutorial=tutorial, id=step_id)
    
    progress, created = UserTutorialProgress.objects.get_or_create(
        user=request.user,
        tutorial=tutorial
    )
    
    # Add step to completed steps if not already there
    completed_steps = progress.completed_steps or []
    if step_id not in completed_steps:
        completed_steps.append(step_id)
        progress.completed_steps = completed_steps
        
        # Check if all steps are completed
        if len(completed_steps) == tutorial.steps.count():
            progress.mark_completed()
        
        progress.save()
    
    return JsonResponse({
        'success': True,
        'progress_percentage': progress.get_progress_percentage(),
        'is_completed': progress.is_completed
    })

def get_tutorial_template(request, slug, template_type='starter'):
    """Redirect to code editor's get_tutorial_template"""
    return redirect('code_editor:get_tutorial_template', slug=slug, template_type=template_type)

def save_tutorial_progress(request, slug):
    """Redirect to code editor's save_tutorial_progress"""
    return redirect('code_editor:save_tutorial_progress', slug=slug)

def tutorial_search_api(request):
    """API endpoint for tutorial search suggestions"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    tutorials = Tutorial.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query),
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
    """Show user's tutorial progress"""
    progress_records = UserTutorialProgress.objects.filter(
        user=request.user
    ).select_related('tutorial', 'tutorial__category').order_by('-last_accessed')
    
    # Separate completed and in-progress
    completed = progress_records.filter(is_completed=True)
    in_progress = progress_records.filter(is_completed=False)
    
    # Get tutorial recommendations
    completed_categories = completed.values_list('tutorial__category', flat=True)
    recommended = Tutorial.objects.filter(
        category__in=completed_categories,
        is_published=True
    ).exclude(
        id__in=progress_records.values_list('tutorial', flat=True)
    )[:3]
    
    context = {
        'completed': completed,
        'in_progress': in_progress,
        'recommended': recommended,
        'total_completed': completed.count(),
        'total_in_progress': in_progress.count()
    }
    
    return render(request, 'tutorials/my_tutorials.html', context)