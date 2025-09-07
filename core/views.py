
from datetime import date, timedelta
import calendar
from collections import defaultdict


from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse


from .models import (
    Meals, MealRecipient, MonthlySummary,
    Category, StockItem, WeeklyStockMovement
)
from .forms import (
    MealsForm, WeeklyMealsForm, MonthlySummaryForm,
    CategoryForm, StockItemForm, WeeklyStockMovementForm
)

# For  Authentication 

def login_view(request):
    #Handles user login using Django's built in AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    #Logs out the user and redirects to login page

    logout(request)
    return redirect('login')


from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    today = date.today()
    year = today.year
    week = today.isocalendar()[1]  
    
    return render(request, "core/main.html", {
        "reports": "Reports",  
        "year": year,
        "month": today.month,
        "week": week,
    })


def home(request):
    
    return render(request, 'core/home.html')


# For Meals
class MealListView(ListView):
    model = Meals
    template_name = "core/meals_list.html"
    context_object_name = "meals"
    ordering = ["-mealDate"]  


class MealCreateView(CreateView):
    model = Meals
    form_class = MealsForm
    template_name = "core/meal_form.html"
    success_url = reverse_lazy("meals_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Meal"
        return context


class MealUpdateView(UpdateView):
    model = Meals
    form_class = MealsForm
    template_name = "core/meal_form.html"
    success_url = reverse_lazy("meals_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Edit Meal"
        return context


class MealDeleteView(DeleteView):
    model = Meals
    template_name = "core/meal_confirm_delete.html"
    success_url = reverse_lazy("meals_list")
    context_object_name = "meal"


# For meal recipients

class RecipientListView(ListView):
    model = MealRecipient
    template_name = "core/recipients_list.html"
    context_object_name = "recipients"
    ordering = ["name"]


class RecipientCreateView(CreateView):
    model = MealRecipient
    fields = ["name"]
    template_name = "core/recipient_form.html"
    success_url = reverse_lazy("recipients_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Recipient"
        return context


class RecipientUpdateView(UpdateView):
    model = MealRecipient
    fields = ["name"]
    template_name = "core/recipient_form.html"
    success_url = reverse_lazy("recipients_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Edit Recipient"
        return context


class RecipientDeleteView(DeleteView):
    model = MealRecipient
    template_name = "core/meal_confirm_delete.html"
    success_url = reverse_lazy("recipients_list")
    context_object_name = "recipient"


# For Weekly Meals..

def weekly_meals(request):
    #This Handles weekly meal creation for all recipients
    
    recipients = MealRecipient.objects.all()
    meal_types = Meals.CATEGORY_CHOICES
    days = range(7)

    if request.method == "POST":
        form = WeeklyMealsForm(request.POST)
        if form.is_valid():
            week_start = form.cleaned_data["weekStart"]
            week_end = week_start + timedelta(days=6)

            # Loop through each day and recipient to create meals
            for day in days:
                meal_date = week_start + timedelta(days=day)
                for recipient in recipients:
                    for code, _ in meal_types:
                        field_name = f"{day}_{recipient.id}_{code}"
                        quantity = form.cleaned_data.get(field_name, 0) or 0
                        if quantity > 0:
                            Meals.objects.create(
                                weekStart=week_start,
                                weekEnd=week_end,
                                mealDate=meal_date,
                                mealCategory=code,
                                mealsFor=recipient,
                                quantity=quantity,
                            )
            return redirect(
                "weekly_summary",
                year=week_start.year,
                week=week_start.isocalendar()[1]
            )
    else:
        form = WeeklyMealsForm()

    # Prepare field matrix for template rendering
    field_matrix = [
        [f"{day}_{recipient.id}_{code}" for recipient in recipients for code, _ in meal_types]
        for day in days
    ]

    return render(request, "core/weekly_meals.html", {
        "form": form,
        "recipients": recipients,
        "meal_types": meal_types,
        "days": days,
        "field_matrix": field_matrix,
    })


def weekly_summary(request, year, week):
    #This Generates a weekly summary table of meals per recipient

    start_date = date.fromisocalendar(year, week, 1)
    end_date = start_date + timedelta(days=6)

    recipients = MealRecipient.objects.all()
    meal_types = dict(Meals.CATEGORY_CHOICES)

    summary = []
    for recipient in recipients:
        row = {"recipient": recipient.name, "meals": []}
        total = 0
        for day in range(7):
            meal_date = start_date + timedelta(days=day)
            day_data = {}
            for code, _ in Meals.CATEGORY_CHOICES:
                qty = Meals.objects.filter(
                    mealDate=meal_date,
                    mealsFor=recipient,
                    mealCategory=code
                ).aggregate(Sum("quantity"))["quantity__sum"] or 0
                day_data[code] = qty
                total += qty
            row["meals"].append(day_data)
        row["total"] = total
        summary.append(row)

    return render(request, "core/weekly_summary.html", {
        "summary": summary,
        "start_date": start_date,
        "end_date": end_date,
        "meal_types": meal_types,
    })


# For monthly Summary
def monthly_summary(request, year=None, month=None):
    # Generates monthly meal summary for all recipients
    
    today = date.today()
    year = year or today.year
    month = month or today.month

    num_days = calendar.monthrange(year, month)[1]
    recipients = MealRecipient.objects.all()
    meal_types = dict(Meals.CATEGORY_CHOICES)

    summary = []
    for recipient in recipients:
        row = {"recipient": recipient.name, "meals": []}
        total = 0
        for day in range(1, num_days + 1):
            meal_date = date(year, month, day)
            day_data = {}
            for code, _ in Meals.CATEGORY_CHOICES:
                qty = Meals.objects.filter(
                    mealDate=meal_date,
                    mealsFor=recipient,
                    mealCategory=code
                ).aggregate(Sum("quantity"))["quantity__sum"] or 0
                day_data[code] = qty
                total += qty
            row["meals"].append(day_data)
        row["total"] = total
        summary.append(row)

    return render(request, "core/monthly_summary.html", {
        "summary": summary,
        "year": year,
        "month": month,
        "meal_types": meal_types,
        "num_days": num_days,
    })


class MonthSelectForm(forms.Form):
    # Form to select a month and year for monthly summary
    year = forms.IntegerField(
        initial=date.today().year,
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "width:100px; display:inline-block;"})
    )
    month = forms.IntegerField(
        min_value=1, max_value=12,
        initial=date.today().month,
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "width:80px; display:inline-block;"})
    )


