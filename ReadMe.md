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

### `GET /api/foodviewapi/`

Returns all available food and drink items.

### `GET /api/cartviewapi/`

Fetches current cart items for the authenticated user.

### `POST /api/cartviewapi/`

Adds or updates an item in the cart.

```json
{
  "item_name": "<item_name>",
  "count": 2,
  "table_number": null
}
```

### `DELETE /api/cartviewapi/`

Removes an item from the cart.

```json
{
  "item_name": "Coca Cola"
}
```

### `POST /api/cartviewsubmitapi/`

Submits the current cart for preparation.

```json
{
  "table_number": 7
}
```

### `GET /api/getbill/`

Fetches all served items for billing.

---

# 📆 Data Models Summary

### `TofaProductsOrder`

| Field          | Description             |
| -------------- | ----------------------- |
| `item_name`    | ForeignKey to product   |
| `user`         | ForeignKey to user      |
| `status`       | Order status            |
| `count`        | Quantity                |
| `table_number` | Table number (optional) |

### `TofaProductsRepository`

| Field              | Description            |
| ------------------ | ---------------------- |
| `item_name`        | Primary key (string)   |
| `category`         | ForeignKey to category |
| `brand`            | Product brand          |
| `price`            | Product price          |
| `item_description` | Text description       |
| `item_quantity`    | Inventory stock count  |

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

