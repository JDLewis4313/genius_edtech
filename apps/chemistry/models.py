from django.db import models

class Element(models.Model):
    """Chemical element from the periodic table"""
    atomic_number = models.IntegerField(primary_key=True)
    symbol = models.CharField(max_length=3)
    name = models.CharField(max_length=100)
    atomic_mass = models.FloatField()
    category = models.CharField(max_length=50)
    group = models.IntegerField(null=True, blank=True)
    period = models.IntegerField()
    phase = models.CharField(max_length=10, null=True, blank=True)
    number_of_neutrons = models.IntegerField(null=True, blank=True)
    number_of_protons = models.IntegerField(null=True, blank=True)
    number_of_electrons = models.IntegerField(null=True, blank=True)
    number_of_valence = models.IntegerField(null=True, blank=True)
    radioactive = models.BooleanField(default=False)
    natural = models.BooleanField(default=True)
    metal = models.BooleanField(default=False)
    nonmetal = models.BooleanField(default=False)
    metalloid = models.BooleanField(default=False)
    atomic_radius = models.FloatField(null=True, blank=True)
    electronegativity = models.FloatField(null=True, blank=True)
    first_ionization = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    melting_point = models.FloatField(null=True, blank=True)
    boiling_point = models.FloatField(null=True, blank=True)
    number_of_isotopes = models.IntegerField(null=True, blank=True)
    discoverer = models.CharField(max_length=200, null=True, blank=True)
    year_discovered = models.IntegerField(null=True, blank=True)
    specific_heat = models.FloatField(null=True, blank=True)
    number_of_shells = models.IntegerField(null=True, blank=True)
    
    def get_electron_configuration(self):
        """Generate electron configuration based on atomic number"""
        configs = {
            1: "1s¹", 2: "1s²",
            3: "[He] 2s¹", 4: "[He] 2s²", 5: "[He] 2s² 2p¹",
            6: "[He] 2s² 2p²", 7: "[He] 2s² 2p³", 8: "[He] 2s² 2p⁴",
            9: "[He] 2s² 2p⁵", 10: "[He] 2s² 2p⁶",
            11: "[Ne] 3s¹", 12: "[Ne] 3s²", 13: "[Ne] 3s² 3p¹",
            14: "[Ne] 3s² 3p²", 15: "[Ne] 3s² 3p³", 16: "[Ne] 3s² 3p⁴",
            17: "[Ne] 3s² 3p⁵", 18: "[Ne] 3s² 3p⁶",
            # Add more as needed
        }
        return configs.get(self.atomic_number, "Configuration not available")
    
    def get_category_class(self):
        """Return CSS class for element category"""
        category_mapping = {
            'Alkali Metal': 'alkali-metal',
            'Alkaline Earth Metal': 'alkaline-earth',
            'Transition Metal': 'transition-metal',
            'Metal': 'post-transition',
            'Metalloid': 'metalloid',
            'Nonmetal': 'nonmetal',
            'Halogen': 'halogen',
            'Noble Gas': 'noble-gas',
            'Lanthanide': 'lanthanide',
            'Actinide': 'actinide',
            'Transactinide': 'transition-metal',
        }
        return category_mapping.get(self.category, 'unknown')
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    class Meta:
        ordering = ['atomic_number']

class Molecule(models.Model):
    """Chemical molecule for 3D viewer"""
    name = models.CharField(max_length=100)
    formula = models.CharField(max_length=100)
    smiles = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.formula})"