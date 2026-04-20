"""
Admin configuration for split_expenses app.
"""
from django.contrib import admin
from .models import Group, SharedExpense, Balance


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin interface for Group model."""
    list_display = ['name', 'created_by', 'get_member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'created_by__username']
    filter_horizontal = ['members']


@admin.register(SharedExpense)
class SharedExpenseAdmin(admin.ModelAdmin):
    """Admin interface for SharedExpense model."""
    list_display = ['description', 'amount', 'paid_by', 'group', 'date']
    list_filter = ['group', 'date']
    search_fields = ['description', 'paid_by__username']


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    """Admin interface for Balance model."""
    list_display = ['owed_by', 'owed_to', 'amount', 'is_settled', 'created_at']
    list_filter = ['is_settled', 'created_at']
    search_fields = ['owed_by__username', 'owed_to__username']
