from datetime import timedelta
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class MealRecipient(models.Model):
    """Represents a person receiving meals"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Meal Recipient"
        verbose_name_plural = "Meal Recipients"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipients_list')


class Meals(models.Model):
    """Represents a meal entry for a recipient"""
    
    CATEGORY_BREAKFAST = "O"
    CATEGORY_LUNCH = "M"
    CATEGORY_DINNER = "A"
    CATEGORY_NIGHT_SNACK = "N"
    
    CATEGORY_CHOICES = [
        (CATEGORY_BREAKFAST, "Breakfast"),
        (CATEGORY_LUNCH, "Lunch"),
        (CATEGORY_DINNER, "Dinner"),
        (CATEGORY_NIGHT_SNACK, "Night Snack"),
    ]

    weekStart = models.DateField()
    weekEnd = models.DateField()
    mealDate = models.DateField()
    quantity = models.PositiveIntegerField(default=1)
    mealCategory = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    mealsFor = models.ForeignKey(MealRecipient, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Meal"
        verbose_name_plural = "Meals"
        ordering = ["-mealDate", "mealsFor"]
        indexes = [
            models.Index(fields=['mealDate', 'mealsFor']),
            models.Index(fields=['weekStart', 'weekEnd']),
        ]

    def __str__(self):
        return f"{self.mealDate} - {self.get_mealCategory_display()} for {self.mealsFor}"

    def save(self, *args, **kwargs):
        # Auto-calculate weekEnd if not provided
        if self.weekStart and not self.weekEnd:
            self.weekEnd = self.weekStart + timedelta(days=6)
        super().save(*args, **kwargs)


class MonthlySummary(models.Model):
    """Stores aggregated monthly meals per month/year"""
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveIntegerField()
    totalMeals = models.PositiveIntegerField()

    class Meta:
        unique_together = ('month', 'year')
        verbose_name_plural = "Monthly Summaries"
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.month}/{self.year} - {self.totalMeals} meals"


class Category(models.Model):
    """General category for stock items"""
    category_no = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["category_no"]

    def __str__(self):
        return self.description


class StockItem(models.Model):
    """Stock item with unit and optional size"""
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=20, default="KG")
    size = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

class WeeklyStockMovement(models.Model):
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    week_number = models.PositiveIntegerField()
    
    # Existing fields
    total_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_issued = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extern_issues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # New fields for stock balancing
    start_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    end_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # U/PR field
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def calculated_end_stock(self):
        """Calculate what the end stock should be"""
        return self.start_stock + self.total_received - self.total_issued - self.extern_issues
    
    @property
    def stock_variance(self):
        """Difference between calculated and actual end stock"""
        return self.calculated_end_stock - self.end_stock
    
    @property
    def needs_attention(self):
        """Flag if stock variance is significant"""
        return abs(self.stock_variance) > 0.1  # More than 0.1 variance

class Expenses(models.Model):
    """Monthly expenses by category"""
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveIntegerField()
    budgetedExpense = models.DecimalField(max_digits=12, decimal_places=2)
    actualExpense = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="expenses")

    class Meta:
        unique_together = ('month', 'year', 'category')
        ordering = ["-year", "-month", "category"]
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.category.description} - {self.month}/{self.year}"

    @property
    def variance(self):
        return self.budgetedExpense - self.actualExpense


class FormG(models.Model):
    """Form G - Budget tracking"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="form_g_entries")
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900)])
    month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])

    annual_budget = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    week1_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    week2_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    week3_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    week4_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    week5_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        unique_together = ("category", "month", "year")
        ordering = ["-year", "-month", "category__description"]
        verbose_name = "Form G"
        verbose_name_plural = "Form G Entries"

    @property
    def expense_for_month(self):
        items = [
            self.week1_expense,
            self.week2_expense,
            self.week3_expense,
            self.week4_expense,
            self.week5_expense,
        ]
        return sum((i or Decimal("0.00") for i in items), Decimal("0.00"))

    @property
    def underspent(self):
        return (self.monthly_budget or Decimal("0.00")) - self.expense_for_month

    def __str__(self):
        return f"Form G - {self.category.description} ({self.month}/{self.year})"


class RationAllowance(models.Model):
    """Ration allowance limits per category"""
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    min_allowance = models.DecimalField(max_digits=8, decimal_places=3)
    max_allowance = models.DecimalField(max_digits=8, decimal_places=3)
    unit = models.CharField(max_length=20, default="kg")
    per = models.CharField(max_length=20, default="day")

    class Meta:
        verbose_name_plural = "Ration Allowances"

    def __str__(self):
        return f"{self.category} ({self.min_allowance}-{self.max_allowance} {self.unit}/{self.per})"


class FormH(models.Model):
    """Form H - Ration usage summary"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    week1_usage = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    week2_usage = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    week3_usage = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    week4_usage = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    week5_usage = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    total_usage = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    avg_per_person_per_day = models.DecimalField(max_digits=8, decimal_places=3, default=0)

    class Meta:
        unique_together = ("category", "month", "year")
        verbose_name = "Form H"
        verbose_name_plural = "Form H Entries"
        ordering = ["-year", "-month", "category"]

    @property
    def adjusted_total_usage(self):
        return self.total_usage

    def __str__(self):
        return f"{self.category} ({self.month}/{self.year})"
    
class AnnualSummary(models.Model):
    """FORM X - Annual feeding, expenditure and ration summary"""
    year = models.PositiveIntegerField(unique=True)
    total_meals_served = models.IntegerField(default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_cost_per_meal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Annual Summaries"
        ordering = ["-year"]
    
    def __str__(self):
        return f"Annual Summary - {self.year}"