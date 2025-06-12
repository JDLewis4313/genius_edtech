from django.shortcuts import render
from .models import Element, Molecule

def dashboard(request):
    # Sample data - replace with database query when models are populated
    modules = [
        {'title': 'Atomic Structure', 'topics': 3, 'difficulty': 'Beginner'},
        {'title': 'Chemical Bonding', 'topics': 4, 'difficulty': 'Intermediate'},
        {'title': 'Stoichiometry', 'topics': 2, 'difficulty': 'Advanced'},
        {'title': 'Thermodynamics', 'topics': 5, 'difficulty': 'Advanced'},
    ]
    return render(request, 'chemistry/chemistry_dashboard.html', {'modules': modules})

def calculator(request):
    return render(request, 'chemistry/calculator.html')

def molecular_viewer(request):
    return render(request, 'chemistry/molecular_viewer.html')

def periodic_table(request):
    elements = Element.objects.all()
    return render(request, 'chemistry/periodic_table.html', {'elements': elements})
