"""
RESTful API views for budget management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for budget management.
    
    Provides CRUD operations for budgets via API.
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only budgets belonging to the current user."""
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically assign budget to current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get alerts for a specific budget."""
        budget = self.get_object()
        alerts = budget.check_alerts()
        return Response({'alerts': alerts})


class BudgetAlertsView(APIView):
    """
    API endpoint for Budget Guardian alerts.
    
    GET /api/budgets/alerts/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return all active budget alerts for the current user."""
        budgets = Budget.objects.filter(user=request.user, is_active=True)
        all_alerts = []
        
        for budget in budgets:
            alerts = budget.check_alerts()
            for alert in alerts:
                alert['budget_id'] = budget.id
                alert['budget_name'] = str(budget)
                all_alerts.append(alert)
        
        return Response({
            'alerts': all_alerts,
            'count': len(all_alerts)
        })
