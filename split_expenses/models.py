"""
Split Expense models for managing shared expenses and groups.

This module implements a mini Splitwise-like system for splitting expenses among friends.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Group(models.Model):
    """
    Group model for expense sharing.
    
    Users can create groups (e.g., "Roommates", "Trip to Paris") and add members.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Group creator/owner
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    
    # Group members (many-to-many relationship)
    # Using 'expense_groups' as related_name to avoid conflict with auth.User.groups
    members = models.ManyToManyField(User, related_name='expense_groups')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        """Return the number of members in the group."""
        return self.members.count()
    
    def get_total_expenses(self):
        """Calculate total expenses in this group."""
        return self.shared_expenses.aggregate(
            models.Sum('amount')
        )['amount__sum'] or Decimal('0.00')


class SharedExpense(models.Model):
    """
    Shared expense model for group expenses.
    
    Represents an expense that is split among group members.
    """
    # Expense details
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    
    # Who paid for this expense
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='paid_expenses'
    )
    
    # Which group this expense belongs to
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='shared_expenses'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.group.name} - {self.description} - ₹{self.amount}"
    
    def get_amount_per_person(self):
        """
        Calculate the amount each person owes for this expense.
        
        Returns the per-person share amount.
        """
        from decimal import Decimal
        member_count = self.group.get_member_count()
        if member_count == 0:
            return Decimal('0.00')
        return (Decimal(str(self.amount)) / Decimal(str(member_count))).quantize(Decimal('0.01'))
    
    def split_equally(self):
        """
        Split expense equally among all group members.
        
        This method creates Balance records for each member (except the payer).
        Each member (except the payer) owes their share to the payer.
        
        Example: If 3 members split ₹60:
        - Each person's share: ₹20
        - If Person A pays ₹60:
          - Person B owes ₹20 to Person A
          - Person C owes ₹20 to Person A
        """
        from decimal import Decimal
        
        # Ensure we have a valid group
        if not self.group:
            raise ValueError("Expense must have a group assigned")
        
        # Get all group members
        members = list(self.group.members.all())
        member_count = len(members)
        
        if member_count == 0:
            raise ValueError("Group has no members. Cannot split expense.")
        
        if member_count == 1:
            # Only one member, no splitting needed
            return 0
        
        # Ensure paid_by is a member of the group
        if self.paid_by not in members:
            raise ValueError(f"Payer {self.paid_by.username} is not a member of group {self.group.name}")
        
        # Calculate amount per person (each person's share)
        amount_per_person = self.get_amount_per_person()
        
        # Delete existing balances for this expense (in case of updates)
        Balance.objects.filter(expense=self).delete()
        
        # Create balance records for each member except the payer
        balances_created = 0
        for member in members:
            if member != self.paid_by:
                # This member owes their share to the payer
                Balance.objects.create(
                    expense=self,
                    owed_by=member,
                    owed_to=self.paid_by,
                    amount=amount_per_person
                )
                balances_created += 1
        
        return balances_created


class Balance(models.Model):
    """
    Balance model for tracking who owes whom.
    
    Represents a debt: owed_by owes amount to owed_to.
    """
    # The expense this balance is related to (null for simplified balances)
    expense = models.ForeignKey(
        SharedExpense,
        on_delete=models.CASCADE,
        related_name='balances',
        null=True,
        blank=True
    )
    
    # Who owes the money
    owed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='debts'
    )
    
    # Who is owed the money
    owed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='credits'
    )
    
    # Amount owed
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Whether this balance has been settled
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owed_by', 'owed_to', 'is_settled']),
        ]
    
    def __str__(self):
        return f"{self.owed_by.username} owes ${self.amount} to {self.owed_to.username}"
    
    def settle(self):
        """Mark this balance as settled."""
        from django.utils import timezone
        self.is_settled = True
        self.settled_at = timezone.now()
        self.save()
    
    @staticmethod
    def get_net_balance(user1, user2, group=None):
        """
        Calculate net balance between two users.
        
        Returns positive amount if user1 owes user2, negative if user2 owes user1.
        If group is specified, only considers balances within that group.
        """
        balances = Balance.objects.filter(
            models.Q(owed_by=user1, owed_to=user2) | models.Q(owed_by=user2, owed_to=user1),
            is_settled=False
        )
        
        if group:
            balances = balances.filter(expense__group=group)
        
        net = Decimal('0.00')
        for balance in balances:
            if balance.owed_by == user1:
                net += balance.amount
            else:
                net -= balance.amount
        
        return net
    
    @staticmethod
    def simplify_balances(group):
        """
        Simplify balances within a group.
        
        If A owes B $10 and B owes A $5, simplify to A owes B $5.
        This is a basic implementation - full simplification would require graph algorithms.
        """
        members = list(group.members.all())
        
        for i, member1 in enumerate(members):
            for member2 in members[i+1:]:
                net = Balance.get_net_balance(member1, member2, group)
                
                # Delete existing balances between these two
                Balance.objects.filter(
                    models.Q(owed_by=member1, owed_to=member2) |
                    models.Q(owed_by=member2, owed_to=member1),
                    expense__group=group,
                    is_settled=False
                ).delete()
                
                # Create simplified balance
                if net > 0:
                    Balance.objects.create(
                        expense=None,  # Simplified balance, not tied to specific expense
                        owed_by=member1,
                        owed_to=member2,
                        amount=net
                    )
                elif net < 0:
                    Balance.objects.create(
                        expense=None,
                        owed_by=member2,
                        owed_to=member1,
                        amount=-net
                    )
