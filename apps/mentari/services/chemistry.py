# apps/mentari/services/chemistry.py
import re
from django.utils.html import escape

def handle_chemistry_request(message, user=None):
    """Handle chemistry-related requests"""
    try:
        msg_lower = message.lower()
        
        # Molar mass calculations
        if "molar mass" in msg_lower or "molecular weight" in msg_lower:
            return handle_molar_mass_request(message)
        
        # Element information
        elif any(keyword in msg_lower for keyword in ["element", "atomic number", "periodic"]):
            return handle_element_request(message)
        
        # Chemical formula analysis
        elif any(keyword in msg_lower for keyword in ["formula", "compound", "molecule"]):
            return handle_formula_analysis(message)
        
        # General chemistry information
        elif "chemistry" in msg_lower:
            return get_chemistry_overview()
        
        # Default chemistry help
        else:
            return get_chemistry_help()
            
    except Exception as e:
        return {
            "text": f"<div class='alert alert-danger'>Chemistry error: {str(e)}</div>"
        }

def handle_molar_mass_request(message):
    """Handle molar mass calculation requests"""
    # Extract chemical formula using regex
    formula_match = re.search(r'\b([A-Z][a-z]?\d*)+\b', message)
    
    if not formula_match:
        return {
            "text": (
                "<div class='alert alert-warning'>"
                "Please provide a chemical formula (e.g., H2O, CO2, NaCl)"
                "</div>"
            )
        }
    
    formula = formula_match.group(0)
    
    try:
        # Try to import and use the chemistry service
        from apps.chemistry.services import ChemistryService
        service = ChemistryService()
        molar_mass = service.calculate_molar_mass(formula)
        
        return {
            "text": (
                f"<div class='alert alert-success'>"
                f"<strong>🧪 Molar Mass Calculation</strong><br>"
                f"Formula: <strong>{escape(formula)}</strong><br>"
                f"Molar Mass: <strong>{molar_mass}</strong>"
                "</div>"
            ),
            "card": {
                "type": "chemistry_result",
                "formula": formula,
                "molar_mass": molar_mass
            }
        }
    except ImportError:
        # Fallback if chemistry service not available
        return get_basic_molar_mass(formula)
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-danger'>"
                f"Could not calculate molar mass for {escape(formula)}: {str(e)}"
                "</div>"
            )
        }

def handle_element_request(message):
    """Handle element information requests"""
    try:
        # Try to extract element symbol or atomic number
        element_match = re.search(r'\b[A-Z][a-z]?\b', message)
        number_match = re.search(r'\b\d+\b', message)
        
        from apps.chemistry.services import ChemistryService
        service = ChemistryService()
        
        if element_match:
            symbol = element_match.group(0)
            result = service.explain_element_by_symbol(symbol)
        elif number_match:
            atomic_num = int(number_match.group(0))
            result = service.explain_element(atomic_num)
        else:
            return {
                "text": (
                    "<div class='alert alert-warning'>"
                    "Please specify an element symbol (e.g., C, H, O) or atomic number"
                    "</div>"
                )
            }
        
        return {
            "text": result
        }
        
    except ImportError:
        return {
            "text": (
                "<div class='alert alert-info'>"
                "🧪 Element information is available in the chemistry section!"
                "</div>"
            ),
            "redirect_url": "/chemistry/"
        }
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-danger'>"
                f"Element lookup error: {str(e)}"
                "</div>"
            )
        }

def handle_formula_analysis(message):
    """Handle chemical formula analysis"""
    # Extract formula
    formula_match = re.search(r'\b([A-Z][a-z]?\d*)+\b', message)
    
    if not formula_match:
        return {
            "text": (
                "<div class='alert alert-warning'>"
                "Please provide a chemical formula to analyze (e.g., H2O, CO2)"
                "</div>"
            )
        }
    
    formula = formula_match.group(0)
    
    try:
        from apps.chemistry.services import ChemistryService
        service = ChemistryService()
        analysis = service.analyze_compound(formula)
        
        return {
            "text": analysis,
            "card": {
                "type": "chemistry_result",
                "formula": formula
            }
        }
        
    except ImportError:
        return get_basic_formula_info(formula)
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-danger'>"
                f"Formula analysis error: {str(e)}"
                "</div>"
            )
        }

def get_chemistry_overview():
    """Provide general chemistry overview"""
    return {
        "text": (
            "<div class='alert alert-info'>"
            "<strong>🧪 Chemistry Helper</strong><br><br>"
            "I can help you with:<br>"
            "• <strong>Molar mass calculations</strong> - 'molar mass of H2O'<br>"
            "• <strong>Element information</strong> - 'tell me about carbon'<br>"
            "• <strong>Compound analysis</strong> - 'analyze CO2'<br>"
            "• <strong>Periodic table data</strong> - 'element 6'<br><br>"
            "Try asking about any chemical formula or element!"
            "</div>"
        ),
        "card": {
            "type": "help",
            "suggestions": [
                "molar mass of H2O",
                "tell me about oxygen",
                "analyze CO2",
                "element 6"
            ]
        }
    }

def get_chemistry_help():
    """Provide chemistry help message"""
    return {
        "text": (
            "<div class='alert alert-primary'>"
            "<strong>🧪 Chemistry Assistant Ready!</strong><br><br>"
            "Ask me about:<br>"
            "• Chemical formulas (H2O, CO2, NaCl)<br>"
            "• Elements and atomic properties<br>"
            "• Molar mass calculations<br>"
            "• Compound analysis<br><br>"
            "<em>Example: 'What's the molar mass of water?'</em>"
            "</div>"
        ),
        "redirect_url": "/chemistry/"
    }

def get_basic_molar_mass(formula):
    """Provide basic molar mass calculation when service unavailable"""
    # Basic atomic masses for common elements
    atomic_masses = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'Na': 22.990, 'Cl': 35.453, 'Ca': 40.078, 'Fe': 55.845
    }
    
    try:
        # Simple parser for basic formulas
        elements = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
        total_mass = 0
        
        for element, count in elements:
            if element in atomic_masses:
                count = int(count) if count else 1
                total_mass += atomic_masses[element] * count
            else:
                raise ValueError(f"Unknown element: {element}")
        
        return {
            "text": (
                f"<div class='alert alert-success'>"
                f"<strong>🧪 Molar Mass (Basic Calculation)</strong><br>"
                f"Formula: <strong>{escape(formula)}</strong><br>"
                f"Approximate Molar Mass: <strong>{total_mass:.3f} g/mol</strong><br>"
                f"<small>Note: For precise calculations, visit the chemistry section</small>"
                "</div>"
            ),
            "card": {
                "type": "chemistry_result",
                "formula": formula,
                "molar_mass": f"{total_mass:.3f} g/mol"
            }
        }
        
    except Exception as e:
        return {
            "text": (
                f"<div class='alert alert-warning'>"
                f"Could not calculate molar mass for {escape(formula)}. "
                f"Try visiting the chemistry section for advanced calculations."
                "</div>"
            ),
            "redirect_url": "/chemistry/"
        }

def get_basic_formula_info(formula):
    """Provide basic formula information when service unavailable"""
    return {
        "text": (
            f"<div class='alert alert-info'>"
            f"<strong>🧪 Chemical Formula: {escape(formula)}</strong><br><br>"
            f"For detailed analysis including:<br>"
            f"• Molecular structure<br>"
            f"• Bond information<br>"
            f"• Physical properties<br>"
            f"• Reaction data<br><br>"
            f"Visit the chemistry section!"
            "</div>"
        ),
        "redirect_url": "/chemistry/"
    }