"""
Context processors for expenses app.

Makes budget alert count available to all templates.
"""
from budgets.models import Budget


def budget_alerts(request):
    """
    Add budget alert count to template context.
    
    This makes alert_count available in all templates.
    """
    alert_count = 0
    if request.user.is_authenticated:
        active_budgets = Budget.objects.filter(user=request.user, is_active=True)
        for budget in active_budgets:
            alerts = budget.check_alerts()
            alert_count += len(alerts)
    
    return {
        'global_alert_count': alert_count
    }
