# apps/mentari/views.py

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from apps.mentari.services.brain import MentariBrain

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """API endpoint for chat interactions with Mentari"""
    
    def post(self, request):
        try:
            # Parse the request
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({
                    'text': '<div class="alert alert-warning">Please enter a message</div>'
                })
            
            # Get or create session data
            session = request.session
            if 'mentari_context' not in session:
                session['mentari_context'] = {}
            
            # Initialize brain
            brain = MentariBrain()
            
            # Get response from brain
            user = request.user if request.user.is_authenticated else None
            response = brain.respond(message, user=user, session=session)
            
            # Ensure response is properly formatted
            if isinstance(response, str):
                response = {"text": response}
            elif not isinstance(response, dict):
                response = {"text": str(response)}
            
            # Add conversation stats if user is authenticated
            if user and user.is_authenticated:
                response['conversation_stats'] = self.get_conversation_stats(user, session)
            
            # Save session
            request.session.modified = True
            
            # Log the interaction
            logger.info(f"Chat interaction - User: {user.username if user else 'Anonymous'}, Message length: {len(message)}")
            
            return JsonResponse(response)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'text': '<div class="alert alert-danger">Invalid request format</div>'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Chat API error: {str(e)}", exc_info=True)
            return JsonResponse({
                'text': (
                    '<div class="alert alert-danger">'
                    f'An error occurred: {str(e)}<br>'
                    '<small>Please try again or contact support if this persists.</small>'
                    '</div>'
                )
            }, status=500)
    
    def get_conversation_stats(self, user, session):
        """Get conversation statistics for the user"""
        try:
            stats = {
                'current_session': session.get('mentari_context', {}).get('interaction_count', 0) + 1
            }
            
            # Update session interaction count
            if 'mentari_context' not in session:
                session['mentari_context'] = {}
            session['mentari_context']['interaction_count'] = stats['current_session']
            
            # Add database stats if available
            try:
                from apps.analytics.models import Event
                from datetime import datetime, timedelta
                
                total_interactions = Event.objects.filter(user=user).count()
                if total_interactions:
                    stats['total_interactions'] = total_interactions
                
                recent_interactions = Event.objects.filter(
                    user=user,
                    timestamp__gte=datetime.now() - timedelta(days=7)
                ).count()
                if recent_interactions:
                    stats['weekly_interactions'] = recent_interactions
                    
            except ImportError:
                # Analytics not available
                pass
            except Exception:
                # Database error, continue without stats
                pass
            
            return stats
            
        except Exception as e:
            logger.warning(f"Error getting conversation stats: {str(e)}")
            return {'current_session': 1}


# For older Django versions or function-based views
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """Function-based view for chat API"""
    view = ChatAPIView()
    return view.post(request)


# Regular view for the chat interface
@login_required
def chat_view(request):
    """Render the chat interface"""
    from django.shortcuts import render
    
    context = {
        'user': request.user,
        'page_title': 'Mentari AI Assistant'
    }
    
    return render(request, 'mentari/chat.html', context)


# Health check endpoint
def health_check(request):
    """Simple health check for the chat system"""
    try:
        brain = MentariBrain()
        test_response = brain.respond("hello", user=None, session={})
        
        return JsonResponse({
            'status': 'healthy',
            'brain_responsive': bool(test_response),
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': str(datetime.now())
        }, status=500)