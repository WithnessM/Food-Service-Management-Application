from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication (login & logout do NOT require login)
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Protected routes (require login)
    path('home/', login_required(views.home), name='home'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),

    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'),
         name='password_reset'),
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),
         name='password_reset_complete'),

    # Meals - Keep only list view and remove individual CRUD
    path("meals/", login_required(views.MealListView.as_view()), name="meals_list"),
    # REMOVED: path("meals/add/", login_required(views.MealCreateView.as_view()), name="meal_create"),
    # REMOVED: path("meals/<int:pk>/edit/", login_required(views.MealUpdateView.as_view()), name="meal_update"),
    # REMOVED: path("meals/<int:pk>/delete/", login_required(views.MealDeleteView.as_view()), name="meal_delete"),

    # Recipients
    path("recipients/", login_required(views.RecipientListView.as_view()), name="recipients_list"),
    path("recipients/add/", login_required(views.RecipientCreateView.as_view()), name="recipient_create"),
    path("recipients/<int:pk>/edit/", login_required(views.RecipientUpdateView.as_view()), name="recipient_update"),
    path("recipients/<int:pk>/delete/", login_required(views.RecipientDeleteView.as_view()), name="recipient_delete"),

    # Weekly Meals & Summaries 
    path("meals/weekly/", login_required(views.weekly_meals), name="weekly_meals"),
    path("meals/weekly/<int:year>/<int:week>/", login_required(views.weekly_summary), name="weekly_summary"),

    # Monthly Summaries 
    path("meals/monthly/<int:year>/<int:month>/", login_required(views.monthly_summary), name="monthly_summary"),
    path("meals/monthly/select/", login_required(views.monthly_summary_select), name="monthly_summary_select"),

    # Categories 
    path("categories/", login_required(views.category_list), name="categories"),
    path("categories/add/", login_required(views.category_add), name="category_add"),
    path("categories/<int:pk>/edit/", login_required(views.category_edit), name="category_edit"),
    path("categories/<int:pk>/delete/", login_required(views.category_delete), name="category_delete"),

    # Stock 
    path("stock/", login_required(views.stock_list), name="stock_list"),
    path("stock/add/", login_required(views.stock_item_add), name="stock_item_add"),
    path("stock/<int:pk>/edit/", login_required(views.stock_item_edit), name="stock_item_edit"),
    path("stock/<int:pk>/delete/", login_required(views.stock_item_delete), name="stock_item_delete"),

    # Stock Movements
    path("stock/movements/", login_required(views.stock_movement_list), name="stock_movement_list"),
    path("stock/movements/add/", login_required(views.stock_movement_add), name="stock_movement_add"),
    path("movements/<int:pk>/edit/", login_required(views.stock_movement_edit), name="stock_movement_edit"),
    path("movements/<int:pk>/delete/", login_required(views.stock_movement_delete), name="stock_movement_delete"),

    # Reports & Exports (protected)
    path(
        'monthly_summary/export/excel/<int:year>/<int:month>/',
        login_required(views.export_monthly_summary_excel),
        name='export_monthly_excel'
    ),
    path(
        'weekly_summary/export/excel/<int:year>/<int:week>/',
        login_required(views.export_weekly_summary_excel),
        name='export_weekly_excel'
    ),
    path(
        "weekly_summary/preview/<int:year>/<int:week>/", 
        login_required(views.weekly_summary_preview), 
        name="weekly_summary_preview"
    ),
    path(
        "monthly_summary/preview/<int:year>/<int:month>/",
        login_required(views.monthly_summary_preview),
        name="monthly_summary_preview"
    ),

    # Stock Movement Preview & Export
    path('stock-movement/preview/', login_required(views.stock_movement_preview), name='stock_movement_preview'),
    path('stock-movement/export/', login_required(views.export_stock_excel), name='export_stock_excel'),

    # Form G
    path('form-g/', login_required(views.form_g_list), name='form_g_list'),
    path('form-g/add/', login_required(views.form_g_add), name='form_g_add'),
    path('form-g/<int:year>/<int:month>/preview/', login_required(views.form_g_monthly_preview), name='form_g_monthly_preview'),
    path('form-g/<int:year>/<int:month>/export/', login_required(views.export_form_g_monthly_excel), name='export_form_g_monthly_excel'),

    # Form H
    path("formh/<int:year>/<int:month>/", login_required(views.generate_formh_summary), name="formh_summary"),
    path("formh/preview/<int:year>/<int:month>/", login_required(views.form_h_monthly_preview), name="form_h_preview"),
    path("formh/export/<int:year>/<int:month>/", login_required(views.export_form_h_monthly_excel), name="form_h_export_excel"),

    # New Functionalities
    path('annual-summary/<int:year>/', login_required(views.annual_summary), name='annual_summary'),
    path('annual-summary/', login_required(views.annual_summary), name='annual_summary_current'),
    path('stock-variance-report/', login_required(views.stock_variance_report), name='stock_variance_report'),
]