from django.contrib import admin
from .models import Portfolio, PortfolioWeight

class PortfolioWeightInline(admin.TabularInline):
    model = PortfolioWeight
    extra = 0

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'target_return', 'created_at')
    inlines = (PortfolioWeightInline,)
    