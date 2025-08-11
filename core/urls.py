from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'), 
    path('home/', views.home, name='home'),
    path('add-inventory/', views.add_inventory_item, name='add-inventory'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('logout/', views.logout_view, name='logout'),
    path('add-food/', views.add_food_item, name='add_food'),
    path('patients/', views.list_patients, name='list_patients'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('menus/', views.list_menus, name='list_menus'),
    path('add-menu/', views.add_menu, name='add_menu'),
    path('budget-dashboard/', views.budget_dashboard, name='budget_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('food-usage/add/', views.add_food_usage, name='add_food_usage'),
    path('report/cost-per-meal/', views.cost_per_meal_day, name='cost_per_meal_day'),
    path('report/stock-balance/', views.stock_balance, name='stock_balance'),
    path('add-budget/', views.add_budget, name='add_budget'),
    path('budget/<int:budget_id>/update-used/', views.update_used_amount, name='update_used_amount'),
    path('budget/<int:budget_id>/delete/', views.delete_budget, name='delete_budget'),

    path('reports/budget/', views.budget_report, name='budget_report'),
    path('reports/budget/pdf/', views.budget_report_pdf, name='budget_report_pdf'),
    path('reports/patient-meal/', views.patient_meal_distribution_report, name='patient_meal_report'),
    path('reports/patient-meal/pdf/', views.patient_meal_report_pdf, name='patient_meal_report_pdf'),
    path('reports/cost-per-meal/', views.cost_per_meal_report, name='cost_per_meal_report'),
    path('reports/cost-per-meal/pdf/', views.cost_per_meal_report_pdf, name='cost_per_meal_report_pdf'),
    path('reports/patients-served/', views.patient_served_report, name='patient_served_report'),

    



]
