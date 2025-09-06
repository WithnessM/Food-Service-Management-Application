from django.contrib import admin
from .models import (
    Meals, MonthlySummary, StockCategory, StockItem,
    Expenses, RationAllowance, AnnualSummary
)


# Simple registration to enable Django admin interface

admin.site.register(Meals)              
admin.site.register(MonthlySummary)    
admin.site.register(StockCategory)      
admin.site.register(StockItem)          
admin.site.register(Expenses)           
admin.site.register(RationAllowance)    
admin.site.register(AnnualSummary)      
