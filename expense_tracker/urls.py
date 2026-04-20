"""
Main URL configuration for the Expense Tracker project.

This file routes all incoming requests to the appropriate views.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Account management (authentication)
    path('accounts/', include('accounts.urls')),
    
    # Expense management
    path('expenses/', include('expenses.urls')),
    
    # Budget management
    path('budgets/', include('budgets.urls')),
    
    # Split expense management
    path('split/', include('split_expenses.urls')),
    
    # API endpoints
    path('api/', include('expense_tracker.api_urls')),
    
    # Dashboard (home page after login)
    path('', include('expenses.urls')),  # Dashboard is in expenses app
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
