import csv
from django.core.management.base import BaseCommand
from chemistry.models import Element

def parse_int(val):
    try:
        return int(float(val)) if val else None
    except (ValueError, TypeError):
        return None

def parse_float(val):
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None

def parse_bool(val):
    if val and val.lower() == 'yes':
        return True
    return False

class Command(BaseCommand):
    help = 'Load periodic table elements from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        with open(options['csvfile'], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                try:
                    # Parse all the fields from the CSV
                    element_data = {
                        'symbol': row['Symbol'],
                        'name': row['Element'],
                        'atomic_mass': parse_float(row['AtomicMass']),
                        'category': row.get('Type', '').strip(),
                        'group': parse_int(row.get('Group')),
                        'period': parse_int(row['Period']),
                        'phase': row.get('Phase', '').lower() if row.get('Phase') else None,
                        'number_of_neutrons': parse_int(row.get('NumberofNeutrons')),
                        'number_of_protons': parse_int(row.get('NumberofProtons')),
                        'number_of_electrons': parse_int(row.get('NumberofElectrons')),
                        'number_of_valence': parse_int(row.get('NumberofValence')),
                        'radioactive': parse_bool(row.get('Radioactive')),
                        'natural': parse_bool(row.get('Natural')),
                        'metal': parse_bool(row.get('Metal')),
                        'nonmetal': parse_bool(row.get('Nonmetal')),
                        'metalloid': parse_bool(row.get('Metalloid')),
                        'atomic_radius': parse_float(row.get('AtomicRadius')),
                        'electronegativity': parse_float(row.get('Electronegativity')),
                        'first_ionization': parse_float(row.get('FirstIonization')),
                        'density': parse_float(row.get('Density')),
                        'melting_point': parse_float(row.get('MeltingPoint')),
                        'boiling_point': parse_float(row.get('BoilingPoint')),
                        'number_of_isotopes': parse_int(row.get('NumberOfIsotopes')),
                        'discoverer': row.get('Discoverer', '').strip() if row.get('Discoverer') else None,
                        'year_discovered': parse_int(row.get('Year')),
                        'specific_heat': parse_float(row.get('SpecificHeat')),
                        'number_of_shells': parse_int(row.get('NumberofShells')),
                    }
                    
                    # Remove None values
                    element_data = {k: v for k, v in element_data.items() if v is not None}
                    
                    obj, created = Element.objects.update_or_create(
                        atomic_number=parse_int(row['AtomicNumber']),
                        defaults=element_data
                    )
                    
                    if created:
                        self.stdout.write(f'Created element: {obj.name}')
                    else:
                        self.stdout.write(f'Updated element: {obj.name}')
                    
                    count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row {row.get("Element", "Unknown")}: {e}')
                    )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} elements!'))