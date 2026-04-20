"""
Management command to create the 5 required categories.

Usage: python manage.py create_categories

This ensures the application always has exactly 5 categories:
- Travel
- Entertainment
- Food
- Education
- Bills
"""
from django.core.management.base import BaseCommand
from expenses.models import Category


class Command(BaseCommand):
    help = 'Creates the 5 required categories: Travel, Entertainment, Food, Education, Bills'

    def handle(self, *args, **options):
        self.stdout.write('Creating required categories...')
        
        # Define the 5 required categories
        categories_data = [
            {'name': 'Travel', 'icon': '✈️', 'color': '#3498db', 'description': 'Travel and transportation expenses'},
            {'name': 'Entertainment', 'icon': '🎬', 'color': '#9b59b6', 'description': 'Entertainment and leisure expenses'},
            {'name': 'Food', 'icon': '🍔', 'color': '#e74c3c', 'description': 'Food and dining expenses'},
            {'name': 'Education', 'icon': '📚', 'color': '#1abc9c', 'description': 'Education and learning expenses'},
            {'name': 'Bills', 'icon': '💳', 'color': '#2ecc71', 'description': 'Bills and utility payments'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'description': cat_data['description']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                # Update existing category if needed
                updated = False
                if category.icon != cat_data['icon']:
                    category.icon = cat_data['icon']
                    updated = True
                if category.color != cat_data['color']:
                    category.color = cat_data['color']
                    updated = True
                if category.description != cat_data['description']:
                    category.description = cat_data['description']
                    updated = True
                
                if updated:
                    category.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'Updated category: {category.name}'))
                else:
                    self.stdout.write(f'Category already exists: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully processed {len(categories_data)} categories'))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Already existed: {len(categories_data) - created_count - updated_count}')
