"""
Admin configuration for expenses app.

Registers models in Django admin panel for easy management.
"""
from django.contrib import admin
from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    list_display = ['name', 'icon', 'color']
    search_fields = ['name']
    list_filter = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Admin interface for Expense model."""
    list_display = ['user', 'description', 'amount', 'category', 'date', 'created_at']
    list_filter = ['category', 'date', 'user']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
