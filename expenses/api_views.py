"""
RESTful API views for expense management.

This module provides API endpoints for CRUD operations on expenses.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Expense, Category
from .serializers import ExpenseSerializer, CategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for expense management.
    
    Provides CRUD operations for expenses via API.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only expenses belonging to the current user."""
        return Expense.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically assign expense to current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get expense statistics for the current user."""
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_week = today - timedelta(days=today.weekday())
        
        expenses = Expense.objects.filter(user=user)
        
        stats = {
            'total_all_time': expenses.aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_this_month': expenses.filter(
                date__gte=start_of_month
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_this_week': expenses.filter(
                date__gte=start_of_week
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_today': expenses.filter(
                date=today
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
            'category_breakdown': list(
                expenses.filter(date__gte=start_of_month)
                .values('category__name')
                .annotate(total=Sum('amount'), count=Count('id'))
                .order_by('-total')
            )
        }
        
        return Response(stats)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for category management.
    
    Provides CRUD operations for categories via API.
    Categories are global and shared across all users, so only admins can modify them.
    Regular users can only read (GET) categories.
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on the action.
        - Read operations (list, retrieve): Allow all authenticated users
        - Write operations (create, update, delete): Require admin access
        """
        if self.action in ['list', 'retrieve', 'usage', 'expenses']:
            permission_classes = [IsAuthenticated]
        else:
            # create, update, partial_update, destroy
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return categories, optionally filtered by search query.
        """
        queryset = Category.objects.all().order_by('name')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """
        Get usage statistics for a specific category.
        
        Returns:
        - Total expenses in this category
        - Expense count
        - Usage by current user
        - Recent expenses
        """
        category = self.get_object()
        user = request.user
        
        # All expenses in this category
        all_expenses = Expense.objects.filter(category=category)
        total_amount = all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        total_count = all_expenses.count()
        
        # Current user's expenses in this category
        user_expenses = all_expenses.filter(user=user)
        user_total = user_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        user_count = user_expenses.count()
        
        # Recent expenses (last 10)
        recent_expenses = user_expenses.order_by('-date')[:10]
        
        return Response({
            'category': CategorySerializer(category).data,
            'statistics': {
                'total_amount': total_amount,
                'total_count': total_count,
                'user_amount': user_total,
                'user_count': user_count,
                'user_percentage': (user_total / total_amount * 100) if total_amount > 0 else 0
            },
            'recent_expenses': ExpenseSerializer(recent_expenses, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def expenses(self, request, pk=None):
        """
        Get all expenses for the current user in this category.
        
        Query parameters:
        - date_from: Filter expenses from this date (YYYY-MM-DD)
        - date_to: Filter expenses until this date (YYYY-MM-DD)
        """
        category = self.get_object()
        user = request.user
        
        expenses = Expense.objects.filter(category=category, user=user)
        
        # Date filtering
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        
        if date_from:
            expenses = expenses.filter(date__gte=date_from)
        if date_to:
            expenses = expenses.filter(date__lte=date_to)
        
        expenses = expenses.order_by('-date')
        
        # Pagination
        page = self.paginate_queryset(expenses)
        if page is not None:
            serializer = ExpenseSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get most popular categories by expense count.
        
        Query parameters:
        - limit: Number of categories to return (default: 10)
        """
        limit = int(request.query_params.get('limit', 10))
        
        # Get categories ordered by number of expenses
        categories = Category.objects.annotate(
            expense_count=Count('expense')
        ).filter(expense_count__gt=0).order_by('-expense_count')[:limit]
        
        serializer = CategorySerializer(categories, many=True)
        return Response({
            'categories': serializer.data,
            'limit': limit
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall category statistics for the current user.
        
        Returns category-wise spending breakdown.
        """
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Get category statistics for current user
        category_stats = Expense.objects.filter(
            user=user,
            date__gte=start_of_month,
            category__isnull=False
        ).values(
            'category__id',
            'category__name',
            'category__icon',
            'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        return Response({
            'period': {
                'start': start_of_month,
                'end': today
            },
            'categories': list(category_stats),
            'total_categories': category_stats.count()
        })


class ExpenseStatsView(APIView):
    """
    API endpoint for detailed expense statistics.
    
    GET /api/expenses/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return comprehensive expense statistics."""
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        expenses = Expense.objects.filter(user=user)
        
        # Category-wise spending
        category_data = expenses.filter(
            date__gte=start_of_month
        ).values('category__name', 'category__icon', 'category__color').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        return Response({
            'category_breakdown': list(category_data),
            'total_expenses': expenses.filter(
                date__gte=start_of_month
            ).aggregate(Sum('amount'))['amount__sum'] or 0
        })