def monthly_summary_select(request):
    #View to select month orr year and redirect to monthly summary

    if request.method == "POST":
        form = MonthSelectForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data["year"]
            month = form.cleaned_data["month"]
            return redirect("monthly_summary", year=year, month=month)
    else:
        form = MonthSelectForm()

    return render(request, "core/monthly_summary_select.html", {"form": form})


### ...For  Managing the Stock...

# Category CRUD

def category_list(request):
    categories = Category.objects.all().order_by("category_no")
    return render(request, "core/categories.html", {"categories": categories})


def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("categories")
        
    else:
        form = CategoryForm()
    return render(request, "core/form.html", {"form": form, "title": "Add Category"})


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("categories")
        

    else:
        form = CategoryForm(instance=category)
    return render(request, "core/form.html", {"form": form, "title": "Edit Category"})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("categories")
    return render(request, "core/confirm_delete.html", {"object": category, "title": "Delete Category"})


# Stock Item CRUD
def stock_list(request):
    stock_items = StockItem.objects.select_related("category").all().order_by("category__category_no", "name")
    return render(request, "core/Stock_list.html", {"stock_items": stock_items})


def stock_item_add(request):
    if request.method == "POST":
        form = StockItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("stock_list")
        
    else:
        form = StockItemForm()
    return render(request, "core/form.html", {"form": form, "title": "Add Stock Item"})


