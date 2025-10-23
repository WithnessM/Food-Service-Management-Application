from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime, timedelta

from .models import (
    Meals, MonthlySummary, MealRecipient,
    Category, StockItem, WeeklyStockMovement,
    FormG, FormH
)

# Meals Forms

# Add this to your forms.py
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

    def clean(self):
        cleaned_data = super().clean()
        week_start = cleaned_data.get("weekStart")
        week_end = cleaned_data.get("weekEnd")
        meal_date = cleaned_data.get("mealDate")

        # Validate date ranges
        if week_start and week_end and week_start > week_end:
            raise ValidationError("Week start date cannot be after week end date.")

        if meal_date and week_start and week_end:
            if not (week_start <= meal_date <= week_end):
                raise ValidationError("Meal date must be within the week range.")

        return cleaned_data

class WeeklyMealsForm(forms.Form):
    """Form for entering meals for a whole week for one recipient"""
  
    weekStart = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date", 
            "class": "form-control",
            "id": "weekStartField",
        }),
        label="Week Starting"
    )

    def __init__(self, *args, **kwargs):
        # Extract the recipient parameter
        recipient = kwargs.pop('recipient', None)
        super().__init__(*args, **kwargs)
        
        # Create fields only for the specified recipient
        meal_types = Meals.CATEGORY_CHOICES
        
        if recipient:
            for day in range(7):
                for code, label in meal_types:
                    field_name = f"{day}_{recipient.id}_{code}"
                    
                    # Set initial value from initial data
                    initial_value = self.initial.get(field_name, 0)
                    
                    self.fields[field_name] = forms.IntegerField(
                        required=False,
                        min_value=0,
                        initial=initial_value,
                        widget=forms.NumberInput(attrs={
                            "class": "form-control meal-quantity", 
                            "min": 0,
                            "placeholder": "0"
                        }),
                        label="",
                    )

    def clean_weekStart(self):
        week_start = self.cleaned_data['weekStart']
        if week_start > date.today():
            raise ValidationError("Week start date cannot be in the future.")
        return week_start
    
# ADD THE MISSING MonthlySummaryForm
class MonthlySummaryForm(forms.ModelForm):
    """Form for monthly summary"""
    
    class Meta:
        model = MonthlySummary
        fields = ["month", "year", "totalMeals"]
        widgets = {
            "month": forms.NumberInput(attrs={
                "min": 1, "max": 12, "class": "form-control",
                "placeholder": "Month (1-12)"
            }),
            "year": forms.NumberInput(attrs={
                "min": 2000, "max": 2100, "class": "form-control",
                "placeholder": "Year"
            }),
            "totalMeals": forms.NumberInput(attrs={
                "min": 0, "class": "form-control",
                "placeholder": "Total Meals"
            }),
        }

    def clean_month(self):
        month = self.cleaned_data['month']
        if not 1 <= month <= 12:
            raise ValidationError("Month must be between 1 and 12.")
        return month

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100.")
        return year


# Stock Forms

class CategoryForm(forms.ModelForm):
    """Form to create/edit a stock category"""
    
    class Meta:
        model = Category
        fields = ["category_no", "description"]
        widgets = {
            "category_no": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Category Number"
            }),
            "description": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Category Description"
            }),
        }

    def clean_category_no(self):
        category_no = self.cleaned_data['category_no']
        if Category.objects.filter(category_no=category_no).exists():
            if not self.instance or self.instance.category_no != category_no:
                raise ValidationError("A category with this number already exists.")
        return category_no


class StockItemForm(forms.ModelForm):
    """Form to create or edit a stock item"""
    
    class Meta:
        model = StockItem
        fields = ["name", "unit", "size", "category"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Item Name"
            }),
            "unit": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Unit (e.g., KG)"
            }),
            "size": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Size (optional)"
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
        }


