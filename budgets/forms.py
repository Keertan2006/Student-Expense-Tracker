"""
Forms for budget management.
"""
from django import forms
from .models import Budget
from expenses.models import Category


class BudgetForm(forms.ModelForm):
    """Form for creating and editing budgets."""
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date', 'is_active',
                  'alert_at_50', 'alert_at_75', 'alert_at_90', 'alert_at_100']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alert_at_50': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alert_at_75': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alert_at_90': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alert_at_100': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].required = False
