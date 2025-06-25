# apps/tutorials/management/commands/import_sample_tutorials.py
from django.core.management.base import BaseCommand
from apps.tutorials.models import TutorialCategory, Tutorial, TutorialStep
import json

class Command(BaseCommand):
    help = 'Import sample tutorials for chemistry programming with Milwaukee water tutorial'

    def handle(self, *args, **options):
        # Create categories first
        self.stdout.write('Creating categories...')
        chemistry_cat, _ = TutorialCategory.objects.get_or_create(
            slug='chemistry',
            defaults={
                'name': 'Chemistry',
                'icon': 'fas fa-flask',
                'color': '#ff6b6b',
                'description': 'Learn programming through chemistry concepts'
            }
        )
        
        milwaukee_cat, _ = TutorialCategory.objects.get_or_create(
            slug='milwaukee-science',
            defaults={
                'name': 'Milwaukee Science',
                'icon': 'fas fa-city',
                'color': '#FDCB6E',
                'description': 'Science discoveries and innovations from Milwaukee'
            }
        )
        
        # Sample tutorial 1: Molecular Weight Calculator (FIXED)
        self.stdout.write('Creating Molecular Weight Calculator tutorial...')
        mol_weight_tutorial, created = Tutorial.objects.get_or_create(
            slug='molecular-weight-calculator',
            defaults={
                'title': 'Build a Molecular Weight Calculator',
                'category': chemistry_cat,
                'difficulty': 'beginner',
                'duration_minutes': 45,
                'description': 'Learn to parse chemical formulas and calculate molecular weights using Python dictionaries and string manipulation.',
                'learning_objectives': [  # FIX: Added missing field
                    'Parse chemical formulas using regular expressions',
                    'Calculate molecular weights from atomic masses',
                    'Handle complex formulas with parentheses',
                    'Build a practical chemistry tool with Python'
                ],
                'technologies': ['Python', 'Regular Expressions', 'Dictionaries'],
                'language': 'python',
                'starter_code': '''# Molecular Weight Calculator Starter Code
import re

# Dictionary of atomic masses (g/mol)
atomic_masses = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
    'F': 19.00, 'Ne': 20.18, 'Na': 22.99, 'Mg': 24.31,
    'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
    'Cl': 35.45, 'K': 39.10, 'Ca': 40.08, 'Fe': 55.85
}

def parse_formula(formula):
    """
    Parse a chemical formula and return element counts.
    
    Args:
        formula (str): Chemical formula like 'H2O' or 'Ca(OH)2'
    
    Returns:
        dict: Dictionary with elements as keys and counts as values
    """
    # TODO: Implement formula parsing
    # Hint: Use re.findall() with pattern r'([A-Z][a-z]?)(\\d*)'
    pass

def calculate_molecular_weight(formula):
    """
    Calculate the molecular weight of a chemical compound.
    
    Args:
        formula (str): Chemical formula
    
    Returns:
        float: Molecular weight in g/mol
    """
    # TODO: Parse formula and calculate total weight
    pass

# Test your calculator
if __name__ == "__main__":
    test_compounds = ['H2O', 'CO2', 'H2SO4']
    
    for compound in test_compounds:
        print(f"{compound}: {calculate_molecular_weight(compound):.2f} g/mol")
''',
                'solution_code': '''# Molecular Weight Calculator - Complete Solution
import re

atomic_masses = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
    'F': 19.00, 'Ne': 20.18, 'Na': 22.99, 'Mg': 24.31,
    'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
    'Cl': 35.45, 'K': 39.10, 'Ca': 40.08, 'Fe': 55.85
}

def parse_formula(formula):
    """Parse chemical formula handling parentheses."""
    # Handle parentheses first
    while '(' in formula:
        match = re.search(r'\\(([^()]+)\\)(\\d*)', formula)
        if match:
            group = match.group(1)
            multiplier = int(match.group(2)) if match.group(2) else 1
            
            expanded = ''
            for element_match in re.finditer(r'([A-Z][a-z]?)(\\d*)', group):
                element = element_match.group(1)
                count = int(element_match.group(2)) if element_match.group(2) else 1
                expanded += element + str(count * multiplier)
            
            formula = formula.replace(match.group(0), expanded)
    
    # Parse expanded formula
    element_counts = {}
    pattern = r'([A-Z][a-z]?)(\\d*)'
    
    for match in re.finditer(pattern, formula):
        element = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1
        element_counts[element] = element_counts.get(element, 0) + count
    
    return element_counts

def calculate_molecular_weight(formula):
    """Calculate molecular weight from formula."""
    element_counts = parse_formula(formula)
    total_weight = 0
    
    for element, count in element_counts.items():
        if element in atomic_masses:
            total_weight += atomic_masses[element] * count
    
    return total_weight

# Test compounds
if __name__ == "__main__":
    test_compounds = ['H2O', 'CO2', 'Ca(OH)2', 'H2SO4']
    
    for compound in test_compounds:
        weight = calculate_molecular_weight(compound)
        print(f"{compound}: {weight:.2f} g/mol")
''',
                'is_published': True
            }
        )
        
        if created:
            # Create steps for molecular weight tutorial
            mol_steps = [
                {
                    'order': 1,
                    'title': 'Understanding Chemical Formulas',
                    'content': 'Chemical formulas show the elements and their quantities in compounds. Learn to identify patterns.',
                    'code_snippet': '# H2O means 2 hydrogen atoms, 1 oxygen atom',
                    'hint': 'Elements start with capital letters, numbers show quantity.'
                },
                {
                    'order': 2,
                    'title': 'Using Regular Expressions',
                    'content': 'Parse formulas using regex to extract elements and counts.',
                    'code_snippet': "pattern = r'([A-Z][a-z]?)(\\d*)'",
                    'hint': 'Match capital letter, optional lowercase, optional digits.'
                },
                {
                    'order': 3,
                    'title': 'Handling Parentheses',
                    'content': 'Process parentheses groups by expanding them first.',
                    'code_snippet': '# Ca(OH)2 becomes CaO2H2',
                    'hint': 'Find parentheses patterns and multiply contents.'
                }
            ]
            
            for step_data in mol_steps:
                TutorialStep.objects.create(tutorial=mol_weight_tutorial, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created tutorial: {mol_weight_tutorial.title}'))

        # Milwaukee Water Tutorial (NEW)
        self.stdout.write('Creating Milwaukee Water Chemistry tutorial...')
        water_tutorial, created = Tutorial.objects.get_or_create(
            slug='milwaukee-water-chemistry',
            defaults={
                'title': 'Milwaukee Water: From Lake Michigan to Your Tap',
                'category': milwaukee_cat,
                'difficulty': 'beginner',
                'duration_minutes': 40,
                'description': 'Explore the chemistry behind Milwaukee\'s famous water system, from Lake Michigan treatment to quality testing.',
                'learning_objectives': [
                    'Understand water treatment chemistry',
                    'Learn about pH, chlorination, and filtration',
                    'Explore Milwaukee\'s water system history',
                    'Calculate water quality parameters'
                ],
                'technologies': ['Python', 'Data Analysis', 'Chemistry'],
                'language': 'python',
                'starter_code': '''# Milwaukee Water Quality Calculator
import math

class MilwaukeeWaterAnalyzer:
    def __init__(self):
        self.target_ph = 7.5
        self.treatment_plants = {
            'Linnwood': {'capacity': 120, 'year': 1874},
            'Howard': {'capacity': 180, 'year': 1915}
        }
    
    def calculate_chlorine_demand(self, organic_matter, ph_level):
        """Calculate chlorine needed for treatment."""
        # TODO: Implement chlorine calculation
        # Higher organic matter needs more chlorine
        pass
    
    def ph_adjustment_needed(self, current_ph, target_ph=7.5):
        """Calculate lime needed for pH adjustment."""
        # TODO: Calculate pH adjustment
        pass
    
    def water_hardness(self, calcium, magnesium):
        """Calculate water hardness - important for brewing!"""
        # TODO: Calculate hardness as CaCO3 equivalent
        pass

# Test with Milwaukee data
if __name__ == "__main__":
    analyzer = MilwaukeeWaterAnalyzer()
    print("🌊 Milwaukee Water Analysis")
''',
                'solution_code': '''# Milwaukee Water Quality Calculator - Complete
import math

class MilwaukeeWaterAnalyzer:
    def __init__(self):
        self.target_ph = 7.5
        self.treatment_plants = {
            'Linnwood': {'capacity': 120, 'year': 1874, 'location': 'North Side'},
            'Howard': {'capacity': 180, 'year': 1915, 'location': 'South Side'}
        }
        
    def calculate_chlorine_demand(self, organic_matter, ph_level, temperature=45):
        """Calculate chlorine needed for Lake Michigan water treatment."""
        base_demand = organic_matter * 0.015
        
        # pH affects chlorine effectiveness
        ph_factor = 1.0
        if ph_level > 7.5:
            ph_factor = 1.0 + (ph_level - 7.5) * 0.2
        
        # Cold water needs more contact time
        temp_factor = 1.0
        if temperature < 50:
            temp_factor = 1.0 + (50 - temperature) * 0.01
            
        total_demand = base_demand * ph_factor * temp_factor
        return max(0.2, min(4.0, total_demand + 0.5))  # Add residual
    
    def ph_adjustment_needed(self, current_ph, target_ph=7.5):
        """Calculate lime needed for pH adjustment."""
        ph_difference = target_ph - current_ph
        
        if abs(ph_difference) < 0.1:
            return 0, "No adjustment needed"
        
        if ph_difference > 0:
            lime_needed = ph_difference * 10  # mg/L CaO
            return lime_needed, f"Add {lime_needed:.1f} mg/L lime"
        else:
            co2_needed = abs(ph_difference) * 15
            return co2_needed, f"Add {co2_needed:.1f} mg/L CO2"
    
    def water_hardness(self, calcium, magnesium):
        """Calculate hardness - Milwaukee's brewing advantage!"""
        hardness = (calcium * 2.5) + (magnesium * 4.1)
        
        if hardness < 75:
            category = "Soft - Perfect for brewing!"
        elif hardness < 150:
            category = "Moderately hard - Good for most uses"
        else:
            category = "Hard - May need softening"
            
        return hardness, category
    
    def daily_analysis(self, sample_data):
        """Complete daily water analysis."""
        results = {}
        
        # Chlorine analysis
        chlorine_needed = self.calculate_chlorine_demand(
            sample_data['organic_matter'],
            sample_data['ph'],
            sample_data.get('temperature', 45)
        )
        results['chlorine_demand'] = f"{chlorine_needed:.2f} mg/L"
        
        # pH adjustment
        lime_dose, note = self.ph_adjustment_needed(sample_data['ph'])
        results['ph_adjustment'] = note
        
        # Hardness
        if 'calcium' in sample_data:
            hardness, category = self.water_hardness(
                sample_data['calcium'], sample_data['magnesium']
            )
            results['hardness'] = f"{hardness:.1f} mg/L ({category})"
        
        return results

# Milwaukee Water Facts
def milwaukee_facts():
    return [
        "🏭 Milwaukee treats 100+ million gallons daily",
        "🍺 Soft water made Milwaukee perfect for brewing",
        "🏗️ Linnwood plant (1874) is one of America's oldest",
        "🌊 Lake Michigan serves 40+ million people",
        "🧪 Water tested 100,000+ times yearly"
    ]

# Demo
if __name__ == "__main__":
    analyzer = MilwaukeeWaterAnalyzer()
    
    print("🌊 Milwaukee Water Quality Analysis")
    print("=" * 40)
    
    # Sample Lake Michigan water
    sample = {
        'ph': 7.8,
        'organic_matter': 3.2,
        'temperature': 42,
        'calcium': 30,
        'magnesium': 8
    }
    
    results = analyzer.daily_analysis(sample)
    
    for key, value in results.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\\n🧠 Milwaukee Water Facts:")
    for fact in milwaukee_facts():
        print(fact)
''',
                'is_published': True
            }
        )
        
        if created:
            # Create steps for Milwaukee water tutorial
            water_steps = [
                {
                    'order': 1,
                    'title': 'Milwaukee\'s Water Source',
                    'content': 'Learn about Lake Michigan as Milwaukee\'s water source and why location matters for water quality.',
                    'code_snippet': '# Lake Michigan: 1,180 cubic miles of fresh water',
                    'hint': 'Consider how lake depth and temperature affect water quality.'
                },
                {
                    'order': 2,
                    'title': 'Water Treatment Chemistry',
                    'content': 'Understand the chemical processes that make raw lake water safe to drink.',
                    'code_snippet': '# Chlorination: Cl2 + H2O → HOCl + HCl',
                    'hint': 'pH affects how well chlorine works as a disinfectant.'
                },
                {
                    'order': 3,
                    'title': 'Quality Testing',
                    'content': 'Learn how water quality is monitored and what the numbers mean.',
                    'code_snippet': '# pH, chlorine, hardness, fluoride levels',
                    'hint': 'Different parameters indicate different aspects of water safety.'
                },
                {
                    'order': 4,
                    'title': 'Milwaukee\'s Brewing Legacy',
                    'content': 'Discover how water chemistry made Milwaukee famous for brewing.',
                    'code_snippet': '# Soft water + quality hops = great beer',
                    'hint': 'Low mineral content in soft water enhances hop flavors.'
                }
            ]
            
            for step_data in water_steps:
                TutorialStep.objects.create(tutorial=water_tutorial, **step_data)
                
            self.stdout.write(self.style.SUCCESS(f'Created tutorial: {water_tutorial.title}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Sample tutorials imported successfully!'))