class WeeklyStockMovementForm(forms.ModelForm):
    """Form to create/edit weekly stock movement"""
    
    class Meta:
        model = WeeklyStockMovement
        fields = ["stock_item", "week_number", "total_received", "total_issued", "extern_issues", "cost"]
        widgets = {
            "stock_item": forms.Select(attrs={"class": "form-select"}),
            "week_number": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 53,
                "placeholder": "Week Number (1-53)"
            }),
            "total_received": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "total_issued": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "extern_issues": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "cost": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
        }

    def clean_week_number(self):
        week_number = self.cleaned_data['week_number']
        if not 1 <= week_number <= 53:
            raise ValidationError("Week number must be between 1 and 53.")
        return week_number

    def clean(self):
        cleaned_data = super().clean()
        total_received = cleaned_data.get('total_received', 0)
        total_issued = cleaned_data.get('total_issued', 0)
        extern_issues = cleaned_data.get('extern_issues', 0)

        if total_issued + extern_issues > total_received:
            raise ValidationError(
                "Total issued and external issues cannot exceed total received."
            )

        return cleaned_data


# Enhanced Stock Movement Form with Start/End Stock
class EnhancedWeeklyStockMovementForm(forms.ModelForm):
    """Enhanced form with start/end stock tracking"""
    
    class Meta:
        model = WeeklyStockMovement
        fields = [
            "stock_item", "week_number", "start_stock", "total_received", 
            "total_issued", "extern_issues", "end_stock", "unit_price", "cost"
        ]
        widgets = {
            "stock_item": forms.Select(attrs={"class": "form-select"}),
            "week_number": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 53,
                "placeholder": "Week Number (1-53)"
            }),
            "start_stock": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "total_received": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "total_issued": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "extern_issues": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "end_stock": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "cost": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
        }

    def clean_week_number(self):
        week_number = self.cleaned_data['week_number']
        if not 1 <= week_number <= 53:
            raise ValidationError("Week number must be between 1 and 53.")
        return week_number

    def clean(self):
        cleaned_data = super().clean()
        start_stock = cleaned_data.get('start_stock', 0)
        total_received = cleaned_data.get('total_received', 0)
        total_issued = cleaned_data.get('total_issued', 0)
        extern_issues = cleaned_data.get('extern_issues', 0)
        end_stock = cleaned_data.get('end_stock', 0)

        # Calculate expected end stock
        calculated_end_stock = start_stock + total_received - total_issued - extern_issues
        
        # Check if issued exceeds available stock
        if total_issued + extern_issues > start_stock + total_received:
            raise ValidationError(
                "Total issued and external issues cannot exceed available stock (start stock + received)."
            )

        # Warn about significant variance (optional)
        if abs(calculated_end_stock - end_stock) > 1.0:  # More than 1.0 variance
            self.add_warning(
                f"Note: Calculated end stock ({calculated_end_stock}) differs from entered end stock ({end_stock}). "
                f"Variance: {calculated_end_stock - end_stock}"
            )

        return cleaned_data

    def add_warning(self, message):
        """Add a warning message without failing validation"""
        if not hasattr(self, '_warning_messages'):
            self._warning_messages = []
        self._warning_messages.append(message)


# Form G Form

