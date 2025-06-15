# apps/tutorials/management/commands/import_sample_tutorials.py
from django.core.management.base import BaseCommand
from apps.tutorials.models import TutorialCategory, Tutorial, TutorialStep
import json

class Command(BaseCommand):
    help = 'Import sample tutorials for chemistry programming'

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
        
        # Sample tutorial 1: Molecular Weight Calculator
        self.stdout.write('Creating Molecular Weight Calculator tutorial...')
        mol_weight_tutorial, created = Tutorial.objects.get_or_create(
            slug='molecular-weight-calculator',
            defaults={
                'title': 'Build a Molecular Weight Calculator',
                'category': chemistry_cat,
                'difficulty': 'beginner',
                'duration_minutes': 45,
                'description': 'Learn to parse chemical formulas and calculate molecular weights using Python dictionaries and string manipulation.',
                'technologies': ['Python', 'Regular Expressions', 'Dictionaries'],
                'language': 'python',
                'starter_code': '''# Molecular Weight Calculator Starter Code
import re

# Dictionary of atomic masses (g/mol)
# This is provided for you - in real applications, you might load this from a database
atomic_masses = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
    'F': 19.00, 'Ne': 20.18, 'Na': 22.99, 'Mg': 24.31,
    # ... more elements
}

def parse_formula(formula):
    """
    Parse a chemical formula and return a dictionary of element counts.
    
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
    # TODO: Parse the formula and calculate total weight
    pass

# Test your calculator
if __name__ == "__main__":
    test_compounds = ['H2O', 'CO2', 'H2SO4']
    
    for compound in test_compounds:
        # TODO: Calculate and print the molecular weight
        print(f"{compound}: {calculate_molecular_weight(compound):.2f} g/mol")
''',
                'solution_code': '''# Molecular Weight Calculator - Complete Solution
import re

# Dictionary of atomic masses (g/mol)
atomic_masses = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
    'F': 19.00, 'Ne': 20.18, 'Na': 22.99, 'Mg': 24.31,
    'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
    'Cl': 35.45, 'Ar': 39.95, 'K': 39.10, 'Ca': 40.08,
    'Fe': 55.85, 'Cu': 63.55, 'Zn': 65.39, 'Br': 79.90,
    'Ag': 107.87, 'I': 126.90, 'Au': 196.97
}

def parse_formula(formula):
    """
    Parse a chemical formula and return a dictionary of element counts.
    Handles parentheses and complex formulas.
    """
    # First, expand parentheses
    while '(' in formula:
        # Find innermost parentheses
        match = re.search(r'\\(([^()]+)\\)(\\d*)', formula)
        if match:
            group = match.group(1)
            multiplier = int(match.group(2)) if match.group(2) else 1
            
            # Multiply everything inside parentheses
            expanded = ''
            for element_match in re.finditer(r'([A-Z][a-z]?)(\\d*)', group):
                element = element_match.group(1)
                count = int(element_match.group(2)) if element_match.group(2) else 1
                expanded += element + str(count * multiplier)
            
            # Replace the parentheses group with expanded form
            formula = formula.replace(match.group(0), expanded)
    
    # Now parse the expanded formula
    element_counts = {}
    pattern = r'([A-Z][a-z]?)(\\d*)'
    
    for match in re.finditer(pattern, formula):
        element = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1
        
        if element in element_counts:
            element_counts[element] += count
        else:
            element_counts[element] = count
    
    return element_counts

def calculate_molecular_weight(formula):
    """
    Calculate the molecular weight of a chemical compound.
    """
    element_counts = parse_formula(formula)
    total_weight = 0
    
    print(f"\\nCalculating molecular weight for: {formula}")
    print("-" * 40)
    
    for element, count in element_counts.items():
        if element in atomic_masses:
            weight = atomic_masses[element] * count
            total_weight += weight
            print(f"{element}: {count} × {atomic_masses[element]:.3f} = {weight:.3f} g/mol")
        else:
            print(f"Warning: Unknown element '{element}'")
    
    print("-" * 40)
    print(f"Total molecular weight: {total_weight:.3f} g/mol")
    return total_weight

# Test the calculator with various compounds
if __name__ == "__main__":
    test_compounds = [
        'H2O',           # Water
        'CO2',           # Carbon dioxide
        'C6H12O6',       # Glucose
        'Ca(OH)2',       # Calcium hydroxide
        'Al2(SO4)3',     # Aluminum sulfate
        'Fe2O3',         # Iron(III) oxide
        'H2SO4',         # Sulfuric acid
        'NH4NO3',        # Ammonium nitrate
    ]
    
    print("Molecular Weight Calculator")
    print("=" * 50)
    
    for compound in test_compounds:
        weight = calculate_molecular_weight(compound)
        print()
''',
                'is_published': True
            }
        )
        
        if created:
            # Create tutorial steps
            steps = [
                {
                    'order': 1,
                    'title': 'Understanding the Problem',
                    'content': '''In chemistry, calculating molecular weights is a fundamental task. Given a chemical formula like H₂O or Ca(OH)₂, we need to:

1. Parse the formula to count each element
2. Look up atomic masses
3. Calculate the total molecular weight

This tutorial will teach you to build a calculator that handles simple and complex formulas with parentheses.''',
                    'code_snippet': '# Example formulas we\'ll handle:\n# H2O → H: 2, O: 1\n# Ca(OH)2 → Ca: 1, O: 2, H: 2',
                    'hint': 'Start by understanding how chemical formulas are structured.'
                },
                {
                    'order': 2,
                    'title': 'Parsing Simple Formulas',
                    'content': '''Let's start with simple formulas without parentheses. We'll use regular expressions to match element symbols and their counts.

Element symbols:
- Start with uppercase letter
- May have one lowercase letter
- Followed by optional number''',
                    'code_snippet': 'import re\n\n# Pattern to match elements\npattern = r\'([A-Z][a-z]?)(\\d*)\'\n\n# Test it\nmatches = re.findall(pattern, \'H2O\')\nprint(matches)  # [(\'H\', \'2\'), (\'O\', \'\')]',
                    'hint': 'Use re.findall() to find all element-count pairs in the formula.'
                },
                {
                    'order': 3,
                    'title': 'Handling Parentheses',
                    'content': '''Chemical formulas often use parentheses to group elements, like Ca(OH)₂. We need to:

1. Find parentheses groups
2. Multiply counts inside by the number after parentheses
3. Expand the formula before parsing''',
                    'code_snippet': '# Ca(OH)2 should become CaO2H2\n# Find pattern: (contents)number',
                    'hint': 'Process parentheses from innermost to outermost using a while loop.'
                },
                {
                    'order': 4,
                    'title': 'Testing Your Calculator',
                    'content': '''Test your calculator with various compounds to ensure it works correctly. Common test cases include:

- Simple compounds: H2O, CO2, NH3
- Compounds with parentheses: Ca(OH)2, Al2(SO4)3
- Complex organic molecules: C6H12O6 (glucose)''',
                    'code_snippet': '',
                    'hint': 'Print intermediate results to debug your parsing logic.'
                }
            ]
            
            for step_data in steps:
                TutorialStep.objects.create(tutorial=mol_weight_tutorial, **step_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created tutorial: {mol_weight_tutorial.title}'))
        
        # Sample tutorial 2: pH Calculator
        self.stdout.write('Creating pH Calculator tutorial...')
        ph_tutorial, created = Tutorial.objects.get_or_create(
            slug='ph-calculator',
            defaults={
                'title': 'Build a pH and Acid-Base Calculator',
                'category': chemistry_cat,
                'difficulty': 'intermediate',
                'duration_minutes': 60,
                'description': 'Create a comprehensive pH calculator that handles strong and weak acids/bases, buffers, and titrations.',
                'technologies': ['Python', 'Math', 'Chemistry'],
                'language': 'python',
                'starter_code': '''# pH and Acid-Base Calculator
import math

# Water ion product constant at 25°C
Kw = 1.0e-14

def ph_from_h_concentration(h_concentration):
    """Calculate pH from H+ concentration."""
    # TODO: Implement pH = -log10[H+]
    pass

def poh_from_oh_concentration(oh_concentration):
    """Calculate pOH from OH- concentration."""
    # TODO: Implement pOH = -log10[OH-]
    pass

def henderson_hasselbalch(pka, base_conc, acid_conc):
    """Calculate pH of a buffer using Henderson-Hasselbalch equation."""
    # TODO: Implement pH = pKa + log10([A-]/[HA])
    pass

# Test your functions
if __name__ == "__main__":
    # Test 1: Strong acid
    h_conc = 0.01  # 0.01 M HCl
    print(f"pH of 0.01 M HCl: {ph_from_h_concentration(h_conc):.2f}")
    
    # Test 2: Buffer
    pka = 4.76  # Acetic acid
    print(f"Buffer pH: {henderson_hasselbalch(pka, 0.1, 0.1):.2f}")
''',
                'solution_code': '''# pH and Acid-Base Calculator - Complete Solution
import math
import matplotlib.pyplot as plt

# Constants
Kw = 1.0e-14  # Water ion product at 25°C
R = 8.314     # Gas constant (J/mol·K)
T = 298.15    # Temperature (K)

def ph_from_h_concentration(h_concentration):
    """Calculate pH from H+ concentration."""
    if h_concentration <= 0:
        raise ValueError("H+ concentration must be positive")
    return -math.log10(h_concentration)

def poh_from_oh_concentration(oh_concentration):
    """Calculate pOH from OH- concentration."""
    if oh_concentration <= 0:
        raise ValueError("OH- concentration must be positive")
    return -math.log10(oh_concentration)

def h_from_ph(ph):
    """Calculate H+ concentration from pH."""
    return 10**(-ph)

def oh_from_poh(poh):
    """Calculate OH- concentration from pOH."""
    return 10**(-poh)

def henderson_hasselbalch(pka, base_conc, acid_conc):
    """Calculate pH of a buffer using Henderson-Hasselbalch equation."""
    if base_conc <= 0 or acid_conc <= 0:
        raise ValueError("Concentrations must be positive")
    return pka + math.log10(base_conc / acid_conc)

def weak_acid_ph(ka, concentration):
    """Calculate pH of a weak acid solution."""
    # For weak acid: [H+] = sqrt(Ka * C)
    h_concentration = math.sqrt(ka * concentration)
    return ph_from_h_concentration(h_concentration)

def weak_base_ph(kb, concentration):
    """Calculate pH of a weak base solution."""
    # For weak base: [OH-] = sqrt(Kb * C)
    oh_concentration = math.sqrt(kb * concentration)
    poh = poh_from_oh_concentration(oh_concentration)
    return 14 - poh

def titration_curve(acid_vol, acid_conc, base_conc, pka=None):
    """Generate titration curve data."""
    volumes = []
    ph_values = []
    
    # Calculate for different amounts of base added
    for base_vol in range(0, int(acid_vol * 2.5) + 1):
        volumes.append(base_vol)
        
        total_vol = acid_vol + base_vol
        acid_moles = acid_vol * acid_conc
        base_moles = base_vol * base_conc
        
        if base_moles < acid_moles:
            # Before equivalence point
            remaining_acid = (acid_moles - base_moles) / total_vol
            if pka:  # Weak acid
                # Buffer region
                salt_conc = base_moles / total_vol
                ph = henderson_hasselbalch(pka, salt_conc, remaining_acid)
            else:  # Strong acid
                ph = ph_from_h_concentration(remaining_acid)
        elif base_moles == acid_moles:
            # At equivalence point
            if pka:  # Weak acid
                # Salt hydrolysis
                salt_conc = acid_moles / total_vol
                kb = Kw / (10**(-pka))
                ph = weak_base_ph(kb, salt_conc)
            else:  # Strong acid
                ph = 7.0
        else:
            # After equivalence point
            excess_base = (base_moles - acid_moles) / total_vol
            poh = poh_from_oh_concentration(excess_base)
            ph = 14 - poh
        
        ph_values.append(ph)
    
    return volumes, ph_values

# Demonstration
if __name__ == "__main__":
    print("pH and Acid-Base Calculator")
    print("=" * 50)
    
    # Example 1: Strong acid
    print("\\n1. Strong Acid (HCl)")
    h_conc = 0.01  # 0.01 M HCl
    ph = ph_from_h_concentration(h_conc)
    print(f"[H+] = {h_conc} M")
    print(f"pH = {ph:.2f}")
    print(f"pOH = {14 - ph:.2f}")
    
    # Example 2: Strong base
    print("\\n2. Strong Base (NaOH)")
    oh_conc = 0.001  # 0.001 M NaOH
    poh = poh_from_oh_concentration(oh_conc)
    ph = 14 - poh
    print(f"[OH-] = {oh_conc} M")
    print(f"pOH = {poh:.2f}")
    print(f"pH = {ph:.2f}")
    
    # Example 3: Buffer
    print("\\n3. Acetate Buffer")
    pka_acetic = 4.76
    acetate = 0.1
    acetic_acid = 0.1
    buffer_ph = henderson_hasselbalch(pka_acetic, acetate, acetic_acid)
    print(f"[CH3COO-]/[CH3COOH] = {acetate}/{acetic_acid}")
    print(f"pKa = {pka_acetic}")
    print(f"pH = {buffer_ph:.2f}")
    
    # Example 4: Weak acid
    print("\\n4. Weak Acid (Acetic Acid)")
    ka_acetic = 1.8e-5
    conc = 0.1
    weak_ph = weak_acid_ph(ka_acetic, conc)
    print(f"Ka = {ka_acetic}")
    print(f"Concentration = {conc} M")
    print(f"pH = {weak_ph:.2f}")
    
    # Example 5: Titration curve
    print("\\n5. Generating Titration Curve...")
    volumes, ph_values = titration_curve(25, 0.1, 0.1, pka=4.76)
    print(f"Equivalence point at {25} mL")
    print(f"pH at equivalence: {ph_values[25]:.2f}")
''',
                'is_published': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created tutorial: {ph_tutorial.title}'))
        
        self.stdout.write(self.style.SUCCESS('Sample tutorials imported successfully!'))