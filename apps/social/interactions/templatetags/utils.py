from django import template

register = template.Library()

@register.filter(name="get_item")  # 👈 This is important
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except Exception:
        return None
