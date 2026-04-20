"""
Management command to create sample data for testing.

Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from expenses.models import Category, Expense
from budgets.models import Budget
from split_expenses.models import Group, SharedExpense
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates sample data for testing the application'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories (exactly 5 categories as required)
        categories_data = [
            {'name': 'Travel', 'icon': '✈️', 'color': '#3498db'},
            {'name': 'Entertainment', 'icon': '🎬', 'color': '#9b59b6'},
            {'name': 'Food', 'icon': '🍔', 'color': '#e74c3c'},
            {'name': 'Education', 'icon': '📚', 'color': '#1abc9c'},
            {'name': 'Bills', 'icon': '💳', 'color': '#2ecc71'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
        
        # Create test users
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(self.style.SUCCESS('Created test user: testuser (password: testpass123)'))
        
        # Create another user for split expenses
        user2, created = User.objects.get_or_create(
            username='friend1',
            defaults={
                'email': 'friend1@example.com',
                'first_name': 'Friend',
                'last_name': 'One'
            }
        )
        if created:
            user2.set_password('testpass123')
            user2.save()
            self.stdout.write(self.style.SUCCESS('Created test user: friend1 (password: testpass123)'))
        
        # Create sample expenses
        today = timezone.now().date()
        expense_data = [
            {'description': 'Lunch at cafeteria', 'amount': 12.50, 'category': 'Food', 'days_ago': 0},
            {'description': 'Uber ride to college', 'amount': 8.75, 'category': 'Travel', 'days_ago': 1},
            {'description': 'Movie tickets', 'amount': 25.00, 'category': 'Entertainment', 'days_ago': 2},
            {'description': 'Groceries', 'amount': 45.30, 'category': 'Food', 'days_ago': 3},
            {'description': 'Textbook', 'amount': 89.99, 'category': 'Education', 'days_ago': 5},
            {'description': 'Coffee', 'amount': 4.50, 'category': 'Food', 'days_ago': 0},
            {'description': 'Bus pass', 'amount': 30.00, 'category': 'Travel', 'days_ago': 7},
            {'description': 'Netflix subscription', 'amount': 15.99, 'category': 'Entertainment', 'days_ago': 10},
            {'description': 'Electricity bill', 'amount': 500.00, 'category': 'Bills', 'days_ago': 15},
        ]
        
        for exp_data in expense_data:
            expense = Expense.objects.create(
                user=test_user,
                description=exp_data['description'],
                amount=Decimal(str(exp_data['amount'])),
                category=categories[exp_data['category']],
                date=today - timedelta(days=exp_data['days_ago'])
            )
            self.stdout.write(f'Created expense: {expense.description}')
        
        # Create budget
        start_date = today.replace(day=1)  # First day of current month
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # Last day of month
        
        budget = Budget.objects.create(
            user=test_user,
            category=categories['Food'],
            amount=Decimal('200.00'),
            start_date=start_date,
            end_date=end_date,
            alert_at_50=True,
            alert_at_75=True,
            alert_at_90=True,
            alert_at_100=True
        )
            self.stdout.write(self.style.SUCCESS(f'Created budget: ₹{budget.amount} for {budget.category.name}'))
        
        # Create group and shared expenses
        group = Group.objects.create(
            name='Roommates',
            description='Shared expenses with roommates',
            created_by=test_user
        )
        group.members.add(test_user, user2)
        self.stdout.write(self.style.SUCCESS(f'Created group: {group.name}'))
        
        # Add shared expenses
        shared_expense1 = SharedExpense.objects.create(
            description='Dinner at restaurant',
            amount=Decimal('60.00'),
            paid_by=test_user,
            group=group,
            date=today - timedelta(days=1)
        )
        shared_expense1.split_equally()
        self.stdout.write(f'Created shared expense: {shared_expense1.description}')
        
        shared_expense2 = SharedExpense.objects.create(
            description='Groceries for the week',
            amount=Decimal('80.00'),
            paid_by=user2,
            group=group,
            date=today - timedelta(days=3)
        )
        shared_expense2.split_equally()
        self.stdout.write(f'Created shared expense: {shared_expense2.description}')
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nYou can now login with:')
        self.stdout.write('  Username: testuser')
        self.stdout.write('  Password: testpass123')
