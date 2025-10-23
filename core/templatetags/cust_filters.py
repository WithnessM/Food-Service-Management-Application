# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a value from a dictionary by key"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return 0