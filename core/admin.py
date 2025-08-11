

#..
from django.contrib import admin
from .models import (
     Patient, FoodItem, Budget,
    InventoryTransaction, FoodItemUsage, Menu
)


admin.site.register(Patient)
admin.site.register(FoodItem)
admin.site.register(Budget)
admin.site.register(InventoryTransaction)
admin.site.register(FoodItemUsage)
admin.site.register(Menu)

