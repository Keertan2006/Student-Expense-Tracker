"""
Serializers for expense API endpoints.

Converts Expense and Category model instances to JSON.
"""
from rest_framework import serializers
from .models import Expense, Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'amount', 'description', 'category', 'category_id',
            'user', 'date', 'created_at', 'updated_at', 'receipt'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create expense and assign to current user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
