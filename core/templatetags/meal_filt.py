from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_days(date, days):
    """Add days to a date"""
    try:
        return date + timedelta(days=int(days))
    except (ValueError, TypeError):
        return date

@register.filter
def get_field(form, field_name):
    """Get form field by dynamic attribute name"""
    return form[field_name]