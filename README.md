# Student Expense Tracker

A comprehensive web-based expense tracking application built with Django that helps students manage their personal finances, set budgets, and split expenses with friends.

## Features

### Core Features
- **Expense Management**: Record, categorize, and track daily expenses
- **Category System**: Organize expenses by categories (Food, Transport, Entertainment, etc.)
- **Budget Management**: Set monthly budgets for categories or overall spending
- **Budget Guardian**: Automatic alerts when spending reaches 50%, 75%, 90%, or 100% of budget
- **Split Expenses (Mini Splitwise)**: 
  - Create groups with friends
  - Add shared expenses
  - Automatically split costs equally
  - Track balances (who owes whom)
- **Interactive Dashboard**: 
  - Total expenses (today, week, month, all-time)
  - Category-wise spending charts
  - Budget usage visualization
  - Recent expenses list

### Technical Features
- **RESTful API**: Complete API endpoints for all features
- **User Authentication**: Secure login/registration system
- **Modern UI**: Bootstrap 5 with responsive design
- **Data Visualization**: Chart.js for expense analytics

## Project Structure

```
expense_tracker/
├── expense_tracker/          # Main project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py               # Main URL routing
│   └── api_urls.py           # API endpoint routing
├── accounts/                 # User authentication app
├── expenses/                 # Expense management app
│   ├── models.py            # Expense and Category models
│   ├── views.py             # Expense views (dashboard, CRUD)
│   └── api_views.py         # REST API endpoints
├── budgets/                  # Budget management app
│   ├── models.py            # Budget model with alert system
│   └── views.py             # Budget views and Budget Guardian
├── split_expenses/           # Split expense module (Mini Splitwise)
│   ├── models.py            # Group, SharedExpense, Balance models
│   └── views.py             # Group and balance management
└── templates/               # HTML templates
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
cd "C:\Users\Keertan P Shetty\OneDrive\Desktop\Engineering  Files\Expense"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional - for admin access)
```bash
python manage.py createsuperuser
```

### Step 6: Load Sample Data (Optional)
```bash
python manage.py loaddata sample_data.json
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

## Database Schema

### Key Models

1. **User** (Django built-in)
   - Authentication and user management

2. **Category**
   - `name`: Category name (Food, Transport, etc.)
   - `icon`: Emoji or icon
   - `color`: Hex color code

3. **Expense**
   - `amount`: Expense amount (Decimal)
   - `description`: Expense description
   - `category`: Foreign key to Category
   - `user`: Foreign key to User
   - `date`: Date of expense
   - `receipt`: Optional image upload

4. **Budget**
   - `user`: Foreign key to User
   - `category`: Foreign key to Category (optional)
   - `amount`: Budget limit
   - `start_date`, `end_date`: Budget period
   - `alert_at_50/75/90/100`: Alert thresholds
   - `is_active`: Active status

5. **Group**
   - `name`: Group name
   - `created_by`: Group creator
   - `members`: Many-to-many with User

6. **SharedExpense**
   - `description`: Expense description
   - `amount`: Total amount
   - `paid_by`: User who paid
   - `group`: Foreign key to Group
   - `date`: Expense date

7. **Balance**
   - `expense`: Foreign key to SharedExpense
   - `owed_by`: User who owes
   - `owed_to`: User who is owed
   - `amount`: Amount owed
   - `is_settled`: Settlement status

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (returns token)
- `POST /api/auth/logout/` - Logout

