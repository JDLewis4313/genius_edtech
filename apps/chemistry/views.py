from django.shortcuts import render
from django.http import JsonResponse
from .models import Element
from quiz.models import Question, Topic, Module
import json

def dashboard(request):
    """Chemistry dashboard view showing all available tools"""
    return render(request, 'chemistry/chemistry_dashboard.html')

def calculator(request):
    """Chemistry calculator view"""
    return render(request, 'chemistry/calculator.html')

def molecular_viewer(request):
    """Molecular 3D viewer"""
    return render(request, 'chemistry/molecular_viewer.html')

def periodic_table(request):
    """Interactive periodic table view"""
    elements = Element.objects.all()
    
    # Prepare element data for JavaScript
    elements_json = []
    for element in elements:
        element_data = {
            'number': element.atomic_number,
            'symbol': element.symbol,
            'name': element.name,
            'mass': str(element.atomic_mass),
            'category': element.get_category_class(),
            'period': element.period,
            'group': element.group,
            'phase': element.phase,
            'radioactive': element.radioactive,
            'electronegativity': element.electronegativity,
            'density': element.density,
            'meltingPoint': element.melting_point,
            'boilingPoint': element.boiling_point,
            'discoverer': element.discoverer,
            'year': element.year_discovered,
            'electronConfig': element.get_electron_configuration(),
        }
        elements_json.append(element_data)
    
    # Get periodic table quiz questions from the database
    try:
        # Find the periodic trends topic or atomic structure module
        periodic_questions = Question.objects.filter(
            topic__title__icontains='periodic'
        ) | Question.objects.filter(
            topic__module__title__icontains='periodic'
        ) | Question.objects.filter(
            text__icontains='element'
        ) | Question.objects.filter(
            text__icontains='periodic'
        )
        
        # Convert questions to format expected by the template
        quiz_questions = []
        for question in periodic_questions[:20]:  # Limit to 20 questions
            options = [choice.text for choice in question.choices.all()]
            correct_answer = question.choices.filter(is_correct=True).first()
            
            if options and correct_answer:
                quiz_questions.append({
                    'question': question.text,
                    'options': options,
                    'correct': correct_answer.text,
                    'explanation': question.explanation,
                    'difficulty': question.difficulty
                })
    except:
        # Fallback to default questions if database queries fail
        quiz_questions = []
    
    context = {
        'elements_json': json.dumps(elements_json),
        'quiz_questions_json': json.dumps(quiz_questions) if quiz_questions else '[]',
    }
    
    return render(request, 'chemistry/periodic_table.html', context)

def element_detail(request, atomic_number):
    """Get detailed information about a specific element"""
    try:
        element = Element.objects.get(atomic_number=atomic_number)
        data = {
            'success': True,
            'element': {
                'atomic_number': element.atomic_number,
                'symbol': element.symbol,
                'name': element.name,
                'atomic_mass': element.atomic_mass,
                'category': element.category,
                'period': element.period,
                'group': element.group,
                'phase': element.phase,
                'radioactive': element.radioactive,
                'natural': element.natural,
                'metal': element.metal,
                'nonmetal': element.nonmetal,
                'metalloid': element.metalloid,
                'number_of_neutrons': element.number_of_neutrons,
                'number_of_protons': element.number_of_protons,
                'number_of_electrons': element.number_of_electrons,
                'number_of_valence': element.number_of_valence,
                'atomic_radius': element.atomic_radius,
                'electronegativity': element.electronegativity,
                'first_ionization': element.first_ionization,
                'density': element.density,
                'melting_point': element.melting_point,
                'boiling_point': element.boiling_point,
                'number_of_isotopes': element.number_of_isotopes,
                'discoverer': element.discoverer,
                'year_discovered': element.year_discovered,
                'specific_heat': element.specific_heat,
                'number_of_shells': element.number_of_shells,
                'electron_configuration': element.get_electron_configuration(),
            }
        }
    except Element.DoesNotExist:
        data = {'success': False, 'error': 'Element not found'}
    
    return JsonResponse(data)