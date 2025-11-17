from django.contrib import admin
from .models import Stock, Price

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'created_at')
    search_fields = ('symbol', 'name')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'close', 'adjusted_close', 'volume')
    list_filter = ('stock',)
    date_hierarchy = 'date'
# Register your models here.
