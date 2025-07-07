from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Element
from django.core.serializers import serialize
import json

@api_view(['GET'])
def elements_api(request):
    """API endpoint for all elements"""
    elements = Element.objects.all().order_by('atomic_number')
    
    elements_data = []
    for element in elements:
        elements_data.append({
            'atomic_number': element.atomic_number,
            'symbol': element.symbol,
            'name': element.name,
            'atomic_mass': element.atomic_mass,
            'category': element.category,
            'group': element.group,
            'period': element.period,
            'phase': element.phase,
            'electronegativity': element.electronegativity,
            'atomic_radius': element.atomic_radius,
            'year_discovered': element.year_discovered,
            'radioactive': element.radioactive,
            'natural': element.natural,
        })
    
    return Response(elements_data)

@api_view(['GET'])
def element_detail_api(request, symbol):
    """API endpoint for specific element"""
    try:
        element = Element.objects.get(symbol=symbol)
        element_data = {
            'atomic_number': element.atomic_number,
            'symbol': element.symbol,
            'name': element.name,
            'atomic_mass': element.atomic_mass,
            'category': element.category,
            'group': element.group,
            'period': element.period,
            'phase': element.phase,
            'electronegativity': element.electronegativity,
            'atomic_radius': element.atomic_radius,
            'year_discovered': element.year_discovered,
            'radioactive': element.radioactive,
            'natural': element.natural,
            'electron_configuration': element.get_electron_configuration(),
        }
        return Response(element_data)
    except Element.DoesNotExist:
        return Response({'error': 'Element not found'}, status=404)
