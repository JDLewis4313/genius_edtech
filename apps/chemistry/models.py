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
    block = models.CharField(max_length=1)
    electron_configuration = models.CharField(max_length=100)
    electronegativity = models.FloatField(null=True, blank=True)
    atomic_radius = models.FloatField(null=True, blank=True)
    ionization_energy = models.FloatField(null=True, blank=True)
    melting_point = models.FloatField(null=True, blank=True)
    boiling_point = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    year_discovered = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    class Meta:
        ordering = ['atomic_number']

class Molecule(models.Model):
    """Chemical molecule for 3D viewer"""
    name = models.CharField(max_length=100)
    formula = models.CharField(max_length=100)
    smiles = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.formula})"
