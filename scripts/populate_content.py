# scripts/populate_content.py
import os
import django
import sys

# Add the project root to Python path
sys.path.append('/path/to/your/genius_edtech')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_local')
django.setup()

from django.core.management import call_command

def populate_external_content():
    """Populate site with external content from multiple sources"""
    
    sources = [
        {'source': 'nasa', 'limit': 5, 'complexity': 'intermediate'},
        {'source': 'science_daily', 'limit': 10, 'complexity': 'beginner'},
        {'source': 'chemistry_world', 'limit': 8, 'complexity': 'advanced'},
        {'source': 'arxiv', 'limit': 5, 'complexity': 'expert'},
    ]
    
    for source_config in sources:
        print(f"Fetching from {source_config['source']}...")
        call_command('fetch_external_articles', **source_config)
        print(f"Completed {source_config['source']}\n")

if __name__ == "__main__":
    populate_external_content()
