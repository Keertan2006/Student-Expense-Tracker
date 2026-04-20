"""
Views for split expense management (Mini Splitwise).

This module handles groups, shared expenses, and balance tracking.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Q
from django import forms
from .models import Group, SharedExpense, Balance
from .forms import GroupForm, SharedExpenseForm


@login_required
def group_list_view(request):
    """List all groups the user is a member of."""
    groups = Group.objects.filter(members=request.user)
    context = {'groups': groups}
    return render(request, 'split_expenses/group_list.html', context)


@login_required
def group_create_view(request):
    """Create a new group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            # Add creator as a member
            group.members.add(request.user)
            messages.success(request, 'Group created successfully!')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm()
    
    return render(request, 'split_expenses/group_form.html', {'form': form, 'title': 'Create Group'})


@login_required
def group_detail_view(request, pk):
    """View group details, members, expenses, and balances."""
    group = get_object_or_404(Group, pk=pk)
    
    # Check if user is a member
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('group_list')
    
    # Get all shared expenses in this group
    expenses = SharedExpense.objects.filter(group=group).order_by('-date')
    
    # Get all balances for this group
    balances = Balance.objects.filter(
        expense__group=group,
        is_settled=False
    )
    
    # Calculate who owes whom (convert to list for template)
    balance_summary_dict = {}
    for balance in balances:
        key = (balance.owed_by, balance.owed_to)
        if key not in balance_summary_dict:
            balance_summary_dict[key] = 0
        balance_summary_dict[key] += balance.amount
    
    # Convert to list for template rendering
    balance_summary = [
        {'owed_by': k[0], 'owed_to': k[1], 'amount': v}
        for k, v in balance_summary_dict.items()
    ]
    
    # Get net balances for each member
    member_balances = {}
    for member in group.members.all():
        total_owed = balances.filter(owed_by=member).aggregate(Sum('amount'))['amount__sum'] or 0
        total_owed_to = balances.filter(owed_to=member).aggregate(Sum('amount'))['amount__sum'] or 0
        member_balances[member] = {
            'owes': total_owed,
            'owed': total_owed_to,
            'net': total_owed_to - total_owed
        }
    
    context = {
        'group': group,
        'expenses': expenses,
        'balances': balances,
        'balance_summary': balance_summary,
        'member_balances': member_balances,
    }
    
    return render(request, 'split_expenses/group_detail.html', context)


@login_required
def group_edit_view(request, pk):
    """Edit a group (only creator can edit)."""
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully!')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'split_expenses/group_form.html', {'form': form, 'title': 'Edit Group', 'group': group})


@login_required
def group_add_member_view(request, pk):
    """Add a member to a group."""
    group = get_object_or_404(Group, pk=pk)
    
    # Only creator can add members
    if group.created_by != request.user:
        messages.error(request, 'Only the group creator can add members.')
        return redirect('group_detail', pk=group.pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user not in group.members.all():
                group.members.add(user)
                messages.success(request, f'{user.username} added to group!')
            else:
                messages.info(request, f'{user.username} is already a member.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        
        return redirect('group_detail', pk=group.pk)
    
    return redirect('group_detail', pk=group.pk)


@login_required
def shared_expense_create_view(request, group_id):
    """Create a shared expense in a group."""
    group = get_object_or_404(Group, pk=group_id)
    
    # Check if user is a member
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('group_list')
    
    if request.method == 'POST':
        form = SharedExpenseForm(request.POST, user=request.user)
        # Override group field to ensure it's set correctly
        form.fields['group'].initial = group
        form.fields['paid_by'].queryset = group.members.all()
        
        if form.is_valid():
            expense = form.save(commit=False)
            # Ensure group is set correctly (in case form validation changed it)
            expense.group = group
            expense.save()
            
            # Automatically split the expense equally
            try:
                balances_created = expense.split_equally()
                amount_per_person = expense.get_amount_per_person()
                if balances_created > 0:
                    messages.success(
                        request, 
                        f'Expense of ₹{expense.amount:.2f} added and split equally among {group.get_member_count()} member(s)! '
                        f'Each member owes ₹{amount_per_person:.2f} to {expense.paid_by.username}.'
                    )
                else:
                    messages.info(request, f'Expense of ₹{expense.amount:.2f} added. (Only one member in group)')
            except Exception as e:
                messages.error(request, f'Error splitting expense: {str(e)}')
                # Log the error but don't fail the expense creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error splitting expense {expense.id}: {str(e)}")
            
            return redirect('group_detail', pk=group_id)
    else:
        form = SharedExpenseForm(user=request.user)
        form.fields['group'].initial = group
        form.fields['group'].widget = forms.HiddenInput()  # Hide group field
        form.fields['paid_by'].queryset = group.members.all()
    
    return render(request, 'split_expenses/shared_expense_form.html', {
        'form': form,
        'group': group,
        'title': 'Add Shared Expense'
    })


@login_required
def balance_view(request):
    """View all balances (who owes whom) across all groups."""
    # Get all balances where user is involved
    debts = Balance.objects.filter(owed_by=request.user, is_settled=False)
    credits = Balance.objects.filter(owed_to=request.user, is_settled=False)
    
    # Calculate totals
    total_owed = debts.aggregate(Sum('amount'))['amount__sum'] or 0
    total_owed_to_me = credits.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Group by person
    debts_by_person = {}
    for debt in debts:
        person = debt.owed_to
        if person not in debts_by_person:
            debts_by_person[person] = 0
        debts_by_person[person] += debt.amount
    
    credits_by_person = {}
    for credit in credits:
        person = credit.owed_by
        if person not in credits_by_person:
            credits_by_person[person] = 0
        credits_by_person[person] += credit.amount
    
    context = {
        'debts': debts,
        'credits': credits,
        'total_owed': total_owed,
        'total_owed_to_me': total_owed_to_me,
        'debts_by_person': debts_by_person,
        'credits_by_person': credits_by_person,
    }
    
    return render(request, 'split_expenses/balance_view.html', context)


@login_required
def settle_balance_view(request, balance_id):
    """Mark a balance as settled."""
    balance = get_object_or_404(
        Balance.objects.filter(
            Q(owed_by=request.user) | Q(owed_to=request.user)
        ),
        pk=balance_id
    )
    
    if request.method == 'POST':
        balance.settle()
        messages.success(request, 'Balance settled!')
        return redirect('balance_view')
    
    return render(request, 'split_expenses/settle_balance_confirm.html', {'balance': balance})
