# apps/blog/templatetags/blog_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Retrieves a value from a dictionary using the given key.
    This is used in templates to show reaction counts.
    """
    return dictionary.get(key)
