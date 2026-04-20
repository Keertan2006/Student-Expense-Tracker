"""
Views for expense management and dashboard.

This module handles all expense-related views including the main dashboard.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Expense, Category
from .forms import ExpenseForm
from budgets.models import Budget


@login_required
def dashboard_view(request):
    """
    Main dashboard view showing expense statistics and charts.
    
    Displays:
    - Total expenses (this month, this week, today)
    - Category-wise spending
    - Budget usage
    - Recent expenses
    - Individual vs group expenses comparison
    """
    user = request.user
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_week = today - timedelta(days=today.weekday())
    
    # Get all user expenses
    all_expenses = Expense.objects.filter(user=user)
    
    # Calculate totals
    total_all_time = all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_this_month = all_expenses.filter(
        date__gte=start_of_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    total_this_week = all_expenses.filter(
        date__gte=start_of_week
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    total_today = all_expenses.filter(
        date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Category-wise spending (this month)
    category_expenses = all_expenses.filter(
        date__gte=start_of_month
    ).values('category__name', 'category__icon', 'category__color').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent expenses (last 10)
    recent_expenses = all_expenses[:10]
    
    # Get active budgets and their usage
    active_budgets = Budget.objects.filter(user=user, is_active=True)
    budget_data = []
    all_alerts = []  # Collect all budget alerts
    
    for budget in active_budgets:
        spent = budget.get_spent_amount()
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        
        # Get alerts for this budget
        alerts = budget.check_alerts()
        for alert in alerts:
            alert['budget'] = budget
            all_alerts.append(alert)
        
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.amount - spent,
            'percentage': min(percentage, 100),
            'alerts': alerts
        })
    
    # Sort alerts by severity (danger > warning > info)
    severity_order = {'danger': 0, 'warning': 1, 'info': 2}
    all_alerts.sort(key=lambda x: (severity_order.get(x['level'], 3), -x['percentage']))
    
    # Individual vs group expenses
    individual_total = total_this_month
    try:
        from split_expenses.models import SharedExpense
        group_total = SharedExpense.objects.filter(
            group__members=user,
            date__gte=start_of_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    except:
        group_total = 0
    
    context = {
        'total_all_time': total_all_time,
        'total_this_month': total_this_month,
        'total_this_week': total_this_week,
        'total_today': total_today,
        'category_expenses': category_expenses,
        'recent_expenses': recent_expenses,
        'budget_data': budget_data,
        'budget_alerts': all_alerts,
        'alert_count': len(all_alerts),
        'individual_total': individual_total,
        'group_total': group_total,
    }
    
    return render(request, 'expenses/dashboard.html', context)


@login_required
def expense_list_view(request):
    """
    List all expenses with filtering options.
    """
    user = request.user
    expenses = Expense.objects.filter(user=user)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    
    # Search
    search = request.GET.get('search')
    if search:
        expenses = expenses.filter(description__icontains=search)
    
    categories = Category.objects.all()
    
    context = {
        'expenses': expenses,
        'categories': categories,
        'selected_category': category_id,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    }
    
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create_view(request):
    """
    Create a new expense.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def expense_edit_view(request, pk):
    """
    Edit an existing expense.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense', 'expense': expense})


@login_required
def expense_delete_view(request, pk):
    """
    Delete an expense.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})
