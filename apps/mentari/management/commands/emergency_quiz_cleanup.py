# apps/mentari/management/__init__.py
# (Create this file if it doesn't exist - it can be empty)

# apps/mentari/management/commands/__init__.py  
# (Create this file if it doesn't exist - it can be empty)

# apps/mentari/management/commands/emergency_quiz_cleanup.py

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from apps.mentari.models import ConversationEntry

class Command(BaseCommand):
    help = 'Emergency cleanup of stuck quiz sessions with detailed reporting'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleared without actually clearing it',
        )
        parser.add_argument(
            '--older-than-hours',
            type=int,
            default=24,
            help='Clear quiz sessions older than specified hours (default: 24)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each session processed',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours_threshold = options['older_than_hours']
        verbose = options['verbose']
        
        cutoff_time = timezone.now() - timedelta(hours=hours_threshold)
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting emergency quiz session cleanup...')
        )
        self.stdout.write(f'Processing sessions older than {hours_threshold} hours')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes will be made'))
        
        cleared_count = 0
        checked_count = 0
        total_keys_removed = 0
        
        # Get sessions that might have quiz data
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        
        self.stdout.write(f'Found {sessions.count()} active sessions to check...')
        
        for session in sessions:
            try:
                checked_count += 1
                session_data = session.get_decoded()
                
                # Check if this session has quiz data
                quiz_keys = []
                for key in session_data.keys():
                    if 'quiz' in key.lower() and not key.startswith('_'):
                        quiz_keys.append(key)
                
                if quiz_keys:
                    if verbose:
                        self.stdout.write(
                            f"Session {session.session_key[:10]}... has quiz keys: {quiz_keys}"
                        )
                    
                    if dry_run:
                        self.stdout.write(
                            f"Would clear {len(quiz_keys)} quiz keys from session {session.session_key[:10]}..."
                        )
                        cleared_count += 1
                        total_keys_removed += len(quiz_keys)
                    else:
                        # Clear quiz-related keys
                        for key in quiz_keys:
                            del session_data[key]
                        
                        # Save the cleaned session
                        session.session_data = Session.objects.encode(session_data)
                        session.save()
                        cleared_count += 1
                        total_keys_removed += len(quiz_keys)
                        
                        if verbose:
                            self.stdout.write(
                                f"Cleared {len(quiz_keys)} quiz keys from session {session.session_key[:10]}..."
                            )
                        
                        # Log this action in ConversationEntry
                        try:
                            ConversationEntry.objects.create(
                                user_message="System: Emergency cleanup executed",
                                bot_response=f"Cleared {len(quiz_keys)} quiz keys from session",
                                emotion="system_maintenance"
                            )
                        except Exception:
                            pass  # Don't fail if logging fails
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not process session {session.session_key}: {e}')
                )
        
        # Summary report
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CLEANUP SUMMARY')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN COMPLETE:\n'
                    f'  • Sessions checked: {checked_count}\n'
                    f'  • Sessions with quiz data: {cleared_count}\n'
                    f'  • Total quiz keys found: {total_keys_removed}\n'
                    f'  • No actual changes made'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'CLEANUP COMPLETE:\n'
                    f'  • Sessions checked: {checked_count}\n'
                    f'  • Sessions cleaned: {cleared_count}\n'
                    f'  • Total quiz keys removed: {total_keys_removed}\n'
                    f'  • All stuck quiz sessions should now be cleared'
                )
            )
        
        # Additional cleanup recommendations
        if cleared_count > 10:
            self.stdout.write(
                self.style.WARNING(
                    f'\nNOTE: Cleared many sessions ({cleared_count}). Consider:\n'
                    f'  • Adding automatic quiz timeout to prevent future issues\n'
                    f'  • Running this command more frequently (daily cron job)\n'
                    f'  • Investigating why so many sessions got stuck'
                )
            )
        
        # Suggest cron job setup
        if not dry_run and cleared_count > 0:
            self.stdout.write(
                self.style.HTTP_INFO(
                    f'\nTo prevent future issues, add this to your crontab:\n'
                    f'0 2 * * * cd /path/to/your/project && python manage.py emergency_quiz_cleanup\n'
                    f'(This runs daily at 2 AM)'
                )
            )

# apps/mentari/management/commands/test_mentari_system.py

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from apps.mentari.models import ConversationEntry
import json

