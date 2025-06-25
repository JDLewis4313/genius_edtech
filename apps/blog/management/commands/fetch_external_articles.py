# apps/blog/management/commands/fetch_external_articles.py
from django.core.management.base import BaseCommand
import feedparser
from datetime import datetime
from apps.blog.models import ExternalArticle

class Command(BaseCommand):
    help = 'Fetch external news feeds and update the ExternalArticle model'

    # Define a list of (source_identifier, feed_url) pairs.
    FEED_URLS = [
        ('nasa', 'https://www.nasa.gov/rss/dyn/breaking_news.rss'),
        ('noaa', 'https://www.noaa.gov/rss/rss.xml'),
        ('nature', 'https://www.nature.com/nature/articles?type=news&format=rss'),
        # Add additional feed URLs as needed.
    ]

    def handle(self, *args, **options):
        for source, url in self.FEED_URLS:
            self.stdout.write(f"Fetching articles from {source} feed...")
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.title
                summary = entry.summary if hasattr(entry, 'summary') else ''
                # Parse the published date if available.
                published_date = None
                if hasattr(entry, 'published_parsed'):
                    published_date = datetime(*entry.published_parsed[:6])

                # Check if the article already exists by its URL.
                if ExternalArticle.objects.filter(original_url=entry.link).exists():
                    continue

                # Create a new ExternalArticle instance.
                article = ExternalArticle(
                    source=source,
                    source_name=source.upper(),  # Or map to a more specific source name.
                    original_url=entry.link,
                    title=title,
                    summary=summary,
                    published_date=published_date,
                    is_featured=False  # Set to True if you want to feature certain articles.
                )
                article.save()
                self.stdout.write(f"Added article: {title}")

        self.stdout.write(self.style.SUCCESS("Finished fetching external articles."))
