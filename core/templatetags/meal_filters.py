from django import template

register = template.Library()

@register.filter
def meal_count(meals, category_code):
    return meals.filter(mealCategory=category_code).count()

@register.filter
def recipient_meal_count(meals, recipient_id):
    return meals.filter(mealsFor_id=recipient_id).count()