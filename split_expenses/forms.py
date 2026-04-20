"""
Forms for split expense management.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Group, SharedExpense


class GroupForm(forms.ModelForm):
    """Form for creating and editing groups."""
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Group name (e.g., Roommates, Trip to Paris)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
        }


class SharedExpenseForm(forms.ModelForm):
    """Form for creating shared expenses."""
    class Meta:
        model = SharedExpense
        fields = ['description', 'amount', 'date', 'paid_by', 'group']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What was the expense for?'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'paid_by': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Only show groups the user is a member of
            self.fields['group'].queryset = Group.objects.filter(members=user)
            # Only show group members as potential payers
            if 'group' in self.data:
                group_id = self.data.get('group')
                if group_id:
                    group = Group.objects.get(id=group_id)
                    self.fields['paid_by'].queryset = group.members.all()
            elif self.instance and self.instance.pk:
                self.fields['paid_by'].queryset = self.instance.group.members.all()
            else:
                self.fields['paid_by'].queryset = User.objects.none()
