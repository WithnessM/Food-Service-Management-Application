from django import template

register = template.Library()

@register.filter
def sum_list(value):
    try:
        return sum(value)
    except TypeError:
        return 0
