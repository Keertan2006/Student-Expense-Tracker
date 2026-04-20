# Database Schema Documentation

## Overview

The Student Expense Tracker uses SQLite (default) or PostgreSQL database. This document describes the database schema and relationships.

## Entity Relationship Diagram

```
User (Django built-in)
├── Expense (1:N)
├── Budget (1:N)
└── Group (1:N as creator)
    └── Group.members (M:N)
        └── SharedExpense (1:N)
            └── Balance (1:N)

Category
└── Expense (1:N)
└── Budget (1:N)
```

## Tables

### 1. auth_user (Django Built-in)
Django's default User model for authentication.

**Fields:**
- `id` (Primary Key, Auto-increment)
- `username` (String, Unique, Max 150 chars)
- `email` (String, Optional)
- `password` (String, Hashed)
- `first_name` (String, Max 150 chars)
- `last_name` (String, Max 150 chars)
- `is_active` (Boolean)
- `is_staff` (Boolean)
- `is_superuser` (Boolean)
- `date_joined` (DateTime)
- `last_login` (DateTime, Optional)

**Relationships:**
- One-to-Many with `expenses_expense`
- One-to-Many with `budgets_budget`
- One-to-Many with `split_expenses_group` (as creator)
- Many-to-Many with `split_expenses_group` (as member)

---

### 2. expenses_category
Stores expense categories (Food, Transport, etc.).

**Fields:**
- `id` (Primary Key, Auto-increment)
- `name` (String, Unique, Max 100 chars)
- `description` (Text, Optional)
- `icon` (String, Max 50 chars, Default: '💰')
- `color` (String, Max 20 chars, Default: '#3498db')

**Relationships:**
- One-to-Many with `expenses_expense`
- One-to-Many with `budgets_budget`

**Indexes:**
- Index on `name`

