# apps/mentari/services/community.py
from django.utils.html import escape
from datetime import datetime, timedelta

def handle_community_request(message, user=None):
    """Handle community/forum requests"""
    try:
        msg_lower = message.lower()
        
        # Recent threads/discussions
        if any(keyword in msg_lower for keyword in ["recent", "latest", "new"]):
            return handle_recent_threads(user)
        
        # Popular content
        elif any(keyword in msg_lower for keyword in ["popular", "trending", "hot"]):
            return handle_popular_content(user)
        
        # Forum boards/categories
        elif any(keyword in msg_lower for keyword in ["boards", "categories", "sections"]):
            return handle_forum_boards(user)
        
        # Search discussions
        elif any(keyword in msg_lower for keyword in ["search", "find", "look for"]):
            return handle_search_discussions(message, user)
        
        # General community info
        elif any(keyword in msg_lower for keyword in ["community", "forum", "commons"]):
            return get_community_overview(user)
        
        # Default community help
        else:
            return get_community_help(user)
            
    except Exception as e:
        return {
            "text": f"<div class='alert alert-danger'>Community error: {str(e)}</div>"
        }

def handle_recent_threads(user):
    """Handle recent threads request"""
    try:
        from apps.community.services import CommunityService
        service = CommunityService()
        threads = service.get_recent_threads(limit=5)
        
        if threads:
            thread_html = "<br>".join([
                f"• <strong>{escape(thread.title)}</strong> by {escape(thread.author.username)} "
                f"<small>({thread.created_at.strftime('%m/%d %H:%M')})</small>"
                for thread in threads
            ])
            
            return {
                "text": (
                    f"<div class='alert alert-info'>"
                    f"<strong>💬 Recent Community Discussions</strong><br><br>"
                    f"{thread_html}"
                    "</div>"
                ),
                "card": {
                    "type": "thread_list",
                    "threads": [
                        {
                            "title": thread.title,
                            "author": thread.author.username,
                            "created_at": thread.created_at.strftime('%m/%d %H:%M'),
                            "url": f"/community/thread/{thread.id}/"
                        }
                        for thread in threads
                    ]
                },
                "redirect_url": "/community/"
            }
        else:
            return get_empty_community_state()
            
    except ImportError:
        return get_community_fallback("recent discussions")
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-warning'>"
                f"Could not load recent threads: {str(e)}"
                "</div>"
            ),
            "redirect_url": "/community/"
        }

def handle_popular_content(user):
    """Handle popular content request"""
    try:
        from apps.community.services import CommunityService
        service = CommunityService()
        popular = service.get_popular_threads(limit=5)
        
        if popular:
            popular_html = "<br>".join([
                f"• <strong>{escape(thread.title)}</strong> "
                f"<small>({getattr(thread, 'reply_count', 0)} replies)</small>"
                for thread in popular
            ])
            
            return {
                "text": (
                    f"<div class='alert alert-success'>"
                    f"<strong>🔥 Popular Discussions</strong><br><br>"
                    f"{popular_html}"
                    "</div>"
                ),
                "redirect_url": "/community/"
            }
        else:
            return get_empty_community_state()
            
    except ImportError:
        return get_community_fallback("popular discussions")
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-warning'>"
                f"Could not load popular content: {str(e)}"
                "</div>"
            ),
            "redirect_url": "/community/"
        }

def handle_forum_boards(user):
    """Handle forum boards/categories request"""
    try:
        from apps.community.services import CommunityService
        service = CommunityService()
        boards = service.get_boards()
        
        if boards:
            boards_html = "<br>".join([
                f"• <strong>{escape(board.name)}</strong> - {escape(board.description)}"
                for board in boards
            ])
            
            return {
                "text": (
                    f"<div class='alert alert-primary'>"
                    f"<strong>📋 Discussion Boards</strong><br><br>"
                    f"{boards_html}"
                    "</div>"
                ),
                "redirect_url": "/community/"
            }
        else:
            return get_default_boards_info()
            
    except ImportError:
        return get_default_boards_info()
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-warning'>"
                f"Could not load discussion boards: {str(e)}"
                "</div>"
            ),
            "redirect_url": "/community/"
        }

def handle_search_discussions(message, user):
    """Handle search discussions request"""
    # Extract search term
    search_term = ""
    if "search for" in message.lower():
        search_term = message.lower().split("search for", 1)[1].strip()
    elif "find" in message.lower():
        search_term = message.lower().split("find", 1)[1].strip()
    
    search_term = search_term.replace('"', '').replace("'", "").strip()
    
    if search_term:
        return {
            "text": (
                f"<div class='alert alert-info'>"
                f"<strong>🔍 Searching for: \"{escape(search_term)}\"</strong><br><br>"
                f"Redirecting to community search..."
                "</div>"
            ),
            "redirect_url": f"/community/search/?q={search_term}"
        }
    else:
        return {
            "text": (
                "<div class='alert alert-warning'>"
                "Please specify what you'd like to search for in the community discussions."
                "</div>"
            ),
            "redirect_url": "/community/"
        }

