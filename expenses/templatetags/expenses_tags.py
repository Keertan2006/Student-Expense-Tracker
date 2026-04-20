"""
Custom template tags for expenses app.

Provides template tags for displaying budget alerts and other expense-related data.
"""
from django import template
from budgets.models import Budget
from expenses.models import Expense
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

register = template.Library()


@register.simple_tag
def budget_alert_count(user):
    """
    Get the count of active budget alerts for a user.
    
    Usage in template:
    {% load expenses_tags %}
    {% budget_alert_count user as alert_count %}
    """
    if not user or not user.is_authenticated:
        return 0
    
    active_budgets = Budget.objects.filter(user=user, is_active=True)
    alert_count = 0
    
    for budget in active_budgets:
        alerts = budget.check_alerts()
        alert_count += len(alerts)
    
    return alert_count


@register.inclusion_tag('expenses/budget_alert_badge.html')
def budget_alert_badge(user):
    """
    Display a badge with budget alert count.
    
    Usage in template:
    {% load expenses_tags %}
    {% budget_alert_badge user %}
    """
    alert_count = budget_alert_count(user)
    return {'alert_count': alert_count}


@register.filter
def divide(value, arg):
    """
    Divide the value by the argument.
    
    Usage: {{ value|divide:arg }}
    """
    try:
        return Decimal(str(value)) / Decimal(str(arg))
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
