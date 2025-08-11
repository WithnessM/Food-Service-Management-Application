from django import forms
from .models import FoodItem, InventoryTransaction


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'unit', 'unit_price']



class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = ['food_item', 'quantity', 'transaction_type', 'budget']
        widgets = {
            'transaction_type': forms.Select(choices=InventoryTransaction._meta.get_field('transaction_type').choices)
        }


from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['patient_number', 'dietary_requirement','category','menu']

from .models import Menu

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'items', 'dietary_notes']
        widgets = {
            'items': forms.CheckboxSelectMultiple()
        }


from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)




from .models import FoodItemUsage

class FoodItemUsageForm(forms.ModelForm):
    class Meta:
        model = FoodItemUsage
        fields = ['food_item', 'quantity_used', 'date_used']

from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['allocated_amount']



class UpdateUsedAmountForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['used_amount']
