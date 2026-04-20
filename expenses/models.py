"""
Expense models for tracking personal expenses.

This module defines the data models for expenses and categories.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """
    Expense category model.
    
    Categories help organize expenses (e.g., Food, Transport, Entertainment).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='💰', help_text='Emoji or icon name')
    color = models.CharField(max_length=20, default='#3498db', help_text='Hex color code')
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """
    Expense model for recording individual expenses.
    
    Each expense belongs to a user and has an amount, category, and date.
    """
    # Expense amount (using DecimalField for precise currency handling)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Expense description
    description = models.CharField(max_length=255)
    
    # Category (many expenses can belong to one category)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # User who made the expense
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    
    # Date of expense
    date = models.DateField(default=timezone.now)
    
    # Timestamp for when the expense was created
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional receipt image
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.description} - ₹{self.amount}"
    
    def get_category_name(self):
        """Return category name or 'Uncategorized' if no category."""
        return self.category.name if self.category else 'Uncategorized'
