import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
import json
import time
from apps.blog.models import ExternalArticle

class Command(BaseCommand):
    help = 'Fetch external articles from various science sources'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, help='Specific source to fetch from')
        parser.add_argument('--limit', type=int, default=10, help='Maximum articles to fetch')

    def handle(self, *args, **options):
        sources = {
            'science_daily': self.fetch_science_daily,
            'nasa': self.fetch_nasa_demo,
        }
        
        if options['source']:
            if options['source'] in sources:
                sources[options['source']](options)
            else:
                self.stdout.write(self.style.ERROR(f"Unknown source: {options['source']}"))
        else:
            # Fetch from all sources
            for source_name, fetch_func in sources.items():
                self.stdout.write(f"Fetching from {source_name}...")
                try:
                    fetch_func(options)
                    time.sleep(2)  # Be respectful to APIs
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error fetching from {source_name}: {e}"))

    def fetch_science_daily(self, options):
        """Fetch articles from Science Daily RSS"""
        url = "https://www.sciencedaily.com/rss/all.xml"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            count = 0
            for item in items[:options['limit']]:
                title = item.find('title').text if item.find('title') else ''
                description = item.find('description').text if item.find('description') else ''
                link = item.find('link').text if item.find('link') else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                
                self.create_or_update_article({
                    'source': 'science_daily',
                    'source_name': 'Science Daily',
                    'title': title[:600],  # Truncate to fit field
                    'summary': self.clean_html(description),
                    'original_url': link,
                    'published_date': self.parse_date(pub_date),
                    'tags': ['science', 'research'],
                    'complexity_level': 'intermediate'
                })
                count += 1
                
            self.stdout.write(self.style.SUCCESS(f"Fetched {count} Science Daily articles"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Science Daily fetch error: {e}"))

    def fetch_nasa_demo(self, options):
        """Create demo NASA articles"""
        demo_articles = [
            {
                'title': 'James Webb Space Telescope Discovers Ancient Galaxies',
                'summary': 'The James Webb Space Telescope has identified some of the oldest and most distant galaxies ever observed, providing new insights into the early universe.',
                'url': 'https://www.nasa.gov/news/releases/2024/webb-ancient-galaxies'
            },
            {
                'title': 'Mars Rover Finds Evidence of Ancient Water',
                'summary': 'NASA\'s Perseverance rover has discovered compelling evidence of ancient water activity on Mars, including mineral deposits that could have supported microbial life.',
                'url': 'https://www.nasa.gov/news/releases/2024/mars-water-evidence'
            },
            {
                'title': 'International Space Station Experiments Yield New Materials',
                'summary': 'Microgravity experiments aboard the ISS have led to the development of new materials with unique properties not achievable on Earth.',
                'url': 'https://www.nasa.gov/news/releases/2024/iss-materials-research'
            }
        ]
        
        for article in demo_articles[:options['limit']]:
            self.create_or_update_article({
                'source': 'nasa',
                'source_name': 'NASA',
                'title': article['title'],
                'summary': article['summary'],
                'original_url': article['url'],
                'published_date': timezone.now(),
                'tags': ['nasa', 'space', 'astronomy'],
                'complexity_level': 'beginner'
            })
            
        self.stdout.write(self.style.SUCCESS(f"Created {len(demo_articles)} NASA demo articles"))

    def create_or_update_article(self, data):
        """Create or update an external article"""
        try:
            article, created = ExternalArticle.objects.get_or_create(
                original_url=data['original_url'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f"Created: {data['title'][:50]}...")
            else:
                self.stdout.write(f"Updated: {data['title'][:50]}...")
                
            return article
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating article: {e}"))
            return None

    def parse_date(self, date_string):
        """Parse various date formats"""
        if not date_string:
            return timezone.now()
            
        # Common date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        
        for fmt in formats:
            try:
                return timezone.make_aware(datetime.strptime(date_string.strip(), fmt))
            except (ValueError, TypeError):
                continue
                
        return timezone.now()

    def clean_html(self, html_string):
        """Clean HTML tags from string"""
        if not html_string:
            return ''
        soup = BeautifulSoup(html_string, 'html.parser')
        return soup.get_text(strip=True, separator=' ')
