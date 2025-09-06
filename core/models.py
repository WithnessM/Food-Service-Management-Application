from django.db import models


# Meals

class MealRecipient(models.Model):
    
    #Represents a person receiving meals

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Meal Recipient"
        verbose_name_plural = "Meal Recipients"

    def __str__(self):
        return self.name


class Meals(models.Model):
    #Represents a meal entry for a recipient

    weekStart = models.DateField()
    weekEnd = models.DateField()
    mealDate = models.DateField()
    quantity = models.IntegerField()

    CATEGORY_CHOICES = [
        ("O", "Breakfast"),
        ("M", "Lunch"),
        ("A", "Dinner"),
        ("N", "Night Snack"),
    ]
    mealCategory = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    mealsFor = models.ForeignKey(MealRecipient, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.mealDate} - {self.get_mealCategory_display()} for {self.mealsFor} ({self.quantity})"


class MonthlySummary(models.Model):
    #Stores aggregated monthly meals per month/year

    month = models.IntegerField()
    year = models.IntegerField()
    totalMeals = models.IntegerField()

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"{self.month}/{self.year} - {self.totalMeals} meals"


# Stock
class StockCategory(models.Model):
    #Category for stock items used in budgeting and expenses

    code = models.CharField(max_length=10, unique=True)
    categoryName = models.CharField(max_length=100)
    rationGroupNo = models.IntegerField()

    def __str__(self):
        return f"{self.code} - {self.categoryName}"


class Category(models.Model):
    #General category for stock items

    category_no = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description


class StockItem(models.Model):
    #Stock item with unit and optional size

    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=20, default="KG")
    size = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class WeeklyStockMovement(models.Model):
    #Tracks weekly movement of stock items


    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    week_number = models.PositiveIntegerField()
    total_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_issued = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extern_issues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_item.name} - Week {self.week_number}"


# Expense and Buget.....

class Expenses(models.Model):
    #Tracks monthly budgeted vs actual expenses for a stock category

    month = models.IntegerField()
    year = models.IntegerField()
    budgetedExpense = models.DecimalField(max_digits=12, decimal_places=2)
    actualExpense = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(StockCategory, on_delete=models.CASCADE, related_name="expenses")

    def __str__(self):
        return f"{self.category.categoryName} - {self.month}/{self.year}"


class RationAllowance(models.Model):
    #Tracks ration allowances and actual usage per category

    month = models.IntegerField()
    year = models.IntegerField()
    min_Allowance = models.DecimalField(max_digits=10, decimal_places=2)
    max_Allowance = models.DecimalField(max_digits=10, decimal_places=2)
    actualUsage = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(StockCategory, on_delete=models.CASCADE, related_name="rationAllowances")

    def __str__(self):
        return f"{self.category.categoryName} - {self.month}/{self.year}"


class AnnualSummary(models.Model):
    # sum total summary per year combining meals, expenses and rations.
    year = models.IntegerField()
    totalFeeding = models.IntegerField()
    totalExpenditure = models.DecimalField(max_digits=12, decimal_places=2)
    totalRations = models.DecimalField(max_digits=12, decimal_places=2)

    summary = models.ForeignKey(MonthlySummary, on_delete=models.CASCADE, related_name="annualSummaries")
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name="annualSummaries")
    ration = models.ForeignKey(RationAllowance, on_delete=models.CASCADE, related_name="annualSummaries")

    def __str__(self):
        return f"Annual Summary {self.year}"
