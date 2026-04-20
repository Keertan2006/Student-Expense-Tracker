"""
URL configuration for split_expenses app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list_view, name='group_list'),
    path('groups/create/', views.group_create_view, name='group_create'),
    path('groups/<int:pk>/', views.group_detail_view, name='group_detail'),
    path('groups/<int:pk>/edit/', views.group_edit_view, name='group_edit'),
    path('groups/<int:pk>/add-member/', views.group_add_member_view, name='group_add_member'),
    path('groups/<int:group_id>/expense/add/', views.shared_expense_create_view, name='shared_expense_create'),
    path('balances/', views.balance_view, name='balance_view'),
    path('balances/<int:balance_id>/settle/', views.settle_balance_view, name='settle_balance'),
]
