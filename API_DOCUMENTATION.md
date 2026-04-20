# API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication

All API endpoints (except registration and login) require authentication using Token Authentication.

### Get Your Token

1. **Register a new user:**
```bash
POST /api/auth/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
}
```

2. **Login to get token:**
```bash
POST /api/auth/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass123"
}

Response:
{
    "token": "your_auth_token_here",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        ...
    }
}
```

3. **Use token in requests:**
```bash
Authorization: Token your_auth_token_here
```

---

## Authentication Endpoints

### Register User
```http
POST /api/auth/register/
Content-Type: application/json

Request Body:
{
    "username": "string (required)",
    "email": "string (required)",
    "password": "string (required)",
    "first_name": "string (optional)",
    "last_name": "string (optional)"
}

Response: 201 Created
{
    "token": "auth_token",
    "user": { ... }
}
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

Request Body:
{
    "username": "string",
    "password": "string"
}

Response: 200 OK
{
    "token": "auth_token",
    "user": { ... }
}
```

### Logout
```http
POST /api/auth/logout/
Authorization: Token your_token

Response: 200 OK
{
    "message": "Logged out successfully"
}
```

---

## Expense Endpoints

### List Expenses
```http
GET /api/expenses/
Authorization: Token your_token

Response: 200 OK
[
    {
        "id": 1,
        "amount": "25.50",
        "description": "Lunch",
        "category": {
            "id": 1,
            "name": "Food",
            "icon": "🍔",
            "color": "#e74c3c"
        },
        "date": "2024-01-15",
        "created_at": "2024-01-15T10:30:00Z",
        ...
    },
    ...
]
```

### Create Expense
```http
POST /api/expenses/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "amount": "25.50",
    "description": "Lunch at cafeteria",
    "category_id": 1,
    "date": "2024-01-15"
}

Response: 201 Created
{
    "id": 1,
    "amount": "25.50",
    ...
}
```

### Get Expense
```http
GET /api/expenses/{id}/
Authorization: Token your_token

Response: 200 OK
{
    "id": 1,
    "amount": "25.50",
    ...
}
```

### Update Expense
```http
PUT /api/expenses/{id}/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "amount": "30.00",
    "description": "Updated description",
    ...
}

Response: 200 OK
{
    "id": 1,
    ...
}
```

### Delete Expense
```http
DELETE /api/expenses/{id}/
Authorization: Token your_token

Response: 204 No Content
```

### Get Expense Statistics
```http
GET /api/expenses/stats/
Authorization: Token your_token

Response: 200 OK
{
    "total_all_time": "500.00",
    "total_this_month": "250.00",
    "total_this_week": "75.00",
    "total_today": "25.50",
    "category_breakdown": [
        {
            "category__name": "Food",
            "total": "150.00",
            "count": 10
        },
        ...
    ]
}
```

---

## Category Endpoints

### List Categories
```http
GET /api/categories/
Authorization: Token your_token

Response: 200 OK
[
    {
        "id": 1,
        "name": "Food",
        "description": "",
        "icon": "🍔",
        "color": "#e74c3c"
    },
    ...
]
```

### Create Category
```http
POST /api/categories/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "name": "Food",
    "icon": "🍔",
    "color": "#e74c3c"
}

Response: 201 Created
```

---

## Budget Endpoints

### List Budgets
```http
GET /api/budgets/
Authorization: Token your_token

Response: 200 OK
[
    {
        "id": 1,
        "category": { ... },
        "amount": "500.00",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "is_active": true,
        "spent_amount": "250.00",
        "remaining_amount": "250.00",
        "usage_percentage": 50.0,
        ...
    },
    ...
]
```

### Create Budget
```http
POST /api/budgets/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "category_id": 1,
    "amount": "500.00",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "is_active": true,
    "alert_at_50": true,
    "alert_at_75": true,
    "alert_at_90": true,
    "alert_at_100": true
}

Response: 201 Created
```

### Get Budget Alerts (Budget Guardian)
```http
GET /api/budgets/alerts/
Authorization: Token your_token

Response: 200 OK
{
    "alerts": [
        {
            "level": "warning",
            "message": "Budget at 90.0%! You have spent $450.00 out of $500.00",
            "percentage": 90.0,
            "budget_id": 1,
            "budget_name": "Food - $500.00"
        },
        ...
    ],
    "count": 2
}
```

---

## Split Expense Endpoints

### List Groups
```http
GET /api/groups/
Authorization: Token your_token

Response: 200 OK
[
    {
        "id": 1,
        "name": "Roommates",
        "description": "Shared expenses",
        "created_by": { ... },
        "members": [ ... ],
        "member_count": 2,
        "total_expenses": "140.00",
        ...
    },
    ...
]
```

### Create Group
```http
POST /api/groups/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "name": "Roommates",
    "description": "Shared expenses with roommates"
}

Response: 201 Created
```

### Add Member to Group
```http
POST /api/groups/{id}/add_member/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "username": "friend1"
}

Response: 200 OK
{
    "message": "friend1 added to group"
}
```

### List Shared Expenses
```http
GET /api/shared-expenses/
Authorization: Token your_token

Response: 200 OK
[
    {
        "id": 1,
        "description": "Dinner",
        "amount": "60.00",
        "date": "2024-01-15",
        "paid_by": { ... },
        "group": { ... },
        ...
    },
    ...
]
```

### Create Shared Expense
```http
POST /api/shared-expenses/
Authorization: Token your_token
Content-Type: application/json

Request Body:
{
    "description": "Dinner at restaurant",
    "amount": "60.00",
    "date": "2024-01-15",
    "paid_by_id": 1,
    "group_id": 1
}

Response: 201 Created

Note: Expense is automatically split equally among group members
```

### Get All Balances
```http
GET /api/split/balances/
Authorization: Token your_token

Response: 200 OK
{
    "debts": [
        {
            "id": 1,
            "owed_by": { ... },
            "owed_to": { ... },
            "amount": "30.00",
            "is_settled": false,
            ...
        }
    ],
    "credits": [ ... ],
    "total_owed": "30.00",
    "total_owed_to_me": "40.00",
    "net_balance": "10.00"
}
```

### Get Group Balances
```http
GET /api/split/groups/{group_id}/balances/
Authorization: Token your_token

Response: 200 OK
{
    "group_id": 1,
    "balances": [ ... ],
    "member_balances": {
        "user1": {
            "owes": "30.00",
            "owed": "40.00",
            "net": "10.00"
        },
        "user2": {
            "owes": "40.00",
            "owed": "30.00",
            "net": "-10.00"
        }
    }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
    "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

---

## Example Usage with cURL

### Register User
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Create Expense
```bash
curl -X POST http://127.0.0.1:8000/api/expenses/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "25.50",
    "description": "Lunch",
    "category_id": 1,
    "date": "2024-01-15"
  }'
```

### Get Expense Statistics
```bash
curl -X GET http://127.0.0.1:8000/api/expenses/stats/ \
  -H "Authorization: Token your_token_here"
```

---

## Pagination

List endpoints support pagination:
- `GET /api/expenses/?page=1`
- `GET /api/expenses/?page=2`

Response includes pagination metadata:
```json
{
    "count": 100,
    "next": "http://127.0.0.1:8000/api/expenses/?page=2",
    "previous": null,
    "results": [ ... ]
}
```

---

## Notes

- All monetary amounts are in Decimal format (strings in JSON)
- Dates are in ISO 8601 format (YYYY-MM-DD)
- Timestamps are in ISO 8601 format with timezone
- All endpoints return JSON
- Authentication is required for all endpoints except registration and login
