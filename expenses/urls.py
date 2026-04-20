"""
URL configuration for expenses app.

Routes expense-related URLs to their views.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('list/', views.expense_list_view, name='expense_list'),
    path('add/', views.expense_create_view, name='expense_create'),
    path('<int:pk>/edit/', views.expense_edit_view, name='expense_edit'),
    path('<int:pk>/delete/', views.expense_delete_view, name='expense_delete'),
]
