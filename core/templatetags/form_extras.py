#Used by the template weekly meals.html
from django import template

register = template.Library()

@register.filter
def get_field(form, name):
    return form[name]

@register.filter
def index(sequence, position):
    #Return the item at the given position in a list
    
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None
