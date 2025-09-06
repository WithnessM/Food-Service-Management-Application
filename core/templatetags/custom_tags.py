from django import template
from datetime import timedelta

register = template.Library()




@register.filter
def add_days(value, days):
    """
    Adds a number of days to a date.
    Usage in template template weekly_summary.html: {{ some_date|add_days:3 }}
    Returns empty string if value is None or invalid.
    """
    if value is None:
        return ""
    
    try:
        days = int(days)  
    except (TypeError, ValueError):
        return value  
    
    try:
        return value + timedelta(days=days)
    except Exception:
        return value  


@register.filter
def get_item(d, key):
    """
    gets an item from a dictionary.
    Usage in template weekly_summary.html: {{ my_dict|get_item:some_key }}
    Returns 0 if key not found, "" on exception.
    """
    try:
        return d.get(key, 0)
    except Exception:
        return ""