class FormGForm(forms.ModelForm):
    """Form for creating or editing a Form G record."""

    class Meta:
        model = FormG
        fields = [
            "category",
            "year",
            "month",
            "annual_budget",
            "monthly_budget",
            "week1_expense",
            "week2_expense",
            "week3_expense",
            "week4_expense",
            "week5_expense",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "year": forms.NumberInput(attrs={
                "class": "form-control", 
                "min": 2000, 
                "max": 2100,
                "placeholder": "Year"
            }),
            "month": forms.NumberInput(attrs={
                "class": "form-control", 
                "min": 1, 
                "max": 12,
                "placeholder": "Month"
            }),
            "annual_budget": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "monthly_budget": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "week1_expense": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "week2_expense": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "week3_expense": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "week4_expense": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "week5_expense": forms.NumberInput(attrs={
                "class": "form-control", 
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
        }

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100.")
        return year

    def clean_month(self):
        month = self.cleaned_data['month']
        if not 1 <= month <= 12:
            raise ValidationError("Month must be between 1 and 12.")
        return month

    def clean(self):
        cleaned_data = super().clean()
        monthly_budget = cleaned_data.get('monthly_budget', 0)
        annual_budget = cleaned_data.get('annual_budget', 0)

        # Check if monthly budget is reasonable compared to annual budget
        if monthly_budget and annual_budget:
            expected_monthly = annual_budget / 12
            if abs(monthly_budget - expected_monthly) > expected_monthly * 0.5:  # 50% variance
                self.add_warning(
                    f"Monthly budget ({monthly_budget}) differs significantly from annual budget pro-rata ({expected_monthly:.2f})"
                )

        return cleaned_data

    def add_warning(self, message):
        """Add a warning message without failing validation"""
        if not hasattr(self, '_warning_messages'):
            self._warning_messages = []
        self._warning_messages.append(message)


# Form H Form

class FormHForm(forms.ModelForm):
    """Form for creating or editing a Form H record."""
    
    class Meta:
        model = FormH
        fields = [
            'category',
            'month',
            'year',
            'week1_usage',
            'week2_usage',
            'week3_usage',
            'week4_usage',
            'week5_usage',
            'total_usage',
            'avg_per_person_per_day',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.NumberInput(attrs={
                'min': 1, 
                'max': 12, 
                'class': 'form-control',
                'placeholder': 'Month'
            }),
            'year': forms.NumberInput(attrs={
                'min': 1900, 
                'class': 'form-control',
                'placeholder': 'Year'
            }),
            'week1_usage': forms.NumberInput(attrs={
                'step': '0.001', 
                'class': 'form-control',
                'placeholder': '0.000'
            }),
            'week2_usage': forms.NumberInput(attrs={
                'step': '0.001', 
                'class': 'form-control',
                'placeholder': '0.000'
            }),
            'week3_usage': forms.NumberInput(attrs={
                'step': '0.001', 
                'class': 'form-control',
                'placeholder': '0.000'
            }),
            'week4_usage': forms.NumberInput(attrs={
                'step': '0.001', 
                'class': 'form-control',
                'placeholder': '0.000'
            }),
            'week5_usage': forms.NumberInput(attrs={
                'step': '0.001', 
                'class': 'form-control',
                'placeholder': '0.000'
            }),
            'total_usage': forms.NumberInput(attrs={
                'readonly': True, 
                'class': 'form-control bg-light'
            }),
            'avg_per_person_per_day': forms.NumberInput(attrs={
                'readonly': True, 
                'class': 'form-control bg-light'
            }),
        }

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 1900 or year > 2100:
            raise ValidationError("Year must be between 1900 and 2100.")
        return year

    def clean_month(self):
        month = self.cleaned_data['month']
        if not 1 <= month <= 12:
            raise ValidationError("Month must be between 1 and 12.")
        return month


# Month Selection Form for Reports
class MonthSelectForm(forms.Form):
    """Form to select a month and year for reports"""
    year = forms.IntegerField(
        initial=date.today().year,
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    month = forms.IntegerField(
        min_value=1, max_value=12,
        initial=date.today().month,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100.")
        return year

    def clean_month(self):
        month = self.cleaned_data['month']
        if not 1 <= month <= 12:
            raise ValidationError("Month must be between 1 and 12.")
        return month


# Year Selection Form for Annual Reports
class YearSelectForm(forms.Form):
    """Form to select a year for annual reports"""
    year = forms.IntegerField(
        initial=date.today().year,
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Year"})
    )

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100.")
        return year


# Week Selection Form
class WeekSelectForm(forms.Form):
    """Form to select a week for weekly reports"""
    year = forms.IntegerField(
        initial=date.today().year,
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    week = forms.IntegerField(
        min_value=1, max_value=53,
        initial=date.today().isocalendar()[1],
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100.")
        return year

    def clean_week(self):
        week = self.cleaned_data['week']
        if not 1 <= week <= 53:
            raise ValidationError("Week must be between 1 and 53.")
        return week