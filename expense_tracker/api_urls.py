"""
API URL configuration for RESTful endpoints.

This file defines all API endpoints for the Expense Tracker application.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import api_views as accounts_api
from expenses import api_views as expenses_api
from budgets import api_views as budgets_api
from split_expenses import api_views as split_api

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'users', accounts_api.UserViewSet)
router.register(r'expenses', expenses_api.ExpenseViewSet, basename='expense')
router.register(r'categories', expenses_api.CategoryViewSet)
router.register(r'budgets', budgets_api.BudgetViewSet, basename='budget')
router.register(r'groups', split_api.GroupViewSet, basename='group')
router.register(r'shared-expenses', split_api.SharedExpenseViewSet, basename='shared-expense')

urlpatterns = [
    # Router URLs (ViewSets)
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('auth/register/', accounts_api.RegisterView.as_view(), name='api-register'),
    path('auth/login/', accounts_api.LoginView.as_view(), name='api-login'),
    path('auth/logout/', accounts_api.LogoutView.as_view(), name='api-logout'),
    
    # Expense statistics
    path('expenses/stats/', expenses_api.ExpenseStatsView.as_view(), name='api-expense-stats'),
    
    # Budget alerts
    path('budgets/alerts/', budgets_api.BudgetAlertsView.as_view(), name='api-budget-alerts'),
    
    # Split expense balances
    path('split/balances/', split_api.BalanceView.as_view(), name='api-balances'),
    path('split/groups/<int:group_id>/balances/', split_api.GroupBalanceView.as_view(), name='api-group-balances'),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls')),
]