**Sample Data:**
- Food 🍔 (#e74c3c)
- Transport 🚗 (#3498db)
- Entertainment 🎬 (#9b59b6)
- Shopping 🛍️ (#f39c12)
- Bills 💳 (#2ecc71)

---

### 3. expenses_expense
Stores individual expense records.

**Fields:**
- `id` (Primary Key, Auto-increment)
- `amount` (Decimal, Max 10 digits, 2 decimal places)
- `description` (String, Max 255 chars)
- `category_id` (Foreign Key → `expenses_category`, Nullable)
- `user_id` (Foreign Key → `auth_user`, NOT NULL)
- `date` (Date, Default: today)
- `receipt` (Image, Optional, Upload to 'receipts/')
- `created_at` (DateTime, Auto-set on create)
- `updated_at` (DateTime, Auto-update on save)

**Relationships:**
- Many-to-One with `auth_user`
- Many-to-One with `expenses_category` (Nullable)

**Indexes:**
- Composite index on (`user_id`, `date`)
- Index on `category_id`

**Constraints:**
- `amount` must be >= 0
- `user_id` is required

---

### 4. budgets_budget
Stores budget limits and alert configurations.

**Fields:**
- `id` (Primary Key, Auto-increment)
- `user_id` (Foreign Key → `auth_user`, NOT NULL)
- `category_id` (Foreign Key → `expenses_category`, Nullable)
- `amount` (Decimal, Max 10 digits, 2 decimal places)
- `start_date` (Date, Default: today)
- `end_date` (Date, NOT NULL)
- `alert_at_50` (Boolean, Default: True)
- `alert_at_75` (Boolean, Default: True)
- `alert_at_90` (Boolean, Default: True)
- `alert_at_100` (Boolean, Default: True)
- `is_active` (Boolean, Default: True)
- `created_at` (DateTime, Auto-set on create)
- `updated_at` (DateTime, Auto-update on save)

**Relationships:**
- Many-to-One with `auth_user`
- Many-to-One with `expenses_category` (Nullable - null means overall budget)

**Indexes:**
- Composite index on (`user_id`, `is_active`)

**Business Logic:**
- If `category_id` is NULL, budget applies to all expenses
- Budget period is defined by `start_date` and `end_date`
- Alert thresholds trigger when spending reaches specified percentages

---

### 5. split_expenses_group
Stores expense sharing groups.

**Fields:**
- `id` (Primary Key, Auto-increment)
- `name` (String, Max 100 chars)
- `description` (Text, Optional)
- `created_by_id` (Foreign Key → `auth_user`, NOT NULL)
- `created_at` (DateTime, Auto-set on create)
- `updated_at` (DateTime, Auto-update on save)

**Relationships:**
- Many-to-One with `auth_user` (as creator)
- Many-to-Many with `auth_user` (as members) via `split_expenses_group_members`

**Business Logic:**
- Creator is automatically added as a member
- Members can add shared expenses to the group

---

### 6. split_expenses_group_members (Junction Table)
Many-to-Many relationship between Groups and Users.

**Fields:**
- `id` (Primary Key, Auto-increment)
- `group_id` (Foreign Key → `split_expenses_group`)
- `user_id` (Foreign Key → `auth_user`)

**Constraints:**
- Unique constraint on (`group_id`, `user_id`)

---

### 7. split_expenses_sharedexpense
Stores shared expenses within groups.

**Fields:**
- `id` (Primary Key, Auto-increment)
- `description` (String, Max 255 chars)
- `amount` (Decimal, Max 10 digits, 2 decimal places)
- `paid_by_id` (Foreign Key → `auth_user`, NOT NULL)
- `group_id` (Foreign Key → `split_expenses_group`, NOT NULL)
- `date` (Date, Default: today)
- `created_at` (DateTime, Auto-set on create)
- `updated_at` (DateTime, Auto-update on save)

**Relationships:**
- Many-to-One with `auth_user` (payer)
- Many-to-One with `split_expenses_group`

**Business Logic:**
- When created, automatically splits amount equally among all group members
- Creates `Balance` records for each member (except payer)

---

### 8. split_expenses_balance
Tracks who owes whom (debts and credits).

**Fields:**
- `id` (Primary Key, Auto-increment)
- `expense_id` (Foreign Key → `split_expenses_sharedexpense`, Nullable)
- `owed_by_id` (Foreign Key → `auth_user`, NOT NULL)
- `owed_to_id` (Foreign Key → `auth_user`, NOT NULL)
- `amount` (Decimal, Max 10 digits, 2 decimal places)
- `is_settled` (Boolean, Default: False)
- `settled_at` (DateTime, Nullable)
- `created_at` (DateTime, Auto-set on create)

**Relationships:**
- Many-to-One with `split_expenses_sharedexpense` (Nullable - null for simplified balances)
- Many-to-One with `auth_user` (as debtor)
- Many-to-One with `auth_user` (as creditor)

**Indexes:**
- Composite index on (`owed_by_id`, `owed_to_id`, `is_settled`)

**Business Logic:**
- Represents a debt: `owed_by` owes `amount` to `owed_to`
- When `is_settled` is True, the balance is considered paid
- `expense_id` can be NULL for simplified/consolidated balances

**Example:**
- If User A pays $60 for a group of 3, two Balance records are created:
  - User B owes $20 to User A
  - User C owes $20 to User A

---

## Database Queries Examples

### Get User's Total Expenses This Month
```sql
SELECT SUM(amount) 
FROM expenses_expense 
WHERE user_id = 1 
  AND date >= '2024-01-01' 
  AND date <= '2024-01-31';
```

### Get Budget Alerts
```sql
SELECT b.*, 
       (SELECT COALESCE(SUM(e.amount), 0) 
        FROM expenses_expense e 
        WHERE e.user_id = b.user_id 
          AND e.category_id = b.category_id 
          AND e.date BETWEEN b.start_date AND b.end_date) as spent
FROM budgets_budget b
WHERE b.is_active = 1
  AND b.user_id = 1;
```

### Get Group Balances
```sql
SELECT 
    u1.username as owed_by,
    u2.username as owed_to,
    SUM(b.amount) as total_amount
FROM split_expenses_balance b
JOIN auth_user u1 ON b.owed_by_id = u1.id
JOIN auth_user u2 ON b.owed_to_id = u2.id
WHERE b.is_settled = 0
  AND b.expense_id IN (
      SELECT id FROM split_expenses_sharedexpense 
      WHERE group_id = 1
  )
GROUP BY b.owed_by_id, b.owed_to_id;
```

---

## Migration Commands

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### View SQL for Migration
```bash
python manage.py sqlmigrate app_name migration_number
```

---

## Data Integrity

### Foreign Key Constraints
- All foreign keys have `on_delete` constraints:
  - `CASCADE`: Delete related records when parent is deleted
  - `SET_NULL`: Set to NULL when parent is deleted (for optional relationships)

### Unique Constraints
- `expenses_category.name`: Unique
- `auth_user.username`: Unique
- `split_expenses_group_members`: Unique on (group_id, user_id)

### Check Constraints
- `expenses_expense.amount` >= 0
- `budgets_budget.amount` >= 0
- `split_expenses_sharedexpense.amount` >= 0
- `split_expenses_balance.amount` >= 0

---

## Performance Considerations

### Indexes
- User and date indexes on expenses for fast filtering
- Category indexes for category-based queries
- Composite indexes on balances for balance lookups

### Query Optimization
- Use `select_related()` for foreign key relationships
- Use `prefetch_related()` for many-to-many relationships
- Aggregate queries use database-level SUM/COUNT for efficiency

---

## Sample Data Population

Use the management command to populate sample data:
```bash
python manage.py create_sample_data
```

This creates:
- 6 categories
- 2 test users
- 8 sample expenses
- 1 budget
- 1 group with 2 shared expenses

---

## Backup and Restore

### Backup SQLite Database
```bash
cp db.sqlite3 db_backup.sqlite3
```

### Restore
```bash
cp db_backup.sqlite3 db.sqlite3
```

### Export to SQL
```bash
python manage.py dumpdata > data.json
```

### Import from SQL
```bash
python manage.py loaddata data.json
```