class Command(BaseCommand):
    help = 'Test the Mentari system integration and quiz reset functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-user',
            action='store_true',
            help='Create a test user for testing',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Testing Mentari System Integration...')
        )
        
        # Create test client
        client = Client()
        
        # Create test user if requested
        if options['create_test_user']:
            try:
                user = User.objects.create_user(
                    username='test_mentari',
                    password='test123',
                    email='test@example.com'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created test user: {user.username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Test user creation failed: {e}')
                )
        
        # Test basic chat functionality
        self.stdout.write('\n1. Testing basic chat...')
        try:
            response = client.post('/ai/chat/', 
                data=json.dumps({'message': 'hello'}),
                content_type='application/json'
            )
            if response.status_code == 200:
                data = response.json()
                if 'text' in data or 'response' in data:
                    self.stdout.write(self.style.SUCCESS('✓ Basic chat working'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Chat response format issue'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Chat failed with status {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Chat test failed: {e}'))
        
        # Test quiz reset endpoint
        self.stdout.write('\n2. Testing quiz reset endpoint...')
        try:
            response = client.post('/ai/chat/', 
                data=json.dumps({'action': 'reset_quiz'}),
                content_type='application/json'
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.stdout.write(self.style.SUCCESS('✓ Quiz reset endpoint working'))
                else:
                    self.stdout.write(self.style.WARNING('! Quiz reset returned success=False'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Quiz reset failed with status {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Quiz reset test failed: {e}'))
        
        # Test routing for different message types
        test_messages = [
            ('community', 'Community routing'),
            ('chemistry', 'Chemistry routing'),
            ('molar mass of H2O', 'Chemistry calculation'),
            ('solve x^2 - 4 = 0', 'Math solving'),
            ('exit quiz', 'Quiz exit command')
        ]
        
        self.stdout.write('\n3. Testing message routing...')
        for message, description in test_messages:
            try:
                response = client.post('/ai/chat/', 
                    data=json.dumps({'message': message}),
                    content_type='application/json'
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'text' in data or 'response' in data:
                        self.stdout.write(self.style.SUCCESS(f'✓ {description}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'! {description} - unusual response format'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ {description} - HTTP {response.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ {description} - {e}'))
        
        # Check conversation logging
        self.stdout.write('\n4. Testing conversation logging...')
        try:
            recent_entries = ConversationEntry.objects.order_by('-id')[:5]
            if recent_entries:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Conversation logging working - {len(recent_entries)} recent entries')
                )
                for entry in recent_entries:
                    self.stdout.write(f'  • {entry.emotion}: {entry.user_message[:50]}...')
            else:
                self.stdout.write(self.style.WARNING('! No conversation entries found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Conversation logging test failed: {e}'))
        
        # Check session count
        self.stdout.write('\n5. Checking sessions...')
        try:
            active_sessions = Session.objects.count()
            self.stdout.write(f'Active sessions: {active_sessions}')
            
            # Count sessions with quiz data
            quiz_sessions = 0
            for session in Session.objects.all()[:10]:  # Check first 10
                try:
                    data = session.get_decoded()
                    if any('quiz' in key.lower() for key in data.keys()):
                        quiz_sessions += 1
                except:
                    pass
            
            if quiz_sessions > 0:
                self.stdout.write(
                    self.style.WARNING(f'! Found {quiz_sessions} sessions with quiz data')
                )
            else:
                self.stdout.write(self.style.SUCCESS('✓ No stuck quiz sessions detected'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Session check failed: {e}'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST SUMMARY COMPLETE')
        self.stdout.write('='*50)
        self.stdout.write(
            'If any tests failed, check:\n'
            '1. URL configuration is correct\n'
            '2. All apps are in INSTALLED_APPS\n'
            '3. Database migrations are applied\n'
            '4. No import errors in views.py'
        )

# Usage instructions:
# 
# 1. Run emergency cleanup:
# python manage.py emergency_quiz_cleanup
# 
# 2. Run dry-run cleanup to see what would be cleaned:
# python manage.py emergency_quiz_cleanup --dry-run
# 
# 3. Run cleanup with verbose output:
# python manage.py emergency_quiz_cleanup --verbose
# 
# 4. Clean sessions older than 12 hours:
# python manage.py emergency_quiz_cleanup --older-than-hours=12
# 
# 5. Test the system:
# python manage.py test_mentari_system
# 
# 6. Test with user creation:
# python manage.py test_mentari_system --create-test-user