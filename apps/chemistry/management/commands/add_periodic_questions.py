# Save as: apps/chemistry/management/commands/add_periodic_questions.py

from django.core.management.base import BaseCommand
from quiz.models import Module, Topic, Question, Choice

class Command(BaseCommand):
    help = 'Add periodic table specific quiz questions'

    def handle(self, *args, **options):
        # Get or create Periodic Trends module
        module, _ = Module.objects.get_or_create(
            title="Periodic Trends",
            defaults={'description': 'Understanding periodic table trends and properties'}
        )
        
        # Get or create topic
        topic, _ = Topic.objects.get_or_create(
            title="Interactive Periodic Table",
            module=module,
            defaults={'description': 'Test your knowledge of the periodic table'}
        )
        
        # Additional quiz questions specifically for the periodic table
        questions_data = [
            {
                'text': 'Which element has the highest electronegativity?',
                'options': ['Fluorine', 'Oxygen', 'Chlorine', 'Nitrogen'],
                'correct': 'Fluorine',
                'explanation': 'Fluorine has the highest electronegativity (3.98) of all elements.',
                'difficulty': 'medium'
            },
            {
                'text': 'Which of these elements was discovered most recently?',
                'options': ['Oganesson', 'Tennessine', 'Moscovium', 'Nihonium'],
                'correct': 'Tennessine',
                'explanation': 'Tennessine (Ts) was discovered in 2010, making it one of the most recently discovered elements.',
                'difficulty': 'hard'
            },
            {
                'text': 'Which element has the lowest melting point?',
                'options': ['Helium', 'Hydrogen', 'Neon', 'Nitrogen'],
                'correct': 'Helium',
                'explanation': 'Helium has the lowest melting point of all elements at -272.2°C (0.95 K).',
                'difficulty': 'hard'
            },
            {
                'text': 'How many naturally occurring elements are there?',
                'options': ['92', '90', '94', '88'],
                'correct': '92',
                'explanation': 'There are 92 naturally occurring elements, from hydrogen (1) to uranium (92).',
                'difficulty': 'medium'
            },
            {
                'text': 'Which element is named after a continent?',
                'options': ['Europium', 'Americium', 'Africium', 'Asiatium'],
                'correct': 'Europium',
                'explanation': 'Europium (Eu) is named after the continent of Europe.',
                'difficulty': 'easy'
            },
            {
                'text': 'What is the heaviest stable (non-radioactive) element?',
                'options': ['Lead', 'Bismuth', 'Gold', 'Mercury'],
                'correct': 'Lead',
                'explanation': 'Lead (Pb) with atomic number 82 is the heaviest stable element. Bismuth was once thought stable but has a very long half-life.',
                'difficulty': 'hard'
            },
            {
                'text': 'Which halogen is a liquid at room temperature?',
                'options': ['Bromine', 'Iodine', 'Chlorine', 'Fluorine'],
                'correct': 'Bromine',
                'explanation': 'Bromine (Br) is the only halogen that is liquid at room temperature.',
                'difficulty': 'medium'
            },
            {
                'text': 'Which element has the chemical symbol W?',
                'options': ['Tungsten', 'Wolfram', 'Wismuth', 'Wurtzium'],
                'correct': 'Tungsten',
                'explanation': 'Tungsten has the symbol W from its German name Wolfram.',
                'difficulty': 'medium'
            },
            {
                'text': 'How many elements are in Period 7?',
                'options': ['32', '18', '8', '7'],
                'correct': '32',
                'explanation': 'Period 7 contains 32 elements, including the actinides.',
                'difficulty': 'hard'
            },
            {
                'text': 'Which noble gas is radioactive?',
                'options': ['Radon', 'Xenon', 'Krypton', 'Argon'],
                'correct': 'Radon',
                'explanation': 'Radon (Rn) is the only naturally occurring radioactive noble gas.',
                'difficulty': 'medium'
            }
        ]
        
        created_count = 0
        for q_data in questions_data:
            # Check if question already exists
            if not Question.objects.filter(text=q_data['text']).exists():
                question = Question.objects.create(
                    topic=topic,
                    text=q_data['text'],
                    difficulty=q_data['difficulty'],
                    question_type='multiple_choice',
                    explanation=q_data['explanation']
                )
                
                # Create choices
                for option in q_data['options']:
                    Choice.objects.create(
                        question=question,
                        text=option,
                        is_correct=(option == q_data['correct'])
                    )
                
                created_count += 1
                self.stdout.write(f'Created question: {q_data["text"][:50]}...')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} periodic table questions!')
        )
