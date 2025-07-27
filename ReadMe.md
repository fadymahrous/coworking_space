# 📟 Project Overview

The goal of this Django project is to develop a robust backend system for a co-working space application. The backend supports four main components:

### 1. Account Management

Provides user registration, login, and authentication via both a web interface and APIs secured with JWT.

### 2. Customer Interface (Home Page)

Allows users to browse menus and available services, and place food or service orders directly from their table through a web interface or API.

### 3. Worker Interface

Enables staff members to manage their shifts and process customer orders efficiently.

### 4. Watcher Interface (Admin Panel)

Grants administrative users the ability to update the menu, manage inventory, and review financial reports.

---

# 🌐 Web Views Documentation

### `welcome(request)`

- **URL**: `/home/`
- **Method**: GET
- **Login Required**: ✅
- **Purpose**: Renders the home page showing:
  - The current user's wallet balance.
  - Total value of served (unpaid) orders.
- **Template**: `home.html`

### `food_view(request)`

- **URL**: `/home/menue/`
- **Methods**: GET, POST
- **Login Required**: ✅
- **Purpose**:
  - GET: Displays categorized menu items.
  - POST: Adds items to the user's cart.
- **Template**: `menue.html`

### `cart_view(request)`

- **URL**: `/home/cart/`
- **Methods**: GET, POST
- **Login Required**: ✅
- **Purpose**:
  - View, update, or remove cart items.
  - Submit the cart for processing.
- **Template**: `cart.html`

### `bill_view(request)`

- **URL**: `/home/bill/`
- **Method**: GET
- **Login Required**: ✅
- **Purpose**: Displays all served items and calculates the total bill.
- **Template**: `bill.html`

---

# 🔌 API Endpoints

All API endpoints require **JWT authentication**.
# Restaurant API Documentation

## Base URL
```
/v1/api/
```

## Authentication
All API endpoints require authentication. Include the authentication token in your request headers.

```
Authorization: Bearer <your-token>
```

---

## 1. Menu API

### Get Menu Items
Retrieve all available menu items.

**Endpoint:** `GET /v1/api/foodmenue/`

