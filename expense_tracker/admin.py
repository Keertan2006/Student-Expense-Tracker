"""
Admin configuration for the main project.

Registers models in Django admin panel.
"""
from django.contrib import admin
from django.contrib.auth.models import User, Group as AuthGroup

# Customize admin site
admin.site.site_header = "Expense Tracker Administration"
admin.site.site_title = "Expense Tracker Admin"
admin.site.index_title = "Welcome to Expense Tracker Admin Panel"
