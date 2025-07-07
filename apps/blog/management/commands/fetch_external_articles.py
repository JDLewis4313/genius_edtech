import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
import time
from apps.blog.models import ExternalArticle


class Command(BaseCommand):
    help = 'Fetch external science articles from trusted sources'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, help='Specific source to fetch from')
        parser.add_argument('--limit', type=int, default=10, help='Maximum articles to fetch')

    def handle(self, *args, **options):
        sources = {
            'nasa': self.fetch_nasa_demo,
            'noaa': self.fetch_noaa_rss,
            'cern': self.fetch_cern_rss,
            'nature': self.fetch_nature_rss,
        }

        if options['source']:
            if options['source'] in sources:
                sources[options['source']](options)
            else:
                self.stdout.write(self.style.ERROR(f"Unknown source: {options['source']}"))
        else:
            for name, fetch_func in sources.items():
                self.stdout.write(f"Fetching from {name}...")
                try:
                    fetch_func(options)
                    time.sleep(2)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"{name} fetch error: {e}"))

    def fetch_nasa_demo(self, options):
        articles = [
            {
                'title': 'NASA Unveils New Artemis Lunar Mission Timeline',
                'summary': 'NASA has announced updates to its Artemis program, including adjusted timelines for upcoming lunar missions.',
                'url': 'https://www.nasa.gov/press-release/nasa-artemis-lunar-update'
            }
        ]
        for article in articles[:options['limit']]:
            self.create_or_update_article({
                'source': 'nasa',
                'source_name': 'NASA',
                'title': article['title'],
                'summary': article['summary'],
                'original_url': article['url'],
                'published_date': timezone.now(),
                'tags': ['nasa', 'space', 'astronomy'],
                'complexity_level': 'beginner',
            })
        self.stdout.write(self.style.SUCCESS("Fetched NASA demo articles."))

    def fetch_noaa_rss(self, options):
        return self.fetch_rss_generic(
            url="https://www.noaa.gov/news/rss.xml",
            source='noaa',
            source_name='NOAA',
            tags=['climate', 'earth science', 'environment'],
            complexity='intermediate',
            limit=options['limit']
        )

    def fetch_cern_rss(self, options):
        return self.fetch_rss_generic(
            url="https://home.cern/news/rss",
            source='cern',
            source_name='CERN',
            tags=['physics', 'particles', 'research'],
            complexity='advanced',
            limit=options['limit']
        )

    def fetch_nature_rss(self, options):
        return self.fetch_rss_generic(
            url="https://www.nature.com/nature.rss",
            source='nature',
            source_name='Nature',
            tags=['biology', 'astronomy', 'earth science'],
            complexity='expert',
            limit=options['limit']
        )

    def fetch_rss_generic(self, url, source, source_name, tags, complexity, limit):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')

            count = 0
            for item in items[:limit]:
                title = item.find('title').text
                description = item.find('description').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text

                self.create_or_update_article({
                    'source': source,
                    'source_name': source_name,
                    'title': title[:600],
                    'summary': self.clean_html(description),
                    'original_url': link,
                    'published_date': self.parse_date(pub_date),
                    'tags': tags,
                    'complexity_level': complexity,
                })
                count += 1

            self.stdout.write(self.style.SUCCESS(f"Fetched {count} articles from {source_name}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"{source_name} fetch error: {e}"))

    def create_or_update_article(self, data):
        try:
            article, created = ExternalArticle.objects.get_or_create(
                original_url=data['original_url'],
                defaults=data
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"{status}: {data['title'][:60]}...")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving article: {e}"))

    def parse_date(self, date_string):
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        for fmt in formats:
            try:
                return timezone.make_aware(datetime.strptime(date_string.strip(), fmt))
            except Exception:
                continue
        return timezone.now()

    def clean_html(self, html_string):
        if not html_string:
            return ''
        soup = BeautifulSoup(html_string, 'html.parser')
        return soup.get_text(strip=True, separator=' ')
