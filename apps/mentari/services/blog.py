# apps/mentari/services/blog.py
from apps.blog.services import BlogService

def handle_blog_request(message, user=None):
    """Handle blog/article requests"""
    try:
        service = BlogService()
        
        if "latest" in message.lower() or "recent" in message.lower():
            result = service.get_latest_articles()
            return {
                "text": result,
                "card": {
                    "type": "article_list",
                    "source": "internal"
                }
            }
        
        elif "external" in message.lower() or "science news" in message.lower():
            result = service.get_external_articles()
            return {
                "text": result,
                "card": {
                    "type": "article_list",
                    "source": "external"
                }
            }
        
        else:
            # Search
            query = message.replace("blog", "").replace("article", "").strip()
            result = service.search_articles(query)
            return {"text": result}
            
    except Exception as e:
        return {"text": f"Blog error: {str(e)}"}