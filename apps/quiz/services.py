# apps/quiz/services.py
from .models import Topic, Question, QuizAttempt, Module
from django.db.models import Count, Avg

class QuizService:
    def get_topic_id_by_name(self, topic_name):
        """Get topic ID by name (case-insensitive partial match)"""
        try:
            # Try exact match first
            topic = Topic.objects.filter(title__iexact=topic_name).first()
            if topic:
                return topic.id
            
            # Try partial match
            topic = Topic.objects.filter(title__icontains=topic_name).first()
            return topic.id if topic else None
        except:
            return None
    
    def get_all_topics(self):
        """Get all available topics with question counts"""
        topics = Topic.objects.annotate(
            question_count=Count('questions')
        ).filter(question_count__gt=0).order_by('module__order', 'order')
        
        return list(topics.values('id', 'title', 'module__name', 'question_count'))
    
    def get_questions(self, topic_id, limit=5):
        """Get questions for a specific topic"""
        try:
            questions = Question.objects.filter(
                topic_id=topic_id
            ).order_by('?')[:limit]  # Random order
            
            return list(questions.values('id', 'text', 'difficulty'))
        except:
            return []
    
    def get_question_with_choices(self, question_id):
        """Get a question with its choices"""
        try:
            question = Question.objects.get(id=question_id)
            choices = question.choices.all().values('id', 'text', 'is_correct')
            
            return {
                'question': question.text,
                'explanation': question.explanation,
                'choices': list(choices)
            }
        except Question.DoesNotExist:
            return None
    
    def submit_answer(self, user, question_id, choice_id):
        """Check answer and return feedback"""
        try:
            question = Question.objects.get(id=question_id)
            choice = question.choices.get(id=choice_id)
            
            is_correct = choice.is_correct
            
            # Log attempt if user is authenticated
            if user and user.is_authenticated:
                QuizAttempt.objects.create(
                    user=user,
                    topic=question.topic,
                    score=100 if is_correct else 0
                )
            
            return {
                'correct': is_correct,
                'explanation': question.explanation
            }
            
        except:
            return {'correct': False, 'explanation': 'Error checking answer.'}
    
    def get_user_stats(self, user):
        """Get user's quiz statistics"""
        if not user or not user.is_authenticated:
            return {}
        
        attempts = QuizAttempt.objects.filter(user=user)
        
        stats = attempts.aggregate(
            total_attempts=Count('id'),
            average_score=Avg('score')
        )
        
        # Topics attempted
        topics_attempted = attempts.values_list('topic__title', flat=True).distinct()
        
        return {
            'total_attempts': stats['total_attempts'] or 0,
            'average_score': round(stats['average_score'] or 0, 1),
            'topics_attempted': list(topics_attempted)[:5]
        }