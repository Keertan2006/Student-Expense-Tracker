"""
Management command to list all categories.

Usage: python manage.py list_categories
"""
from django.core.management.base import BaseCommand
from expenses.models import Category


class Command(BaseCommand):
    help = 'Lists all expense categories'

    def handle(self, *args, **options):
        categories = Category.objects.all().order_by('name')
        
        self.stdout.write('\nExpense Categories:')
        self.stdout.write('-' * 40)
        
        for cat in categories:
            self.stdout.write(f'  {cat.name} (Color: {cat.color})')
        
        self.stdout.write('-' * 40)
        self.stdout.write(f'Total: {categories.count()} categories\n')
        
        # Check for required categories
        required = ['Travel', 'Entertainment', 'Food', 'Education', 'Bills']
        existing = [cat.name for cat in categories]
        missing = [name for name in required if name not in existing]
        
        if missing:
            self.stdout.write(self.style.WARNING(f'Missing categories: {", ".join(missing)}'))
            self.stdout.write(self.style.WARNING('Run: python manage.py create_categories'))
        else:
            self.stdout.write(self.style.SUCCESS('All 5 required categories exist!'))
