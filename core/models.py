from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone


class Menu(models.Model):
    name = models.CharField(max_length=100)
    items = models.ManyToManyField('FoodItem')  
    dietary_notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    CATEGORY_CHOICES = [
        ('Diabetic', 'Diabetic'),
        ('Non-Diabetic', 'Non-Diabetic'),
    ]

    patient_number = models.CharField(max_length=20, unique=True)
    dietary_requirement = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    menu = models.ForeignKey('Menu', on_delete=models.SET_NULL, null=True, blank=True)
    date_served = models.DateField(default=timezone.now)
    


    def __str__(self):
        return f"{self.patient_number} ({self.category})"

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Budget(models.Model):
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Budget (R{self.allocated_amount})"

    @property
    def remaining_amount(self):
        return self.allocated_amount - self.used_amount



class InventoryTransaction(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    transaction_type = models.CharField(max_length=10, choices=[('IN', 'Received'), ('OUT', 'Issued')])
    date = models.DateField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == 'OUT':
            self.total_cost = Decimal(self.food_item.unit_price) * Decimal(self.quantity)

            if self.budget:
                if self.budget.used_amount + self.total_cost > self.budget.allocated_amount:
                    raise ValidationError("This transaction exceeds the allocated budget.")

        super().save(*args, **kwargs)

        if self.transaction_type == 'OUT' and self.budget:
            Budget.objects.filter(pk=self.budget.pk).update(
                used_amount=F('used_amount') + self.total_cost
            )

class FoodItemUsage(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity_used = models.FloatField()
    date_used = models.DateField() 

