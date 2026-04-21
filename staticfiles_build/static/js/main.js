// Main JavaScript for Expense Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initCurrencyFormatting();
    initAnimations();
    initFormValidation();
    initTooltips();
    initAutoSave();
    initCharts();
    initFilters();
});

// Format currency to INR
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Initialize currency formatting
function initCurrencyFormatting() {
    // Format all currency displays
    document.querySelectorAll('.currency-amount').forEach(element => {
        const amount = element.textContent.replace(/[₹,]/g, '');
        element.textContent = formatCurrency(amount);
    });
    
    // Format currency inputs
    document.querySelectorAll('input[type="number"][data-currency]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const formatted = formatCurrency(this.value);
                // Store original value for form submission
                this.setAttribute('data-original-value', this.value);
            }
        });
        
        input.addEventListener('focus', function() {
            const original = this.getAttribute('data-original-value');
            if (original) {
                this.value = original;
            }
        });
    });
}

// Initialize animations
function initAnimations() {
    // Fade in cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .stat-card').forEach(card => {
        observer.observe(card);
    });
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields correctly.', 'error');
            }
        });
    });
    
    // Real-time validation
    document.querySelectorAll('input[required], select[required]').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Remove existing error
    const existingError = field.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Check if required
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }
    
    // Check email format
    if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address.';
    }
    
    // Check number range
    if (field.type === 'number' && value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        const numValue = parseFloat(value);
        
        if (min && numValue < parseFloat(min)) {
            isValid = false;
            errorMessage = `Value must be at least ${min}.`;
        }
        if (max && numValue > parseFloat(max)) {
            isValid = false;
            errorMessage = `Value must be at most ${max}.`;
        }
    }
    
    // Display error
    if (!isValid) {
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-danger small mt-1';
        errorDiv.textContent = errorMessage;
        field.parentElement.appendChild(errorDiv);
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    }
    
    return isValid;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Tooltips
function initTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Auto-save functionality for forms
function initAutoSave() {
    const autoSaveForms = document.querySelectorAll('form[data-autosave]');
    
    autoSaveForms.forEach(form => {
        const formId = form.getAttribute('data-autosave');
        const inputs = form.querySelectorAll('input, select, textarea');
        
        // Load saved data
        loadFormData(form, formId);
        
        // Save on input change
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                saveFormData(form, formId);
            });
        });
    });
}

function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
}

function loadFormData(form, formId) {
    const saved = localStorage.getItem(`form_${formId}`);
    if (saved) {
        const data = JSON.parse(saved);
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && field.type !== 'file') {
                field.value = data[key];
            }
        });
    }
}

// Initialize charts
function initCharts() {
    // Chart.js is loaded via CDN in base.html
    // This function can be extended for custom chart configurations
    if (typeof Chart !== 'undefined') {
        // Set default chart options
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = '#374151';
    }
}

// Filter functionality
function initFilters() {
    const filterForms = document.querySelectorAll('form[data-filter]');
    
    filterForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit filter form on change
                if (form.getAttribute('data-auto-submit') === 'true') {
                    form.submit();
                }
            });
        });
    });
}

// Notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Confirm delete dialogs
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Add event listeners to delete buttons
document.addEventListener('click', function(e) {
    if (e.target.closest('a[data-confirm-delete]')) {
        e.preventDefault();
        const link = e.target.closest('a[data-confirm-delete]');
        const message = link.getAttribute('data-confirm-delete') || 'Are you sure?';
        
        if (confirmDelete(message)) {
            window.location.href = link.href;
        }
    }
});

// Export data functionality
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const rows = data.map(row => 
        headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') 
                ? `"${value}"` 
                : value;
        }).join(',')
    );
    
    return [headers.join(','), ...rows].join('\n');
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility: Format number with Indian locale
function formatNumber(num) {
    return parseFloat(num).toLocaleString('en-IN');
}

// Make functions available globally
window.expenseTracker = {
    formatCurrency,
    showNotification,
    confirmDelete,
    exportToCSV,
    formatDate,
    formatNumber
};
