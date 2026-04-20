"""
RESTful API views for split expense management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from .models import Group, SharedExpense, Balance
from .serializers import GroupSerializer, SharedExpenseSerializer, BalanceSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for group management.
    
    Provides CRUD operations for groups via API.
    """
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only groups the user is a member of."""
        return Group.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically set creator and add as member."""
        group = serializer.save(created_by=self.request.user)
        group.members.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the group."""
        group = self.get_object()
        username = request.data.get('username')
        
        try:
            user = User.objects.get(username=username)
            if user not in group.members.all():
                group.members.add(user)
                return Response({'message': f'{username} added to group'})
            return Response({'message': f'{username} is already a member'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class SharedExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for shared expense management.
    
    Provides CRUD operations for shared expenses via API.
    """
    serializer_class = SharedExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only expenses from groups the user is a member of."""
        return SharedExpense.objects.filter(group__members=self.request.user)
    
    def perform_create(self, serializer):
        """Create expense and automatically split it."""
        expense = serializer.save()
        expense.split_equally()


class BalanceView(APIView):
    """
    API endpoint for viewing balances.
    
    GET /api/split/balances/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return all balances for the current user."""
        debts = Balance.objects.filter(owed_by=request.user, is_settled=False)
        credits = Balance.objects.filter(owed_to=request.user, is_settled=False)
        
        total_owed = debts.aggregate(Sum('amount'))['amount__sum'] or 0
        total_owed_to_me = credits.aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'debts': BalanceSerializer(debts, many=True).data,
            'credits': BalanceSerializer(credits, many=True).data,
            'total_owed': total_owed,
            'total_owed_to_me': total_owed_to_me,
            'net_balance': total_owed_to_me - total_owed
        })


class GroupBalanceView(APIView):
    """
    API endpoint for group-specific balances.
    
    GET /api/split/groups/<group_id>/balances/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        """Return balances for a specific group."""
        try:
            # First get the group by pk (ManyToMany fields can't be used in .get())
            group = Group.objects.get(pk=group_id)
            # Then verify the user is a member
            if request.user not in group.members.all():
                return Response({'error': 'You are not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        
        balances = Balance.objects.filter(
            expense__group=group,
            is_settled=False
        )
        
        # Calculate member balances
        member_balances = {}
        for member in group.members.all():
            total_owed = balances.filter(owed_by=member).aggregate(Sum('amount'))['amount__sum'] or 0
            total_owed_to = balances.filter(owed_to=member).aggregate(Sum('amount'))['amount__sum'] or 0
            member_balances[member.username] = {
                'owes': total_owed,
                'owed': total_owed_to,
                'net': total_owed_to - total_owed
            }
        
        return Response({
            'group_id': group_id,
            'balances': BalanceSerializer(balances, many=True).data,
            'member_balances': member_balances
        })
