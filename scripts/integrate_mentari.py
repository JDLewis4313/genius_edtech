# scripts/test_mentari.py
from django.core.management.base import BaseCommand
from apps.mentari.services.brain import MentariBrain

class Command(BaseCommand):
    help = 'Test Mentari responses'

    def handle(self, *args, **options):
        brain = MentariBrain()
        
        test_cases = [
            # Math
            ("2 + 2", "arithmetic"),
            ("solve x^2 - 4 = 0", "symbolic math"),
            ("integrate x^2", "calculus"),
            
            # Chemistry
            ("molar mass of H2O", "chemistry"),
            ("tell me about element 6", "element info"),
            
            # Code
            ("run code: print('Hello')", "python code"),
            ("run code: SELECT * FROM users", "SQL detection"),
            ("save code: console.log('test');", "JavaScript save"),
            
            # Quiz
            ("quiz on atoms", "quiz request"),
            
            # Other
            ("reflect on my progress today", "reflection"),
            ("show my profile", "user profile"),
            ("recent forum threads", "community"),
        ]
        
        for message, test_type in test_cases:
            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"TEST: {test_type}")
            self.stdout.write(f"INPUT: {message}")
            try:
                response = brain.respond(message)
                self.stdout.write(self.style.SUCCESS(f"RESPONSE: {response}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))# scripts/test_mentari.py
from django.core.management.base import BaseCommand
from apps.mentari.services.brain import MentariBrain

class Command(BaseCommand):
    help = 'Test Mentari responses'

    def handle(self, *args, **options):
        brain = MentariBrain()
        
        test_cases = [
            # Math
            ("2 + 2", "arithmetic"),
            ("solve x^2 - 4 = 0", "symbolic math"),
            ("integrate x^2", "calculus"),
            
            # Chemistry
            ("molar mass of H2O", "chemistry"),
            ("tell me about element 6", "element info"),
            
            # Code
            ("run code: print('Hello')", "python code"),
            ("run code: SELECT * FROM users", "SQL detection"),
            ("save code: console.log('test');", "JavaScript save"),
            
            # Quiz
            ("quiz on atoms", "quiz request"),
            
            # Other
            ("reflect on my progress today", "reflection"),
            ("show my profile", "user profile"),
            ("recent forum threads", "community"),
        ]
        
        for message, test_type in test_cases:
            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"TEST: {test_type}")
            self.stdout.write(f"INPUT: {message}")
            try:
                response = brain.respond(message)
                self.stdout.write(self.style.SUCCESS(f"RESPONSE: {response}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))