# apps/chemistry/services.py
from .models import Element
import re

class ChemistryService:
    def explain_element(self, atomic_number):
        """Get element info by atomic number"""
        try:
            element = Element.objects.get(atomic_number=atomic_number)
            return self._format_element_info(element)
        except Element.DoesNotExist:
            return f"Element with atomic number {atomic_number} not found."
    
    def explain_element_by_symbol(self, symbol):
        """Get element info by symbol"""
        try:
            element = Element.objects.get(symbol__iexact=symbol)
            return self._format_element_info(element)
        except Element.DoesNotExist:
            return f"Element with symbol '{symbol}' not found."
    
    def _format_element_info(self, element):
        """Format element information nicely"""
        info = f"**{element.name} ({element.symbol})**\n"
        info += f"• Atomic Number: {element.atomic_number}\n"
        info += f"• Atomic Mass: {element.atomic_mass}\n"
        
        # Add optional fields if they exist
        if hasattr(element, 'category') and element.category:
            info += f"• Category: {element.category}\n"
        if hasattr(element, 'phase') and element.phase:
            info += f"• Phase at STP: {element.phase}\n"
        if hasattr(element, 'group') and element.group:
            info += f"• Group: {element.group}\n"
        if hasattr(element, 'period') and element.period:
            info += f"• Period: {element.period}\n"
        if hasattr(element, 'discoverer') and element.discoverer:
            info += f"• Discovered by: {element.discoverer}"
            if hasattr(element, 'year_discovered') and element.year_discovered:
                info += f" ({element.year_discovered})"
            info += "\n"
        
        return info
    
    def calculate_molar_mass(self, formula):
        """Calculate molar mass of a chemical formula"""
        try:
            # Parse formula
            pattern = r'([A-Z][a-z]?)(\d*)'
            matches = re.findall(pattern, formula)
            
            if not matches:
                return f"Invalid formula: {formula}"
            
            total_mass = 0.0
            breakdown = []
            
            for element_symbol, count in matches:
                count = int(count) if count else 1
                
                try:
                    element = Element.objects.get(symbol=element_symbol)
                    mass_contribution = float(element.atomic_mass) * count
                    total_mass += mass_contribution
                    
                    if count > 1:
                        breakdown.append(f"{element_symbol}: {element.atomic_mass} × {count} = {mass_contribution:.2f}")
                    else:
                        breakdown.append(f"{element_symbol}: {element.atomic_mass}")
                        
                except Element.DoesNotExist:
                    return f"Unknown element: {element_symbol}"
            
            response = f"**Molar mass of {formula}:**\n"
            response += "\n".join(breakdown)
            response += f"\n\n**Total: {total_mass:.2f} g/mol**"
            
            return response
            
        except Exception as e:
            return f"Error calculating molar mass: {str(e)}"