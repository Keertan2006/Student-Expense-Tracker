"""
Serializers for budget API endpoints.
"""
from rest_framework import serializers
from .models import Budget
from expenses.serializers import CategorySerializer
from expenses.models import Category


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    user = serializers.StringRelatedField(read_only=True)
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    
    def get_spent_amount(self, obj):
        return obj.get_spent_amount()
    
    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()
    
    def get_usage_percentage(self, obj):
        return obj.get_usage_percentage()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'category', 'category_id', 'amount',
            'start_date', 'end_date', 'is_active',
            'alert_at_50', 'alert_at_75', 'alert_at_90', 'alert_at_100',
            'created_at', 'updated_at',
            'spent_amount', 'remaining_amount', 'usage_percentage'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create budget and assign to current user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