**Response:**
```json
{
    "message": "Items fetched successfully",
    "data": [
        {
            "item_name": "Margherita Pizza",
            "item_description": "Classic pizza with tomatoes and mozzarella",
            "price": 12.99
        },
        {
            "item_name": "Caesar Salad",
            "item_description": "Fresh romaine lettuce with caesar dressing",
            "price": 8.50
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Items retrieved successfully
- `500 Internal Server Error` - Failed to fetch items

---

## 2. Cart API

### Get Cart Contents
Retrieve all items currently in the user's cart.

**Endpoint:** `GET /v1/api/cart/`

**Response:**
```json
{
    "message": "Cart items fetched",
    "data": [
        {
            "item_name": "Margherita Pizza",
            "count": 2
        },
        {
            "item_name": "Caesar Salad", 
            "count": 1
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Cart items retrieved successfully
- `404 Not Found` - Cart is empty
- `500 Internal Server Error` - Failed to fetch cart items

### Add/Update Cart Item
Add a new item to cart or update the quantity of an existing item.

**Endpoint:** `POST /v1/api/cart/`

**Request Body:**
```json
{
    "item_name": "Margherita Pizza",
    "count": 2
}
```

**Response:**
```json
{
    "message": "Update the Cart successfully"
}
```

**Validation Rules:**
- `item_name`: Must be a valid menu item name
- `count`: Must be greater than 0

**Status Codes:**
- `200 OK` - Item added/updated successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Item not found or failed to update

### Remove Cart Item
Remove an item completely from the cart.

**Endpoint:** `DELETE /v1/api/cart/`

**Request Body:**
```json
{
    "item_name": "Margherita Pizza"
}
```

**Response:**
```json
{
    "message": "Item deleted"
}
```

**Status Codes:**
- `200 OK` - Item removed successfully
- `500 Internal Server Error` - Failed to delete item

---

## 3. Order API

### Submit Cart to Kitchen
Send current cart items to the kitchen for preparation.

**Endpoint:** `POST /v1/api/order/`

**Request Body:**
```json
{
    "table_number": 5
}
```

**Response:**
```json
{
    "message": "Your cart sent to kitchen"
}
```

**Status Codes:**
- `200 OK` - Order submitted successfully
- `406 Not Acceptable` - Failed to send cart to kitchen

### Get Active Orders
Retrieve all active orders for the current user.

**Endpoint:** `GET /v1/api/order/`

**Response:**
```json
{
    "message": "Orders returned successfully",
    "data": {
        "status": "In Progress",
        "order_creation_time": "2025-07-28T10:30:00Z",
        "table_number": 5
    }
}
```

**Status Codes:**
- `200 OK` - Orders retrieved successfully
- `500 Internal Server Error` - Failed to list orders

---

## 4. Bill API

### Get Current Bill
Retrieve items that are ready to be billed (served orders).

**Endpoint:** `GET /v1/api/bill/`

**Response:**
```json
{
    "message": "Successfully retrieved Bill view",
    "data": [
        {
            "item_name": "Margherita Pizza",
            "count": 2
        },
        {
            "item_name": "Caesar Salad",
            "count": 1
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Bill details retrieved successfully
- `500 Internal Server Error` - Failed to retrieve bill

### Request Bill Payment
Submit the current bill for payment processing.

**Endpoint:** `POST /v1/api/bill/`

**Request Body:** No body required

**Response:**
```json
{
    "messages": "Bill submitted to Cashier"
}
```

**Status Codes:**
- `200 OK` - Bill submitted successfully
- `404 Not Found` - No orders to be billed found
- `500 Internal Server Error` - Failed to request bill

---

## Error Response Format

All error responses follow this format:

```json
{
    "error": "Error description message"
}
```

**Common Error Status Codes:**
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `406 Not Acceptable` - Request cannot be processed
- `500 Internal Server Error` - Server error

---

## API Flow

### Typical User Journey:

1. **Browse Menu**: `GET /v1/api/foodmenue/`
2. **Add Items to Cart**: `POST /v1/api/cart/` (repeat as needed)
3. **Review Cart**: `GET /v1/api/cart/`
4. **Update Cart Items**: `POST /v1/api/cart/` (optional)
5. **Submit Order**: `POST /v1/api/order/`
6. **Check Order Status**: `GET /v1/api/order/`
7. **View Bill**: `GET /v1/api/bill/` (when order is served)
8. **Request Payment**: `POST /v1/api/bill/`

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Item names are case-sensitive and must match exactly with menu items
- Cart operations are user-specific and isolated
- Orders cannot be cancelled once submitted to kitchen
- Bills are automatically calculated based on served orders

---

# 📆 Data Models Summary
# Database Schema Documentation

## Table Structure & Relationships

---

## 1. accounts_app_user (User Table)
*Note: Referenced from accounts_app*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | User ID |
| username | CharField | UNIQUE | User login name |
| email | EmailField | UNIQUE | User email |
| ... | ... | ... | *Other user fields* |

---

## 2. watchers_app_categorization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Category ID |
| main_category | CharField(100) | NOT NULL, INDEXED | Main category (e.g., "Food & Drinks") |
| sub_category | CharField(100) | NOT NULL, INDEXED | Sub category (e.g., "Pizza") |
| exposure | BooleanField | NOT NULL | Visibility to customers |

**Constraints:**
- `UNIQUE(main_category, sub_category)` - unique_main_sub

---

## 3. watchers_app_tofaproductsrepository

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| item_name | CharField(100) | **PRIMARY KEY** | Unique item identifier |
| category_id | ForeignKey | NOT NULL | → watchers_app_categorization.id |
| brand | CharField(100) | NOT NULL | Item brand |
| price | FloatField | NOT NULL | Item price |
| item_description | CharField(1000) | NOT NULL | Item description |
| item_quantity | BigIntegerField | DEFAULT 0 | Available stock |

**Constraints:**
- `UNIQUE(item_name, category_id, brand)` - product_uniqueness
- `CHECK(item_quantity >= 0)` - quantity validation

---

## 4. watchers_app_bill_id

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Bill ID |
| bill_value | BigIntegerField | DEFAULT 0 | Total bill amount |
| bill_user_id | ForeignKey | NOT NULL | → accounts_app_user.id |
| bill_issue_time | DateTimeField | AUTO_ADD | Bill creation time |
| bill_status | CharField | DEFAULT 'CUSTOMER_REQUEST_TO_CLOSE' | Bill status |
| bill_closure_time | DateTimeField | NULL | Bill settlement time |

**Status Choices:**
- `'CUSTOMER_REQUEST_TO_CLOSE'`
- `'SETTELLED'`
- `'RETURNED_TO_CUSTOMER'`

---

## 5. watchers_app_tofaproductsorderid

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Order ID |
| status | CharField(20) | DEFAULT 'INPreparation', INDEXED | Order status |
| order_creation_time | DateTimeField | AUTO_ADD | Order creation time |
| fullfilled_at | DateTimeField | NULL | Order completion time |
| user_id | ForeignKey | NOT NULL | → accounts_app_user.id |
| table_number | IntegerField | NULL | Restaurant table number |
| bill_number_id | ForeignKey | NULL | → watchers_app_bill_id.id |

**Status Choices:**
- `'INPreparation'`
- `'Served'`
- `'PAID_Closed'`

---

## 6. watchers_app_tofaproductsorder

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Order item ID |
| item_name_id | ForeignKey | NOT NULL | → watchers_app_tofaproductsrepository.item_name |
| user_id | ForeignKey | NOT NULL | → accounts_app_user.id |
| placed_in_cart_at | DateTimeField | AUTO_ADD, NULL | Cart addition time |
| count | IntegerField | NOT NULL | Item quantity |
| order_number_id | ForeignKey | NULL | → watchers_app_tofaproductsorderid.id |

**Constraints:**
- `UNIQUE(item_name_id, user_id, status, order_number_id)` - unique_item_incart
- `CHECK(count > 0)` - count_must_be_positive

**States:**
- `order_number_id = NULL` → Item in cart
- `order_number_id = <value>` → Item in order

---

## Database Relationships Diagram

```
accounts_app_user (User)
├── watchers_app_tofaproductsorder (user_id) [One-to-Many]
├── watchers_app_tofaproductsorderid (user_id) [One-to-Many]
└── watchers_app_bill_id (bill_user_id) [One-to-Many]

watchers_app_categorization
└── watchers_app_tofaproductsrepository (category_id) [One-to-Many]

watchers_app_tofaproductsrepository
└── watchers_app_tofaproductsorder (item_name_id) [One-to-Many]

watchers_app_tofaproductsorderid
├── watchers_app_tofaproductsorder (order_number_id) [One-to-Many]
└── watchers_app_bill_id (bill_number_id) [One-to-Many] (reverse)

watchers_app_bill_id
└── watchers_app_tofaproductsorderid (bill_number_id) [One-to-Many]

---

# 🛠️ Watcher Interface (`watchers_app`)

Provides administrative control over product categorization, inventory, and financial reporting.

### 🔐 Permissions

All views are protected with `@permission_required('watchers_app.view_categorization')`. Unauthorized access redirects to `/watcher/NotAutohrized/`.

### 🔍 Routes and Views

#### `GET /watcher/`

Redirects to appropriate admin section based on `GoTo` parameter.

#### `GET | POST /watcher/addcategory/`

- Add or delete product categories.
- Uses `Categorization_Form`.

#### `GET | POST /watcher/addgoods/`

- Add, update, delete, or top up product inventory.
- Uses `TofaProductsRepository_form`.

#### `GET /watcher/reports/`

Placeholder for revenue/operations reports.

#### `GET /watcher/NotAutohrized/`

Displays unauthorized access template.

### 🗃️ Watcher Models Summary

#### `Categorization`

| Field           | Description                      |
| --------------- | -------------------------------- |
| `main_category` | Top-level category               |
| `sub_category`  | Sub-category                     |
| `exposure`      | Boolean flag for user visibility |

---

# 👷‍♂️ Worker Interface (`workers_app`)

Allows staff to manage shifts and handle customer orders.

### 🔐 Access

Currently unprotected, but should use `@login_required` or `@permission_required` in production.

### 🔍 Routes and Views

#### `GET /worker/`

Displays the main dashboard for workers.

#### `GET /worker/pick_shift/`

Placeholder for shift selection UI.

#### `GET | POST /worker/ongoing_orders/`

- GET: Lists orders in `INPreparation`.
- POST: Marks order as `Served`.

### 📟 Order Status Flow

| Status           | Role     | Trigger              |
| ---------------- | -------- | -------------------- |
| `INCart_Pending` | Customer | Adds item to cart    |
| `INPreparation`  | System   | Confirms cart        |
| `Served`         | Worker   | Order marked done    |
| `PAID_Closed`    | Admin    | Bill paid and closed |

---

# 👤 Accounts Interface (`accounts_app`)

Handles user management: registration, login, logout, and profile updates.

### 📆 Custom User Model

| Field         | Description              |
| ------------- | ------------------------ |
| `email`       | Unique email address     |
| `birthdate`   | Optional birth date      |
| `nationalid`  | Optional national ID     |
| `phonenumber` | Required phone number    |
| `wallet`      | Wallet balance (decimal) |

### 🔐 Web Views

#### `POST /login/`

Logs in the user.

#### `GET | POST /create_view/`

User registration.

#### `GET /logout/`

Logs out the user.

### 🌐 API Endpoints

#### `POST /api/createuser/`

Creates a new user.

#### `GET /api/createuser/`

Displays required fields for creation.

#### `GET /api/updateuser/`

Fetches current user data.

#### `PUT /api/updateuser/`

Updates user details.

#### `DELETE /api/deleteuser/`

Deletes the authenticated user.

---

# 🚀 Upcoming Phases Enhancements for Production Readiness

### 🧐 Business Logic

- Add backend support for worker shift tracking.
- Implement customer feedback collection module.
- Add API endpoints for Punch In/Punch Out functionality

### 🔐 Security & Permissions

- Enable CSRF protection where needed; exempt APIs explicitly.
- Enforce HTTPS, secure cookies, and proper permission naming using:
  ```python
  'app_label.permission_codename'
  ```

### ⚙️ API Scalability

- Add rate limiting via DRF throttles.
- Implement pagination for cart and billing endpoints.
- Use caching for menu and static content.

### 📆 Deployment Readiness

- Configure Gunicorn and Nginx.
- Load sensitive configs via `.env` using `django-environ`.


### 🎨 UI/UX Improvements

- Add custom 403/404 pages.
- Improve validation feedback.
- Use toast/snackbar notifications for better UX.




---

