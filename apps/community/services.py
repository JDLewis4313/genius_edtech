# apps/community/services.py

from datetime import datetime, timedelta
from django.utils import timezone


class CommunityService:
    """Service for handling community/forum functionality"""
    
    def __init__(self):
        pass
    
    def handle_community_request(self, message, user=None):
        """Main handler for community requests"""
        msg_lower = message.lower()
        
        if "recent" in msg_lower and "thread" in msg_lower:
            return self.get_recent_threads_response()
        elif "popular" in msg_lower:
            return self.get_popular_threads_response()
        elif "boards" in msg_lower:
            return self.get_boards_response()
        else:
            return self.get_community_help_response()
    
    def get_recent_threads_response(self):
        """Get recent threads with proper structure for cards"""
        try:
            threads = self.get_recent_threads()
            return {
                "text": (
                    "<div class='alert alert-info'>"
                    "<strong>💬 Recent Community Threads</strong><br>"
                    "Here are the latest discussions in The Commons:"
                    "</div>"
                ),
                "card": {
                    "type": "thread_list",
                    "threads": threads
                }
            }
        except Exception as e:
            return {
                "text": f"<div class='alert alert-danger'>Could not load recent threads: {str(e)}</div>"
            }
    
    def get_recent_threads(self):
        """Get recent threads - returns list of thread objects"""
        try:
            # Try to import your actual Thread model
            # from apps.community.models import Thread
            # threads = Thread.objects.filter(
            #     is_active=True
            # ).order_by('-last_activity')[:5]
            
            # For now, return mock data with proper structure
            mock_threads = [
                {
                    "id": 1,
                    "title": "Help with Chemistry Quiz - Balancing Equations",
                    "author": "student123",
                    "replies": 8,
                    "last_activity": "2 hours ago",
                    "created_at": timezone.now() - timedelta(hours=2)
                },
                {
                    "id": 2,
                    "title": "Calculus Study Group - Integration Techniques",
                    "author": "mathwiz",
                    "replies": 15,
                    "last_activity": "4 hours ago", 
                    "created_at": timezone.now() - timedelta(hours=4)
                },
                {
                    "id": 3,
                    "title": "FAFSA Application Tips and Deadline Reminders",
                    "author": "advisor_jane",
                    "replies": 12,
                    "last_activity": "1 day ago",
                    "created_at": timezone.now() - timedelta(days=1)
                },
                {
                    "id": 4,
                    "title": "Organic Chemistry Lab Safety Guidelines",
                    "author": "chem_prof",
                    "replies": 6,
                    "last_activity": "2 days ago",
                    "created_at": timezone.now() - timedelta(days=2)
                },
                {
                    "id": 5,
                    "title": "Study Tips for Midterm Exams",
                    "author": "senior_student",
                    "replies": 23,
                    "last_activity": "3 days ago",
                    "created_at": timezone.now() - timedelta(days=3)
                }
            ]
            
            return mock_threads
            
        except Exception as e:
            # Return empty list if there's an error
            return []
    
    def get_popular_threads_response(self):
        """Get popular threads response"""
        return {
            "text": (
                "<div class='alert alert-info'>"
                "🔥 <strong>Popular Discussions</strong><br>"
                "These topics are trending in The Commons! "
                "<a href='/community/' class='btn btn-sm btn-primary'>Join the conversation</a>"
                "</div>"
            ),
            "card": {
                "type": "community_help",
                "actions": [
                    {"text": "View Popular Threads", "url": "/community/popular/"},
                    {"text": "Start New Discussion", "url": "/community/new/"}
                ]
            }
        }
    
    def get_boards_response(self):
        """Get discussion boards response"""
        boards = [
            {"name": "Math & Science", "description": "Questions about STEM subjects"},
            {"name": "Study Groups", "description": "Find study partners"},
            {"name": "Financial Aid", "description": "FAFSA and scholarship help"},
            {"name": "General Discussion", "description": "Everything else"}
        ]
        
        boards_html = "<br>".join([f"• <strong>{board['name']}</strong> - {board['description']}" for board in boards])
        
        return {
            "text": (
                "<div class='alert alert-info'>"
                f"📋 <strong>Available Discussion Boards:</strong><br>{boards_html}"
                "</div>"
            )
        }
    
    def get_community_help_response(self):
        """Get general community help response"""
        return {
            "text": (
                "<div class='alert alert-info'>"
                "Welcome to The Commons - our community discussion space! 💬<br><br>"
                "Here you can:<br>"
                "• Ask questions and get help from peers<br>"
                "• Join study groups<br>"
                "• Share tips and resources<br>"
                "• Connect with other students<br>"
                "</div>"
            ),
            "card": {
                "type": "community_help",
                "actions": [
                    {"text": "Recent Threads", "action": "show recent threads"},
                    {"text": "Popular Discussions", "action": "show popular threads"},
                    {"text": "Visit Community", "url": "/community/"}
                ]
            }
        }


# For backwards compatibility with the old way
def handle_community_request(message, user=None):
    """Standalone function for community requests"""
    service = CommunityService()
    return service.handle_community_request(message, user)