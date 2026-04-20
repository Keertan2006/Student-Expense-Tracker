"""
Forms for expense management.

This module contains forms for creating and editing expenses.
"""
from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    """
    Form for creating and editing expenses.
    
    Provides a user-friendly interface for expense input.
    """
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'category', 'date', 'receipt']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What did you spend on?'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show categories that exist
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].required = False