def get_community_overview(user):
    """Provide general community overview"""
    user_greeting = ""
    if user and user.is_authenticated:
        user_greeting = f"Welcome back, {escape(user.username)}! "
    
    return {
        "text": (
            f"<div class='alert alert-info'>"
            f"<strong>💬 Welcome to The Commons!</strong><br><br>"
            f"{user_greeting}Connect with fellow learners in our community:<br><br>"
            f"• <strong>Recent discussions</strong> - See what's happening now<br>"
            f"• <strong>Popular topics</strong> - Join trending conversations<br>"
            f"• <strong>Study groups</strong> - Collaborate with peers<br>"
            f"• <strong>Q&A forums</strong> - Get help from the community<br><br>"
            f"<em>Try saying 'show recent threads' or 'popular discussions'</em>"
            "</div>"
        ),
        "card": {
            "type": "help",
            "suggestions": [
                "show recent threads",
                "popular discussions", 
                "discussion boards",
                "search for chemistry help"
            ]
        },
        "redirect_url": "/community/"
    }

def get_community_help(user):
    """Provide community help message"""
    return {
        "text": (
            "<div class='alert alert-primary'>"
            "<strong>💬 Community Features</strong><br><br>"
            "I can help you navigate The Commons:<br>"
            "• View recent discussions<br>"
            "• Find popular topics<br>"
            "• Browse discussion boards<br>"
            "• Search for specific topics<br><br>"
            "What would you like to explore?"
            "</div>"
        ),
        "card": {
            "type": "help",
            "suggestions": [
                "recent threads",
                "popular posts",
                "discussion boards",
                "search discussions"
            ]
        },
        "redirect_url": "/community/"
    }

def get_empty_community_state():
    """Handle empty community state"""
    return {
        "text": (
            "<div class='alert alert-info'>"
            "<strong>💬 Community is Growing!</strong><br><br>"
            "No discussions yet, but you can be the first to start one!<br>"
            "Share a question, insight, or just say hello to the community."
            "</div>"
        ),
        "card": {
            "type": "community_cta",
            "title": "Start a Discussion",
            "description": "No threads yet — help kick things off!",
            "button_text": "Go to The Commons",
            "url": "/community/"
        },
        "redirect_url": "/community/"
    }

def get_community_fallback(content_type):
    """Fallback when community service unavailable"""
    return {
        "text": (
            f"<div class='alert alert-warning'>"
            f"<strong>💬 The Commons</strong><br><br>"
            f"Community features are loading. You'll be redirected to view {content_type}."
            "</div>"
        ),
        "redirect_url": "/community/"
    }

def get_default_boards_info():
    """Provide default boards information when service unavailable"""
    default_boards = [
        {"name": "General Discussion", "description": "Open discussions about learning and education"},
        {"name": "Math & Science", "description": "Discussions about mathematics and scientific topics"},
        {"name": "Chemistry Corner", "description": "All things chemistry - from basics to advanced topics"},
        {"name": "Study Groups", "description": "Form and join study groups with fellow learners"},
        {"name": "Q&A Hub", "description": "Ask questions and get help from the community"},
        {"name": "Resources & Tips", "description": "Share learning resources and study tips"}
    ]
    
    boards_html = "<br>".join([
        f"• <strong>{board['name']}</strong> - {board['description']}"
        for board in default_boards
    ])
    
    return {
        "text": (
            f"<div class='alert alert-primary'>"
            f"<strong>📋 Discussion Boards</strong><br><br>"
            f"{boards_html}<br><br>"
            f"<em>Visit The Commons to explore all boards and join discussions!</em>"
            "</div>"
        ),
        "redirect_url": "/community/"
    }

# Additional utility functions for community features

def format_thread_preview(thread):
    """Format a thread for preview display"""
    return {
        "title": thread.title,
        "author": thread.author.username,
        "created_at": thread.created_at.strftime('%b %d, %Y at %I:%M %p'),
        "reply_count": getattr(thread, 'reply_count', 0),
        "last_activity": getattr(thread, 'last_activity', thread.created_at).strftime('%m/%d %H:%M')
    }

def get_community_stats(user):
    """Get community statistics for user"""
    try:
        from apps.community.models import Thread, Post
        
        stats = {
            "total_threads": Thread.objects.count(),
            "total_posts": Post.objects.count(),
            "active_today": Thread.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=1)
            ).count()
        }
        
        if user and user.is_authenticated:
            stats["user_threads"] = Thread.objects.filter(author=user).count()
            stats["user_posts"] = Post.objects.filter(author=user).count()
        
        return stats
        
    except ImportError:
        return {
            "total_threads": "Loading...",
            "total_posts": "Loading...",
            "active_today": "Loading..."
        }