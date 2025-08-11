#from django.shortcuts import render

# Create your views here.


from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import EmailAuthenticationForm



def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'core/main.html')


def logout_view(request):
    logout(request)
    return redirect('login')


from django.shortcuts import render, redirect
from .models import FoodItem
from .forms import FoodItemForm

def add_food_item(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = FoodItemForm()
    return render(request, 'core/add_food.html', {'form': form})

from .forms import InventoryTransactionForm
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def add_inventory_item(request):
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = InventoryTransactionForm()
    return render(request, 'core/add_inventory_item.html', {'form': form})

from .models import Patient
from .forms import PatientForm



@login_required
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PatientForm()
    return render(request, 'core/add_patient.html', {'form': form})

@login_required
def list_patients(request):
    patients = Patient.objects.all()
    return render(request, 'core/list_patients.html', {'patients': patients})


from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from django.shortcuts import render
from .models import Patient

@login_required
def patient_served_report(request):
    # Monthly totals
    monthly_totals = Patient.objects.annotate(
        month=TruncMonth('date_served')
    ).values('month', 'category').annotate(total=Count('id')).order_by('month')

    # Quarterly totals
    quarterly_totals = Patient.objects.annotate(
        quarter=TruncQuarter('date_served')
    ).values('quarter', 'category').annotate(total=Count('id')).order_by('quarter')

    # Yearly totals
    yearly_totals = Patient.objects.annotate(
        year=TruncYear('date_served')
    ).values('year', 'category').annotate(total=Count('id')).order_by('year')

    context = {
        'monthly_totals': monthly_totals,
        'quarterly_totals': quarterly_totals,
        'yearly_totals': yearly_totals,
    }
    return render(request, 'core/patient_served_report.html', context)



from .models import Menu
from .forms import MenuForm

@login_required
def add_menu(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_menus')
    else:
        form = MenuForm()
    return render(request, 'core/add_menu.html', {'form': form})

@login_required
def list_menus(request):
    menus = Menu.objects.all()
    return render(request, 'core/list_menus.html', {'menus': menus})

from .models import Budget
from django.db.models import F

@login_required
def budget_dashboard(request):
    budgets = Budget.objects.all()
    return render(request, 'core/budget_dashboard.html', {'budgets': budgets})


from django.contrib.auth.decorators import login_required

@login_required
def your_view(request):
    pass

from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')


from .forms import FoodItemUsageForm
from .models import FoodItemUsage

@login_required
def add_food_usage(request):
    if request.method == 'POST':
        form = FoodItemUsageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = FoodItemUsageForm()
    return render(request, 'core/add_food_usage.html', {'form': form})


from decimal import Decimal
from django.db.models import Sum
from .models import FoodItemUsage

@login_required
def cost_per_meal_day(request):
    total_cost = Decimal('0.00')
    usages = FoodItemUsage.objects.select_related('food_item')

    for usage in usages:
        total_cost += Decimal(str(usage.quantity_used)) * usage.food_item.unit_price

    total_patients = Patient.objects.count()
    cost_per_patient = total_cost / total_patients if total_patients > 0 else Decimal('0.00')

    return render(request, 'core/report_cost.html', {
        'total_cost': round(total_cost, 2),
        'total_patients': total_patients,
        'cost_per_patient': round(cost_per_patient, 2)
    })




from .models import InventoryTransaction
from django.db.models import Sum
from django.db import models

@login_required
def stock_balance(request):
    balance = (
        InventoryTransaction.objects
        .values('food_item__name')
        .annotate(
            total_in=Sum('quantity', filter=models.Q(transaction_type='IN')),
            total_out=Sum('quantity', filter=models.Q(transaction_type='OUT'))
        )
    )

    return render(request, 'core/report_stock_balance.html', {'balance': balance})


from .forms import BudgetForm
@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('budget_dashboard')
    else:
        form = BudgetForm()
    return render(request, 'core/add_budget.html', {'form': form})



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .forms import UpdateUsedAmountForm


@login_required
def update_used_amount(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id)
    if request.method == 'POST':
        form = UpdateUsedAmountForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('budget_dashboard')
    else:
        form = UpdateUsedAmountForm(instance=budget)
    return render(request, 'core/update_used_amount.html', {'form': form, 'budget': budget})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id)
    if request.method == 'POST':
        budget.delete()
        return redirect('budget_dashboard')
    return render(request, 'core/delete_budget_confirm.html', {'budget': budget})


from django.db.models import F
from django.contrib.auth.decorators import login_required


@login_required
def budget_report(request):
    budgets = Budget.objects.all()
    return render(request, 'core/budget_report.html', {'budgets': budgets})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="budget_report.pdf"'

   
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        HTML(string=html_string).write_pdf(target=tmp.name)
        tmp.seek(0)
        response.write(tmp.read())

    return response

from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import render_to_string

@login_required
def budget_report_pdf(request):
    budgets = Budget.objects.all()
    html_string = render_to_string('core/budget_report_pdf.html', {'budgets': budgets})

    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="budget_report.pdf"'
    return response


from .models import Patient
from django.contrib.auth.decorators import login_required

@login_required
def patient_meal_distribution_report(request):
    patients = Patient.objects.select_related('menu').all()
    return render(request, 'core/patient_meal_report.html', {'patients': patients})

from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse

@login_required
def patient_meal_report_pdf(request):
    patients = Patient.objects.select_related('menu').all()
    html_string = render_to_string('core/patient_meal_report_pdf.html', {'patients': patients})

    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="patient_meal_report.pdf"'
    return response

from django.db.models import Sum
from .models import InventoryTransaction, Patient

@login_required
def cost_per_meal_report(request):
    total_used = InventoryTransaction.objects.filter(transaction_type='OUT').aggregate(
        total=Sum('total_cost'))['total'] or 0
    patient_count = Patient.objects.count()
    cost_per_meal = (total_used / patient_count) if patient_count > 0 else 0

    context = {
        'total_cost': total_used,
        'patient_count': patient_count,
        'cost_per_meal': round(cost_per_meal, 2)
    }
    return render(request, 'core/cost_per_meal_report.html', context)

@login_required
def cost_per_meal_report_pdf(request):
    total_used = InventoryTransaction.objects.filter(transaction_type='OUT').aggregate(
        total=Sum('total_cost'))['total'] or 0
    patient_count = Patient.objects.count()
    cost_per_meal = (total_used / patient_count) if patient_count > 0 else 0

    context = {
        'total_cost': total_used,
        'patient_count': patient_count,
        'cost_per_meal': round(cost_per_meal, 2)
    }

    html_string = render_to_string('core/cost_per_meal_report_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="cost_per_meal_report.pdf"'

    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        HTML(string=html_string).write_pdf(target=tmp.name)
        tmp.seek(0)
        response.write(tmp.read())

    return response
