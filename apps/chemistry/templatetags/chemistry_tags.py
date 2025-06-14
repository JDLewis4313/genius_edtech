from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):

    """
    Template filter to get an item from a dictionary by key.
    Usage: {{ my_dict|get_item:key_variable }}
    """

    try:
        return dictionary.get(key)
    except Exception:
        return None

@register.filter
def dict_get(d, k):
    """
    For nested dict lookups in templates. Usage: {{ d|dict_get:key }}
    """
    try:
        return d.get(k) if d else None
    except Exception:
        return None

@register.filter
def element_class(element):
    """
    Returns CSS classes for an element based on its category.
    Handles both model instances and dicts.
    Usage: <div class="element {{ element|element_class }}"></div>
    """
    categories = {
        'alkali metal': 'alkali-metal',
        'alkaline earth metal': 'alkaline-earth',
        'transition metal': 'transition-metal',
        'post-transition metal': 'post-transition',
        'metalloid': 'metalloid',
        'nonmetal': 'nonmetal',
        'halogen': 'halogen',
        'noble gas': 'noble-gas',
        'lanthanide': 'lanthanide',
        'actinide': 'actinide',
    }
    # Accept both dict and model instance
    if isinstance(element, dict):
        category = element.get('category', '').lower()
    else:
        category = getattr(element, 'category', '').lower()
    return categories.get(category, '')