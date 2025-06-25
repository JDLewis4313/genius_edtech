# apps/blog/management/commands/setup_production.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Set up production environment with initial content'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Setting up GeNiUS EdTech production environment...")
        
        # Run migrations
        self.stdout.write("📊 Applying database migrations...")
        call_command('migrate', verbosity=0)
        
        # Collect static files
        self.stdout.write("📁 Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=0)
        
        # Fetch initial content
        self.stdout.write("📰 Fetching initial external articles...")
        call_command('fetch_external_articles', '--limit', '15')
        
        # Create default boards if they don't exist
        self.stdout.write("🏗️ Setting up community boards...")
        self.setup_default_boards()
        
        self.stdout.write(self.style.SUCCESS("✅ Production setup complete!"))

    def setup_default_boards(self):
        from apps.community.models import Board
        
        default_boards = [
            {
                'name': 'The Feed',
                'slug': 'the-feed',
                'description': 'External articles shared by the community'
            },
            {
                'name': 'General Discussion',
                'slug': 'general',
                'description': 'General chemistry and coding discussions'
            },
            {
                'name': 'Help & Support',
                'slug': 'help',
                'description': 'Get help with chemistry and coding questions'
            }
        ]
        
        for board_data in default_boards:
            Board.objects.get_or_create(
                slug=board_data['slug'],
                defaults={
                    'name': board_data['name'],
                    'description': board_data['description']
                }
            )
            self.stdout.write(f"📋 Board '{board_data['name']}' ready")
