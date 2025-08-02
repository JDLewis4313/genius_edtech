# apps/blog/services.py
from .models import BlogPost, ExternalArticle
from django.db.models import Q

class BlogService:
    def get_latest_articles(self, limit=5):
        """Get latest published articles"""
        posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:limit]
        
        if posts:
            response = "📰 Latest Articles:\n\n"
            for post in posts:
                response += f"• **{post.title}**\n"
                response += f"  {post.excerpt}...\n"
                response += f"  Read more: /blog/{post.slug}/\n\n"
            return response
        else:
            return "No articles published yet."
    
    def get_external_articles(self, limit=5):
        """Get latest external science articles"""
        articles = ExternalArticle.objects.filter(is_featured=True)[:limit]
        
        if not articles:
            articles = ExternalArticle.objects.all()[:limit]
        
        if articles:
            response = "🔬 Science News:\n\n"
            for article in articles:
                response += f"• **{article.title}** ({article.source_name})\n"
                response += f"  {article.summary[:100]}...\n"
                response += f"  Original: {article.original_url}\n\n"
            return response
        else:
            return "No external articles available. Run 'python manage.py fetch_external_content' to get some!"
    
    def search_articles(self, query):
        """Search articles by keyword"""
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_published=True
        )[:5]
        
        if posts:
            response = f"🔍 Articles about '{query}':\n\n"
            for post in posts:
                response += f"• {post.title} - /blog/{post.slug}/\n"
            return response
        else:
            return f"No articles found about '{query}'."
    
    def recommend_articles(self, topic):
        """AI-powered article recommendations"""
        # For now, just search - could enhance with ML later
        return self.search_articles(topic)