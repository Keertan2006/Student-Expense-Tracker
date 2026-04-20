"""
Budget models for managing monthly budgets and alerts.

This module defines the Budget model and Budget Guardian alert system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from expenses.models import Category


class Budget(models.Model):
    """
    Budget model for setting spending limits.
    
    Users can set budgets for specific categories and time periods.
    The Budget Guardian feature monitors spending against these budgets.
    """
    # User who owns this budget
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    
    # Category this budget applies to (null means all categories)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Leave blank for overall budget'
    )
    
    # Budget amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Budget period
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    
    # Alert thresholds (percentage of budget used)
    alert_at_50 = models.BooleanField(default=True, help_text='Alert when 50% of budget is used')
    alert_at_75 = models.BooleanField(default=True, help_text='Alert when 75% of budget is used')
    alert_at_90 = models.BooleanField(default=True, help_text='Alert when 90% of budget is used')
    alert_at_100 = models.BooleanField(default=True, help_text='Alert when budget is exceeded')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        category_name = self.category.name if self.category else 'Overall'
        return f"{self.user.username} - {category_name} - ${self.amount}"
    
    def get_spent_amount(self):
        """
        Calculate total amount spent in this budget period.
        
        Returns the sum of all expenses matching this budget's criteria.
        """
        from expenses.models import Expense
        
        expenses = Expense.objects.filter(
            user=self.user,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        if self.category:
            expenses = expenses.filter(category=self.category)
        
        return expenses.aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    def get_remaining_amount(self):
        """Calculate remaining budget amount."""
        return self.amount - self.get_spent_amount()
    
    def get_usage_percentage(self):
        """Calculate budget usage percentage."""
        if self.amount == 0:
            return 0
        return min((self.get_spent_amount() / self.amount) * 100, 100)
    
    def check_alerts(self):
        """
        Check if any alert thresholds have been reached.
        
        Returns a list of alert messages.
        """
        alerts = []
        usage = self.get_usage_percentage()
        spent = self.get_spent_amount()
        
        if usage >= 100 and self.alert_at_100:
            alerts.append({
                'level': 'danger',
                'message': f'Budget exceeded! You have spent ₹{spent:.2f} out of ₹{self.amount:.2f}',
                'percentage': usage
            })
        elif usage >= 90 and self.alert_at_90:
            alerts.append({
                'level': 'warning',
                'message': f'Budget at {usage:.1f}%! You have spent ₹{spent:.2f} out of ₹{self.amount:.2f}',
                'percentage': usage
            })
        elif usage >= 75 and self.alert_at_75:
            alerts.append({
                'level': 'warning',
                'message': f'Budget at {usage:.1f}%! You have spent ₹{spent:.2f} out of ₹{self.amount:.2f}',
                'percentage': usage
            })
        elif usage >= 50 and self.alert_at_50:
            alerts.append({
                'level': 'info',
                'message': f'Budget at {usage:.1f}%! You have spent ₹{spent:.2f} out of ₹{self.amount:.2f}',
                'percentage': usage
            })
        
        return alerts
