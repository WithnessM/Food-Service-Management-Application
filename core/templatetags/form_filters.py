from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """Get form field by dynamic attribute name"""
    return form[field_name]

@register.filter
def add_days(date, days):
    """Add days to a date"""
    from datetime import timedelta
    return date + timedelta(days=int(days))