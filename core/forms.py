from django import forms

from .models import (
    Meals, MonthlySummary, MealRecipient,
    Category, StockItem, WeeklyStockMovement
)


# Meals Form

class MealsForm(forms.ModelForm):
    """Form for creating/editing a single meal entry"""
    class Meta:
        model = Meals
        fields = ["weekStart", "weekEnd", "mealDate", "mealCategory", "mealsFor", "quantity"]
        widgets = {
            "weekStart": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "weekEnd": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "mealDate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "mealCategory": forms.Select(attrs={"class": "form-select"}),
            "mealsFor": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"min": 0, "class": "form-control"}),
        }


class WeeklyMealsForm(forms.Form):
    #form for entering meals for a whole week.
  
    weekStart = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create fields for each day, recipient and meal type

        recipients = MealRecipient.objects.all()
        meal_types = Meals.CATEGORY_CHOICES
        for day in range(7):
            for recipient in recipients:
                for code, label in meal_types:
                    field_name = f"{day}_{recipient.id}_{code}"
                    self.fields[field_name] = forms.IntegerField(
                        required=False,
                        min_value=0,
                        initial=0,
                        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
                        label=f"Day {day+1} - {recipient.name} - {label}",
                    )


class MonthlySummaryForm(forms.ModelForm):
    #Form for selecting month and year 

    class Meta:
        model = MonthlySummary
        fields = ["month", "year"]
        widgets = {
            "month": forms.NumberInput(attrs={"min": 1, "max": 12, "class": "form-control"}),
            "year": forms.NumberInput(attrs={"min": 2000, "max": 2100, "class": "form-control"}),
        }


# Stock Formss

class CategoryForm(forms.ModelForm):
    #Form to create/edit a stock category

    class Meta:
        model = Category
        fields = ["category_no", "description"]


class StockItemForm(forms.ModelForm):
    #Form to create or edit a stock item

    class Meta:
        model = StockItem
        fields = ["name", "unit", "size", "category"]


class WeeklyStockMovementForm(forms.ModelForm):
    #Form to createooredit weekly stock movement

    class Meta:
        model = WeeklyStockMovement
        fields = ["stock_item", "week_number", "total_received", "total_issued", "extern_issues", "cost"]
