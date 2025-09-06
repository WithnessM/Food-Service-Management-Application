from django.urls import path
from . import views

urlpatterns = [

    # Authentication & Dashboard... 
    
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # Meals 
    path("meals/", views.MealListView.as_view(), name="meals_list"),
    path("meals/add/", views.MealCreateView.as_view(), name="meal_create"),
    path("meals/<int:pk>/edit/", views.MealUpdateView.as_view(), name="meal_update"),
    path("meals/<int:pk>/delete/", views.MealDeleteView.as_view(), name="meal_delete"),

    # Recipients
    path("recipients/", views.RecipientListView.as_view(), name="recipients_list"),
    path("recipients/add/", views.RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/edit/", views.RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/delete/", views.RecipientDeleteView.as_view(), name="recipient_delete"),

    #Weekly Meals & Summaries 
    path("meals/weekly/", views.weekly_meals, name="weekly_meals"),
    path("meals/weekly/<int:year>/<int:week>/", views.weekly_summary, name="weekly_summary"),

    # Monthly Summaries 
    path("meals/monthly/<int:year>/<int:month>/", views.monthly_summary, name="monthly_summary"),
    path("meals/monthly/select/", views.monthly_summary_select, name="monthly_summary_select"),

    # Categories 
    path("categories/", views.category_list, name="categories"),
    path("categories/add/", views.category_add, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    # Stock 
    path("stock/", views.stock_list, name="stock_list"),
    path("stock/add/", views.stock_item_add, name="stock_item_add"),
    path("stock/<int:pk>/edit/", views.stock_item_edit, name="stock_item_edit"),
    path("stock/<int:pk>/delete/", views.stock_item_delete, name="stock_item_delete"),

    # Stock Movements
    path("stock/movements/", views.stock_movement_list, name="stock_movement_list"),
    path("stock/movements/add/", views.stock_movement_add, name="stock_movement_add"),
    path("movements/<int:pk>/edit/", views.stock_movement_edit, name="stock_movement_edit"),
    path("movements/<int:pk>/delete/", views.stock_movement_delete, name="stock_movement_delete"),

   #For expoting the reports
    # Monthly summary Excel export
    path(
        'monthly_summary/export/excel/<int:year>/<int:month>/',
        views.export_monthly_summary_excel,
        name='export_monthly_excel'
    ),

    # Weekly summary Excel export
    path(
        'weekly_summary/export/excel/<int:year>/<int:week>/',
        views.export_weekly_summary_excel,
        name='export_weekly_excel'
    ),

    path("weekly_summary/preview/<int:year>/<int:week>/", 
     views.weekly_summary_preview, 
     name="weekly_summary_preview"),

    path("monthly_summary/preview/<int:year>/<int:month>/",
     views.monthly_summary_preview,
     name="monthly_summary_preview"),

     # Stock Movement Preview
    path('stock-movement/preview/', views.stock_movement_preview, name='stock_movement_preview'),

    # Export Stock Excel
    path('stock-movement/export/', views.export_stock_excel, name='export_stock_excel'),

    # (Optional) Other stock-related URLs
    path('stock-movement/', views.stock_movement_list, name='stock_movement_list'),



]
