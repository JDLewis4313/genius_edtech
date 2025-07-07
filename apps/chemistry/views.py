from django.shortcuts import render
from django.http import JsonResponse
from .models import Element
from apps.analytics.models import Event  # ✅ Analytics logging
import re
from apps.quiz.models import Question 
import json

def dashboard(request):
    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='page_view',
            path=request.path,
            meta={'tool': 'Chemistry Dashboard'}
        )
    return render(request, 'chemistry/chemistry_dashboard.html')

def calculator(request):
    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='tool_open',
            path=request.path,
            meta={'tool': 'Chemistry Calculator'}
        )
    return render(request, 'chemistry/calculator.html')

def molecular_viewer(request):
    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='tool_open',
            path=request.path,
            meta={'tool': 'Molecular 3D Viewer'}
        )
    return render(request, 'chemistry/molecular_viewer.html')

def periodic_table(request):
    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='tool_open',
            path=request.path,
            meta={'tool': 'Periodic Table'}
        )

    elements = Element.objects.all()
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

    try:
        periodic_questions = Question.objects.filter(
            topic__title__icontains='periodic'
        ) | Question.objects.filter(
            topic__module__title__icontains='periodic'
        ) | Question.objects.filter(
            text__icontains='element'
        ) | Question.objects.filter(
            text__icontains='periodic'
        )
        quiz_questions = []
        for question in periodic_questions[:20]:
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
        quiz_questions = []

    context = {
        'elements_json': json.dumps(elements_json),
        'quiz_questions_json': json.dumps(quiz_questions) if quiz_questions else '[]',
    }
    return render(request, 'chemistry/periodic_table.html', context)

def element_detail(request, atomic_number):
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

def calculate_molar_mass(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            formula = data.get("formula", "")
            if not formula:
                return JsonResponse({"success": False, "error": "No formula provided"})

            pattern = r'([A-Z][a-z]?)(\d*)'
            elements = re.findall(pattern, formula)
            if not elements:
                return JsonResponse({"success": False, "error": "Invalid formula"})

            total_mass = 0.0
            steps = []
            for symbol, count in elements:
                try:
                    element = Element.objects.get(symbol=symbol)
                except Element.DoesNotExist:
                    return JsonResponse({"success": False, "error": f"Unknown element: {symbol}"})
                n = int(count) if count else 1
                mass_contrib = element.atomic_mass * n
                total_mass += mass_contrib
                steps.append(f"{symbol}: {element.atomic_mass} × {n} = {mass_contrib:.3f}")

            if request.user.is_authenticated:
                Event.objects.create(
                    user=request.user,
                    event_type='tool_use',
                    path=request.path,
                    meta={'tool': 'Molar Mass Calculator', 'formula': formula, 'result': total_mass}
                )

            return JsonResponse({
                "success": True,
                "formula": formula,
                "molar_mass": total_mass,
                "steps": steps,
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "POST required"})
