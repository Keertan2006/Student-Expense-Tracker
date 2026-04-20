"""
Admin configuration for budgets app.
"""
from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin interface for Budget model."""
    list_display = ['user', 'category', 'amount', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'category', 'user']
    search_fields = ['user__username']
    date_hierarchy = 'start_date'
