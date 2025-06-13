import csv
from django.core.management.base import BaseCommand
from quiz.models import Module, Topic, Question, Choice

class Command(BaseCommand):
    help = 'Import quiz data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Track modules and topics to avoid duplicates
            modules = {}
            topics = {}
            
            for row in reader:
                # Get or create module
                module_name = row['module_name']
                if module_name not in modules:
                    module, created = Module.objects.get_or_create(
                        title=module_name,
                        defaults={'description': f'Module about {module_name}'}
                    )
                    modules[module_name] = module
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created module: {module_name}'))
                
                # Get or create topic
                topic_name = row['topic_name']
                topic_key = f"{module_name}_{topic_name}"
                if topic_key not in topics:
                    topic, created = Topic.objects.get_or_create(
                        title=topic_name,
                        module=modules[module_name],
                        defaults={'description': f'Topic about {topic_name}'}
                    )
                    topics[topic_key] = topic
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created topic: {topic_name}'))
                
                # Create question
                question = Question.objects.create(
                    topic=topics[topic_key],
                    text=row['question_text'],
                    difficulty=row['difficulty'],
                    question_type=row['question_type'],
                    explanation=row['explanation']
                )
                self.stdout.write(f'Created question: {question.text[:30]}...')
                
                # Create choices
                options = row['options'].split('|')
                correct_answer = row['correct_answer']
                
                for option in options:
                    is_correct = (option.strip() == correct_answer.strip())
                    Choice.objects.create(
                        question=question,
                        text=option.strip(),
                        is_correct=is_correct
                    )
                    
            self.stdout.write(self.style.SUCCESS('Quiz data imported successfully!'))
