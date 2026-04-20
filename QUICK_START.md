# Quick Start Guide

## Step-by-Step Setup (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### 4. Load Sample Data (Recommended for Testing)
```bash
python manage.py create_sample_data
```

This creates:
- Test user: `testuser` / `testpass123`
- Friend user: `friend1` / `testpass123`
- Sample categories, expenses, budgets, and groups

### 5. Run the Server
```bash
python manage.py runserver
```

### 6. Access the Application
Open your browser and go to:
- **Web Interface**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/

## First Steps After Setup

### 1. Login
- Use `testuser` / `testpass123` (if you loaded sample data)
- Or register a new account at `/accounts/register/`

### 2. Explore the Dashboard
- View expense statistics
- See category-wise spending charts
- Check budget usage

### 3. Add Your First Expense
- Click "Add Expense" from dashboard
- Fill in amount, description, category, and date
- Save and see it appear in your expense list

### 4. Create a Budget
- Go to "Budgets" → "Create Budget"
- Set a monthly budget for a category
- Configure alert thresholds
- Watch Budget Guardian alerts as you spend

### 5. Try Split Expenses
- Create a group: "Split Expenses" → "Create Group"
- Add a friend as a member
- Add a shared expense
- View balances to see who owes whom

## Common Tasks

### View All Expenses
- Navigate to "Expenses" in the menu
- Filter by category, date range, or search

### Check Budget Alerts
- Go to "Budget Guardian" to see all active alerts
- Alerts show when spending reaches 50%, 75%, 90%, or 100% of budget

### Manage Groups
- View all groups at "Split Expenses"
- Click on a group to see members, expenses, and balances
- Add members (if you're the creator)
- Add shared expenses that split automatically

### View Balances
- Go to "Split Expenses" → "View Balances"
- See who owes you and who you owe
- Settle balances when payments are made

## API Testing

### Get Your API Token
1. Login via web interface
2. Or use API:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### Make API Calls
```bash
# List expenses
curl -H "Authorization: Token YOUR_TOKEN" \
  http://127.0.0.1:8000/api/expenses/

# Create expense
curl -X POST http://127.0.0.1:8000/api/expenses/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":"25.50","description":"Lunch","category_id":1,"date":"2024-01-15"}'
```

See `API_DOCUMENTATION.md` for complete API reference.

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Errors
```bash
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
python manage.py create_sample_data
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Import Errors
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## Next Steps

1. **Customize Categories**: Add your own expense categories
2. **Set Real Budgets**: Create budgets based on your actual spending
3. **Invite Friends**: Create groups and start splitting expenses
4. **Explore API**: Build a mobile app or integrate with other tools
5. **Review Documentation**: Read `README.md` and `API_DOCUMENTATION.md`

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review `API_DOCUMENTATION.md` for API usage
3. Check `DATABASE_SCHEMA.md` for database structure
4. Review code comments for implementation details

---

**Happy Expense Tracking! 💰**