def stock_item_edit(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    if request.method == "POST":
        form = StockItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("stock_list")
    else:
        form = StockItemForm(instance=item)
    return render(request, "core/form.html", {"form": form, "title": "Edit Stock Item"})


def stock_item_delete(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    if request.method == "POST":
        item.delete()
        return redirect("stock_list")
    return render(request, "core/confirm_delete.html", {"object": item, "title": "Delete Stock Item"})


# For Weeeklu stock movement
def stock_movement_list(request):
    movements = WeeklyStockMovement.objects.select_related("stock_item", "stock_item__category").all()
    return render(request, "core/stock_movement_list.html", {"movements": movements})


def stock_movement_add(request):
    if request.method == "POST":
        form = WeeklyStockMovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("stock_movement_list")
    else:
        form = WeeklyStockMovementForm()
    return render(request, "core/form.html", {"form": form, "title": "Add Stock Movement"})


def stock_movement_edit(request, pk):
    movement = get_object_or_404(WeeklyStockMovement, pk=pk)
    if request.method == "POST":
        form = WeeklyStockMovementForm(request.POST, instance=movement)
        if form.is_valid():
            form.save()
            return redirect("stock_movement_list")
    else:
        form = WeeklyStockMovementForm(instance=movement)
    return render(request, "core/form.html", {"form": form, "title": "Edit Stock Movement"})


def stock_movement_delete(request, pk):
    movement = get_object_or_404(WeeklyStockMovement, pk=pk)
    if request.method == "POST":
        movement.delete()
        return redirect("stock_movement_list")
    return render(request, "core/confirm_delete.html", {"object": movement, "title": "Delete Stock Movement"})


def stock_weekly_summary(request):
    # This Generates weekly stock summary based on selected week
    weeks = WeeklyStockMovement.objects.values_list("week_number", flat=True).distinct().order_by("week_number")
    selected_week = int(request.GET.get("week_number", weeks.first() if weeks else 0))

    summary = []
    totals = {}

    if selected_week:
        summary = (
            WeeklyStockMovement.objects
            .filter(week_number=selected_week)
            .values("stock_item__category__description")
            .annotate(
                total_received=Sum("total_received"),
                total_issued=Sum("total_issued"),
                total_extern=Sum("extern_issues"),
                total_cost=Sum("cost")
            )
            .order_by("stock_item__category__description")
        )

        totals = WeeklyStockMovement.objects.filter(week_number=selected_week).aggregate(
            total_received=Sum("total_received"),
            total_issued=Sum("total_issued"),
            total_extern=Sum("extern_issues"),

            total_cost=Sum("cost")
        )

    return render(request, "core/Stock Weekly_summary.html", {
        "summary": summary,
        "totals": totals,
        "weeks": weeks,
        "selected_week": selected_week,
    })


#------EXPORTING EXCEL REPORRTS----- FROM CHATGPT-5.....

from datetime import date, timedelta
from django.shortcuts import render
from .models import Meals

def weekly_summary_preview(request, year, week):
    # Convert year/week to start and end dates
    start_date = date.fromisocalendar(year, week, 1)  # Monday
    end_date = start_date + timedelta(days=6)          # Sunday

    # Fetch meals for the week
    meals = Meals.objects.filter(mealDate__range=[start_date, end_date])

    context = {
        "year": year,
        "week": week,
        "meals": meals,
        "start_date": start_date,
        "end_date": end_date,
        "month_name": start_date.strftime('%B'),  # Month of the first day
        "date_range": f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}",
    }
    return render(request, "core/weekly_summary_preview.html", context)

from datetime import date
from django.shortcuts import render
from .models import Meals

def monthly_summary_preview(request, year, month):
    # Get first and last day of month
    first_day = date(year, month, 1)
    last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)

    meals = Meals.objects.filter(mealDate__range=[first_day, last_day])

    context = {
        "year": year,
        "month": month,
        "meals": meals,
        "month_name": first_day.strftime('%B'),
        "date_range": f"{first_day.strftime('%d %b')} - {last_day.strftime('%d %b %Y')}",
    }
    return render(request, "core/monthly_summary_preview.html", context)

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from datetime import date, timedelta
from django.db.models import Sum
from .models import Meals, MealRecipient

def export_weekly_summary_excel(request, year, week):
    start_date = date.fromisocalendar(year, week, 1)
    end_date = start_date + timedelta(days=6)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Week_{week}_{year}"

    # Create headers with actual dates
    headers = ["Recipient"]
    meal_types = [code for code, _ in Meals.CATEGORY_CHOICES]
    for day in range(7):
        current_date = start_date + timedelta(days=day)
        for mt in meal_types:
            headers.append(f"{current_date.strftime('%d %b')} {mt}")
    headers.append("Total")
    ws.append(headers)

    recipients = MealRecipient.objects.all()
    for recipient in recipients:
        row = [recipient.name]
        total = 0
        for day in range(7):
            meal_date = start_date + timedelta(days=day)
            for code, _ in Meals.CATEGORY_CHOICES:
                qty = Meals.objects.filter(
                    mealDate=meal_date,
                    mealsFor=recipient,
                    mealCategory=code
                ).aggregate(total=Sum("quantity"))["total"] or 0
                row.append(qty)
                total += qty
        row.append(total)
        ws.append(row)

    # Adjust column widths
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename=Weekly_Summary_Week{week}_{year}.xlsx'
    wb.save(response)
    return response

import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from datetime import date, timedelta
from django.db.models import Sum
from .models import Meals, MealRecipient

