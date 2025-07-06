# apps/mentari/views/chat.py
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.mentari.services.brain import MentariBrain
from apps.analytics.services import AnalyticsService
import json

def chat_page_view(request):
    """Render the chat interface"""
    return render(request, "mentari/chat.html", {
        'user': request.user
    })

@csrf_exempt
def mentari_chat_view(request):
    """Handle chat API requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()
        
        if not message:
            return JsonResponse({'response': 'Please enter a message.'})
        
        user = request.user if request.user.is_authenticated else None
        
        # Log the interaction
        if user:
            analytics = AnalyticsService()
            analytics.log_event(
                user=user,
                event_type='mentari_chat',
                metadata={'message_length': len(message)}
            )
        
        # Get response from brain - PASS SESSION HERE
        brain = MentariBrain()
        result = brain.respond(message, user, request.session)

        # Normalize response
        if isinstance(result, str):
            response_text = result
            card = None
            redirect_url = None
        else:
            response_text = result.get("text") or result.get("response") or "I'm thinking..."
            card = result.get("card")
            redirect_url = result.get("redirect_url")

        # Track conversation stats
        session_key = f"mentari_stats_{request.session.session_key}"
        stats = request.session.get(session_key, {
            'total_interactions': 0,
            'topics_discussed': []
        })
        
        stats['total_interactions'] += 1
        
        # Track topics
        topic_keywords = ['math', 'chemistry', 'quiz', 'code', 'blog', 'forum']
        for keyword in topic_keywords:
            if keyword in message.lower() and keyword not in stats['topics_discussed']:
                stats['topics_discussed'].append(keyword)
        
        request.session[session_key] = stats
        
        # Build response
        response_data = {
            'response': response_text,
            'conversation_stats': {
                'total_interactions': stats['total_interactions'],
                'growth_indicators': f"↑ {len(stats['topics_discussed'])} topics explored",
                'support_needed': 'low' if stats['total_interactions'] < 10 else 'moderate'
            }
        }
        
        # Add optional fields if present
        if card:
            response_data['card'] = card
        if redirect_url:
            response_data['redirect_url'] = redirect_url
        
        # Ensure session is saved
        request.session.modified = True
        
        
        # Add conversation history for authenticated users
        if user and user.is_authenticated:
            try:
                from apps.mentari.services.learning_brain import LearningContext
                context = LearningContext(user.id)
                recent_history = context.context.get('conversation_history', [])[-3:]
                if recent_history:
                    response_data['conversation_summary'] = {
                        'recent_topics': list(set([h.get('topic') for h in recent_history if h.get('topic')])),
                        'last_interaction': recent_history[-1]['timestamp'] if recent_history else None,
                        'total_interactions': len(context.context.get('conversation_history', []))
                    }
            except Exception as e:
                logger.error(f"Failed to load conversation summary: {e}")

        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'response': 'Invalid message format.'}, status=400)
    except Exception as e:
        print(f"Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'response': 'I encountered an error. Please try again.',
            'error': str(e) if request.user.is_staff else None
        }, status=500)