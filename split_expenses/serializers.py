"""
Serializers for split expense API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group, SharedExpense, Balance


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested representations."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model."""
    created_by = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()
    total_expenses = serializers.ReadOnlyField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'created_by', 'members',
            'created_at', 'updated_at', 'member_count', 'total_expenses'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create group and assign creator."""
        members_data = validated_data.pop('members', [])
        group = Group.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        group.members.add(group.created_by)
        for member in members_data:
            group.members.add(member)
        return group


class SharedExpenseSerializer(serializers.ModelSerializer):
    """Serializer for SharedExpense model."""
    paid_by = UserSerializer(read_only=True)
    paid_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='paid_by',
        write_only=True
    )
    group = GroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True
    )
    
    class Meta:
        model = SharedExpense
        fields = [
            'id', 'description', 'amount', 'date',
            'paid_by', 'paid_by_id', 'group', 'group_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create expense and automatically split it."""
        expense = SharedExpense.objects.create(**validated_data)
        expense.split_equally()
        return expense


class BalanceSerializer(serializers.ModelSerializer):
    """Serializer for Balance model."""
    owed_by = UserSerializer(read_only=True)
    owed_to = UserSerializer(read_only=True)
    expense = SharedExpenseSerializer(read_only=True)
    
    class Meta:
        model = Balance
        fields = [
            'id', 'expense', 'owed_by', 'owed_to', 'amount',
            'is_settled', 'settled_at', 'created_at'
        ]
        read_only_fields = ['created_at']
