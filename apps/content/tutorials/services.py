# apps/tutorials/services.py
from .models import Tutorial, TutorialStep, UserTutorialProgress
from django.db.models import Count, Q

class TutorialService:
    def recommend(self, topic):
        """Recommend tutorials based on topic"""
        tutorials = Tutorial.objects.filter(
            Q(title__icontains=topic) | Q(description__icontains=topic),
            is_published=True
        ).annotate(
            step_count=Count('steps')
        )[:5]
        
        return list(tutorials.values('title', 'slug', 'description', 'difficulty', 'step_count'))
    
    def get_tutorial_progress(self, user, tutorial_slug):
        """Get user's progress on a tutorial"""
        if not user or not user.is_authenticated:
            return {'completed_steps': 0, 'total_steps': 0}
        
        try:
            tutorial = Tutorial.objects.get(slug=tutorial_slug)
            total_steps = tutorial.steps.count()
            
            completed_steps = UserTutorialProgress.objects.filter(
                user=user,
                tutorial=tutorial,
                completed=True
            ).count()
            
            return {
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'percentage': int((completed_steps / total_steps * 100) if total_steps > 0 else 0)
            }
        except Tutorial.DoesNotExist:
            return {'completed_steps': 0, 'total_steps': 0}
    
    def mark_step_complete(self, user, tutorial_slug, step_order):
        """Mark a tutorial step as complete"""
        if not user or not user.is_authenticated:
            return False
        
        try:
            tutorial = Tutorial.objects.get(slug=tutorial_slug)
            step = tutorial.steps.get(order=step_order)
            
            UserTutorialProgress.objects.update_or_create(
                user=user,
                tutorial=tutorial,
                step=step,
                defaults={'completed': True}
            )
            
            return True
        except:
            return False
    
    def get_recommended_next(self, user):
        """Get recommended next tutorial for user"""
        if not user or not user.is_authenticated:
            # Return beginner tutorials for anonymous users
            return Tutorial.objects.filter(
                difficulty='beginner',
                is_published=True
            ).first()
        
        # Get completed tutorials
        completed = UserTutorialProgress.objects.filter(
            user=user,
            completed=True
        ).values_list('tutorial_id', flat=True).distinct()
        
        # Find next uncompleted tutorial
        next_tutorial = Tutorial.objects.filter(
            is_published=True
        ).exclude(id__in=completed).order_by('order').first()
        
        return next_tutorial