def export_monthly_summary_excel(request, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month

    first_day = date(year, month, 1)
    last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    num_days = (last_day - first_day).days + 1

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{first_day.strftime('%B')}-{year} Summary"

    # Headers
    headers = ["Recipient"]
    recipients = MealRecipient.objects.all()
    meal_types = [code for code, _ in Meals.CATEGORY_CHOICES]

    for day in range(num_days):
        current_date = first_day + timedelta(days=day)
        for mt in meal_types:
            headers.append(f"{current_date.strftime('%d %b')} {mt}")
    headers.append("Total")
    ws.append(headers)

    # Fill data
    for recipient in recipients:
        row = [recipient.name]
        total = 0
        for day in range(num_days):
            meal_date = first_day + timedelta(days=day)
            for code, _ in Meals.CATEGORY_CHOICES:
                qty = Meals.objects.filter(
                    mealDate=meal_date,
                    mealsFor=recipient,
                    mealCategory=code
                ).aggregate(total=Sum("quantity"))["total"] or 0
                row.append(qty)
                total += qty
        row.append(total)
        ws.append(row)

    # Adjust column widths
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # Response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename=Monthly_Summary_{first_day.strftime("%b")}_{year}.xlsx'
    wb.save(response)
    return response


from django.db.models import Sum
from .models import WeeklyStockMovement, Category

def stock_movement_preview(request):
    movements = WeeklyStockMovement.objects.select_related(
        "stock_item", "stock_item__category"
    ).all()

    categories = Category.objects.all()
    category_totals = []
    for cat in categories:
        totals = WeeklyStockMovement.objects.filter(
            stock_item__category=cat
        ).aggregate(
            total_received=Sum("total_received"),
            total_issued=Sum("total_issued"),
            total_extern=Sum("extern_issues"),
            total_cost=Sum("cost")
        )
        totals["description"] = cat.description
        category_totals.append(totals)

    grand_totals = WeeklyStockMovement.objects.aggregate(
        total_received=Sum("total_received"),
        total_issued=Sum("total_issued"),
        total_extern=Sum("extern_issues"),
        total_cost=Sum("cost")
    )

    return render(request, "core/stock_movement_preview.html", {
        "movements": movements,
        "category_totals": category_totals,
        "grand_totals": grand_totals
    })


import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.db.models import Sum
from .models import WeeklyStockMovement, StockItem, Category

def export_stock_excel(request):
    wb = openpyxl.Workbook()

    # --- Sheet 1: Stock Movement ---
    ws1 = wb.active
    ws1.title = "Stock Movement"

    headers = [
        "Week Number", "Stock Item", "Category",
        "Total Received", "Total Issued", "External Issues", "Cost"
    ]
    ws1.append(headers)

    movements = WeeklyStockMovement.objects.select_related("stock_item", "stock_item__category").all()
    
    for m in movements:
        ws1.append([
            m.week_number,
            m.stock_item.name,
            m.stock_item.category.description,
            float(m.total_received),
            float(m.total_issued),
            float(m.extern_issues),
            float(m.cost),
        ])

    # --- Totals per Category ---
    categories = Category.objects.all()
    ws1.append([])  # Empty row before totals
    ws1.append(["Totals per Category"])
    ws1.append(["Category", "Total Received", "Total Issued", "External Issues", "Total Cost"])

    for cat in categories:
        cat_totals = WeeklyStockMovement.objects.filter(stock_item__category=cat).aggregate(
            total_received=Sum("total_received"),
            total_issued=Sum("total_issued"),
            total_extern=Sum("extern_issues"),
            total_cost=Sum("cost")
        )
        ws1.append([
            cat.description,
            float(cat_totals["total_received"] or 0),
            float(cat_totals["total_issued"] or 0),
            float(cat_totals["total_extern"] or 0),
            float(cat_totals["total_cost"] or 0),
        ])

    # --- Grand Totals ---
    grand_totals = WeeklyStockMovement.objects.aggregate(
        total_received=Sum("total_received"),
        total_issued=Sum("total_issued"),
        total_extern=Sum("extern_issues"),
        total_cost=Sum("cost")
    )
    ws1.append([])
    ws1.append([
        "GRAND TOTAL",
        "",
        "",
        float(grand_totals["total_received"] or 0),
        float(grand_totals["total_issued"] or 0),
        float(grand_totals["total_extern"] or 0),
        float(grand_totals["total_cost"] or 0),
    ])

    # Adjust column widths
    for col in ws1.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws1.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # --- Sheet 2: Stock Items ---
    ws2 = wb.create_sheet(title="Stock Items")
    items = StockItem.objects.select_related("category").all()
    ws2.append(["Name", "Unit", "Size", "Category"])
    for item in items:
        ws2.append([item.name, item.unit, item.size or "", item.category.description])
    for col in ws2.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws2.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # --- Sheet 3: Categories ---
    ws3 = wb.create_sheet(title="Categories")
    categories = Category.objects.all().order_by("category_no")
    ws3.append(["Category No", "Description"])
    for cat in categories:
        ws3.append([cat.category_no, cat.description])
    for col in ws3.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws3.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # --- Prepare response ---
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="Stock_Summary.xlsx"'
    wb.save(response)
    return response


