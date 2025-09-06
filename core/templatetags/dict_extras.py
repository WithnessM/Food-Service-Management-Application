#Used by the template monthly_summary.html

from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def to(start, end):
    return range(start, end + 1)

