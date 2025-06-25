# apps/blog/management/commands/refresh_content.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Refresh external content (for scheduled runs)'

    def add_arguments(self, parser):
        parser.add_argument('--daily', action='store_true', help='Daily refresh (fewer articles)')
        parser.add_argument('--weekly', action='store_true', help='Weekly refresh (more articles)')

    def handle(self, *args, **options):
        if options['daily']:
            limit = 5
            self.stdout.write("📅 Daily content refresh...")
        elif options['weekly']:
            limit = 20
            self.stdout.write("📅 Weekly content refresh...")
        else:
            limit = 10
            self.stdout.write("📅 Standard content refresh...")
        
        # Clean up old content (optional)
        self.cleanup_old_content()
        
        # Fetch new content
        call_command('fetch_external_articles', '--limit', str(limit))
        
        self.stdout.write(self.style.SUCCESS(f"✅ Refreshed with up to {limit} new articles"))

    def cleanup_old_content(self):
        from apps.blog.models import ExternalArticle
        
        # Remove articles older than 6 months that have no interactions
        cutoff_date = timezone.now() - timedelta(days=180)
        old_articles = ExternalArticle.objects.filter(
            fetched_date__lt=cutoff_date,
            is_featured=False
        )
        
        # Only delete if they have no comments or reactions
        from apps.interactions.models import Comment, Reaction
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(ExternalArticle)
        articles_with_interactions = Comment.objects.filter(content_type=ct).values_list('object_id', flat=True)
        articles_with_reactions = Reaction.objects.filter(content_type=ct).values_list('object_id', flat=True)
        
        interactive_articles = set(list(articles_with_interactions) + list(articles_with_reactions))
        
        deletable_articles = old_articles.exclude(id__in=interactive_articles)
        deleted_count = deletable_articles.count()
        
        if deleted_count > 0:
            deletable_articles.delete()
            self.stdout.write(f"🧹 Cleaned up {deleted_count} old articles")
