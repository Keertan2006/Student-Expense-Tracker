"""
Views for budget management and Budget Guardian alerts.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget
from .forms import BudgetForm


@login_required
def budget_list_view(request):
    """
    List all budgets for the current user with alert status.
    """
    budgets = Budget.objects.filter(user=request.user)
    
    # Get alerts for each budget
    budget_data = []
    all_alerts = []
    
    for budget in budgets:
        alerts = budget.check_alerts()
        budget_data.append({
            'budget': budget,
            'spent': budget.get_spent_amount(),
            'remaining': budget.get_remaining_amount(),
            'usage_percentage': budget.get_usage_percentage(),
            'alerts': alerts
        })
        all_alerts.extend(alerts)
    
    context = {
        'budget_data': budget_data,
        'all_alerts': all_alerts,
    }
    
    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_create_view(request):
    """Create a new budget."""
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm()
    
    return render(request, 'budgets/budget_form.html', {'form': form, 'title': 'Create Budget'})


@login_required
def budget_edit_view(request, pk):
    """Edit an existing budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    
    return render(request, 'budgets/budget_form.html', {'form': form, 'title': 'Edit Budget', 'budget': budget})


@login_required
def budget_delete_view(request, pk):
    """Delete a budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')
    
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})


@login_required
def budget_alerts_view(request):
    """
    Budget Guardian - View all active alerts.
    
    This is the main Budget Guardian feature that shows all budget alerts.
    """
    budgets = Budget.objects.filter(user=request.user, is_active=True)
    all_alerts = []
    
    for budget in budgets:
        alerts = budget.check_alerts()
        for alert in alerts:
            alert['budget'] = budget
            all_alerts.append(alert)
    
    # Sort alerts by severity (danger > warning > info)
    severity_order = {'danger': 0, 'warning': 1, 'info': 2}
    all_alerts.sort(key=lambda x: (severity_order.get(x['level'], 3), -x['percentage']))
    
    context = {
        'alerts': all_alerts,
        'alert_count': len(all_alerts),
    }
    
    return render(request, 'budgets/budget_alerts.html', context)