### Expenses
- `GET /api/expenses/` - List expenses
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/{id}/` - Get expense
- `PUT /api/expenses/{id}/` - Update expense
- `DELETE /api/expenses/{id}/` - Delete expense
- `GET /api/expenses/stats/` - Get expense statistics

### Budgets
- `GET /api/budgets/` - List budgets
- `POST /api/budgets/` - Create budget
- `GET /api/budgets/alerts/` - Get budget alerts

### Split Expenses
- `GET /api/groups/` - List groups
- `POST /api/groups/` - Create group
- `GET /api/shared-expenses/` - List shared expenses
- `POST /api/shared-expenses/` - Create shared expense
- `GET /api/split/balances/` - Get all balances
- `GET /api/split/groups/{id}/balances/` - Get group balances

### API Authentication
Use Token authentication:
```bash
# Include token in header:
Authorization: Token <your_token>
```

## Usage Guide

### 1. User Registration & Login
- Visit `/accounts/register/` to create an account
- Login at `/accounts/login/`

### 2. Adding Expenses
- Go to Dashboard → Click "Add Expense"
- Fill in amount, description, category, and date
- Optionally upload a receipt

### 3. Setting Budgets
- Navigate to "Budgets" → "Create Budget"
- Select category (or leave blank for overall)
- Set amount and date range
- Configure alert thresholds

### 4. Budget Guardian
- View alerts at "Budget Guardian" page
- Alerts appear when spending reaches thresholds
- Color-coded: Green (safe), Yellow (warning), Red (exceeded)

### 5. Split Expenses
- Create a group: "Split Expenses" → "Create Group"
- Add members by username
- Add shared expenses to the group
- Expenses are automatically split equally
- View balances: "View Balances" shows who owes whom

## Data Flow

### Expense Creation Flow
1. User submits expense form
2. `ExpenseForm` validates data
3. `expense_create_view` saves expense to database
4. Expense appears in dashboard and expense list

### Budget Alert Flow
1. User creates budget with alert thresholds
2. When expense is added, budget's `check_alerts()` is called
3. Method calculates spent amount vs budget
4. If threshold reached, alert is generated
5. Alerts displayed in Budget Guardian page

### Split Expense Flow
1. User creates group and adds members
2. User adds shared expense (amount + payer)
3. `split_equally()` method calculates per-person amount
4. Balance records created for each member (except payer)
5. Balances tracked in `Balance` model
6. Users can view "who owes whom" in balance view

## Key Logic Explained

### Budget Alerts
```python
def check_alerts(self):
    usage = self.get_usage_percentage()
    if usage >= 100 and self.alert_at_100:
        # Generate danger alert
    elif usage >= 90 and self.alert_at_90:
        # Generate warning alert
    # ... and so on
```

### Expense Splitting
```python
def split_equally(self):
    members = self.group.members.all()
    amount_per_person = self.amount / members.count()
    for member in members:
        if member != self.paid_by:
            Balance.objects.create(
                owed_by=member,
                owed_to=self.paid_by,
                amount=amount_per_person
            )
```

## Sample Test Data

After running migrations, you can create test data:

1. **Create Categories** (via admin or code):
   - Food 🍔
   - Transport 🚗
   - Entertainment 🎬
   - Shopping 🛍️
   - Bills 💳

2. **Create Test User**:
   - Username: `testuser`
   - Password: `testpass123`

3. **Add Sample Expenses**:
   - Various amounts across different categories
   - Different dates to see time-based statistics

4. **Create Budget**:
   - Set $500 monthly budget for Food
   - Add expenses to trigger alerts

5. **Create Group**:
   - Name: "Roommates"
   - Add 2-3 members
   - Add shared expenses

## Troubleshooting

### Common Issues

1. **Migration Errors**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Static Files Not Loading**:
   ```bash
   python manage.py collectstatic
   ```

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

4. **Database Errors**:
   - Delete `db.sqlite3` and run migrations again

## Development Notes

- **Architecture**: Follows Django MVT (Model-View-Template) pattern
- **Database**: SQLite (default, can be changed to PostgreSQL)
- **API**: Django REST Framework for RESTful endpoints
- **Frontend**: Bootstrap 5 + Chart.js for visualization
- **Security**: CSRF protection, authentication required for all views

## Future Enhancements

- Email notifications for budget alerts
- Export expenses to CSV/PDF
- Recurring expenses
- Custom split ratios (not just equal)
- Expense search and advanced filtering
- Mobile app integration

## License

This project is created for educational purposes (college mini-project/hackathon).

## Author

Student Expense Tracker - Django Web Application

---

**Note**: This is a beginner-friendly project suitable for learning Django, web development, and financial management systems.
