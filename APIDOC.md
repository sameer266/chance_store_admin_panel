# Mobile App API Documentation

## Base URL
```
https://yourdomain.com/api/
```

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [Category APIs](#category-apis)
3. [Product APIs](#product-apis)
4. [Cart APIs](#cart-apis)
5. [Profile APIs](#profile-apis)
6. [Order APIs](#order-apis)
7. [Review APIs](#review-apis)
8. [Coupon APIs](#coupon-apis)
9. [Notification APIs](#notification-apis)

---

## Authentication APIs

### 1. Register
**Endpoint:** `POST /api/register/`

**Description:** Register a new user account. An OTP will be sent to the provided email.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully. Please verify OTP sent to your email."
}
```

---

### 2. Verify OTP
**Endpoint:** `POST /api/verify-otp/`

**Description:** Verify the OTP sent during registration to activate the account.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP verified successfully. Your account is now active."
}
```

---

### 3. Resend OTP
**Endpoint:** `POST /api/resend-otp/`

**Description:** Resend OTP to the user's email.

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Otp resend successfully"
}
```

---

### 4. Login
**Endpoint:** `POST /api/login/`

**Description:** Login with email and password to get JWT tokens.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "gender": "Male",
    "avatar": "http://example.com/media/avatar.jpg",
    "address": "123 Main St",
    "city": "New York"
  }
}
```

---

### 5. Logout
**Endpoint:** `POST /api/logout/`

**Description:** Logout and blacklist the refresh token.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

### 6. Token Refresh
**Endpoint:** `POST /api/token/refresh/`

**Description:** Refresh the access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 7. Forget Password
**Endpoint:** `POST /api/forget-password/`

**Description:** Request OTP for password reset.

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent to your email for password reset."
}
```

---

### 8. Forget Password Verify OTP
**Endpoint:** `POST /api/forget-password/verify-otp/`

**Description:** Verify OTP for password reset and get access token.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "OTP verified successfully. You can now reset your password."
}
```

---

### 9. Reset Password
**Endpoint:** `POST /api/reset-password/`

**Description:** Reset password after OTP verification.

**Authentication:** Required (JWT from forget password flow)

**Request Body:**
```json
{
  "new_password": "newSecurePassword123",
  "confirm_password": "newSecurePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

---

## Category APIs

### 10. Get All Categories
**Endpoint:** `GET /api/categories/`

**Description:** Get list of all product categories.

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "image": "http://example.com/media/categories/electronics.jpg"
    },
    {
      "id": 2,
      "name": "Fashion",
      "image": "http://example.com/media/categories/fashion.jpg"
    }
  ]
}
```

---

## Product APIs

### 11. Home
**Endpoint:** `GET /api/home/`

**Description:** Get home page data including sliders, featured categories, featured products, and best offers.

**Response:**
```json
{
  "success": true,
  "sliders": [
    {
      "id": 1,
      "image": "http://example.com/media/sliders/banner1.jpg"
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "image": "http://example.com/media/categories/electronics.jpg"
    }
  ],
  "featured_products": [
    {
      "id": 1,
      "name": "iPhone 15 Pro",
      "price": 999.00,
      "cost_price": 1299.00,
      "in_stock": true,
      "category": "Electronics",
      "main_image": "http://example.com/media/products/iphone.jpg"
    }
  ],
  "best_offers_products": [
    {
      "id": 2,
      "name": "Samsung TV",
      "price": 499.00,
      "cost_price": 799.00,
      "in_stock": true,
      "category": "Electronics",
      "main_image": "http://example.com/media/products/tv.jpg"
    }
  ]
}
```

---

### 12. All Collections
**Endpoint:** `GET /api/all-collections/`

**Description:** Get all products.

**Response:**
```json
{
  "success": true,
  "count": 50,
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "price": 99.99,
      "cost_price": 149.99,
      "in_stock": true,
      "category": "Category Name",
      "main_image": "http://example.com/media/products/product.jpg"
    }
  ]
}
```

---

### 13. New Arrivals
**Endpoint:** `GET /api/new-arrivals/`

**Description:** Get products added in the last 30 days.

**Response:**
```json
{
  "success": true,
  "count": 15,
  "new_arrivals": [
    {
      "id": 1,
      "name": "New Product",
      "price": 79.99,
      "cost_price": 99.99,
      "in_stock": true,
      "category": "Fashion",
      "main_image": "http://example.com/media/products/new.jpg"
    }
  ]
}
```

---

### 14. Filter Products
**Endpoint:** `GET /api/filter-products/`

**Description:** Filter products by category, brand, and price range.

**Query Parameters:**
- `category_name` (optional): Filter by category name
- `brand_name` (optional): Filter by brand name
- `min_price` (optional): Minimum price
- `max_price` (optional): Maximum price

**Example Request:**
```
GET /api/filter-products/?category_name=Electronics&min_price=100&max_price=500
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "products": [
    {
      "id": 1,
      "name": "Filtered Product",
      "price": 299.99,
      "cost_price": 399.99,
      "in_stock": true,
      "category": "Electronics",
      "main_image": "http://example.com/media/products/filtered.jpg"
    }
  ]
}
```

---

### 15. Search Products
**Endpoint:** `GET /api/search-products/`

**Description:** Search products by name, description, brand, or price.

**Query Parameters:**
- `query` (required): Search query string

**Example Request:**
```
GET /api/search-products/?query=phone
```

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": 1,
      "name": "iPhone 15 Pro",
      "price": 999.00,
      "cost_price": 1299.00,
      "in_stock": true,
      "category": "Electronics",
      "brand": "Apple",
      "main_image": "http://example.com/media/products/iphone.jpg"
    }
  ]
}
```

---

### 16. Product Details
**Endpoint:** `GET /api/product/{id}/`

**Description:** Get detailed information about a specific product.

**Example Request:**
```
GET /api/product/1/
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": 1,
    "name": "iPhone 15 Pro",
    "slug": "iphone-15-pro",
    "description": "Brand: Apple\nManufacturer: Apple Inc.\nCountry of Origin: USA",
    "price": 999.00,
    "cost_price": 1299.00,
    "in_stock": true,
    "category": "Electronics",
    "brand": "Apple",
    "main_image": "http://example.com/media/products/iphone.jpg",
    "shipping_cost": 10.00,
    "estimated_delivery_days": 3,
    "gallery": [
      "http://example.com/media/products/iphone_1.jpg",
      "http://example.com/media/products/iphone_2.jpg"
    ],
    "variants": [
      {
        "id": 1,
        "variant_type": "Color",
        "name": "Black",
        "price_adjustment": 0.00
      },
      {
        "id": 2,
        "variant_type": "Storage",
        "name": "256GB",
        "price_adjustment": 100.00
      }
    ]
  }
}
```

---

### 17. Category Products
**Endpoint:** `GET /api/category/{category_id}/products/`

**Description:** Get all products in a specific category.

**Example Request:**
```
GET /api/category/1/products/
```

**Response:**
```json
{
  "success": true,
  "featured_category": "Electronics",
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "price": 99.99,
      "cost_price": 149.99,
      "in_stock": true,
      "category": "Electronics",
      "main_image": "http://example.com/media/products/product.jpg"
    }
  ]
}
```

---

## Cart APIs

### 18. Add to Cart
**Endpoint:** `POST /api/cart-add/`

**Description:** Add a product to the cart.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response:**
```json
{
  "success": true,
  "message": "Product added to cart successfully."
}
```

---

### 19. View Cart
**Endpoint:** `GET /api/cart/`

**Description:** Get all items in the user's cart.

**Authentication:** Required (JWT)

**Response:**
```json
{
  "success": true,
  "cart_items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "iPhone 15 Pro",
      "image": "http://example.com/media/products/iphone.jpg",
      "quantity": 2,
      "price": 999.00,
      "total_price": 1998.00
    }
  ]
}
```

---

### 20. Update Cart Item
**Endpoint:** `POST /api/cart-update/`

**Description:** Update quantity of a cart item.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "cart_item_id": 1,
  "quantity": 3
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cart item updated successfully."
}
```

---

### 21. Remove from Cart
**Endpoint:** `POST /api/cart-remove/`

**Description:** Remove an item from the cart.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "cart_item_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cart item removed successfully."
}
```

---

## Profile APIs

### 22. Customer Profile
**Endpoint:** `GET /api/customer-profile/`

**Description:** Get the logged-in user's profile information.

**Authentication:** Required (JWT)

**Response:**
```json
{
  "success": true,
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "gender": "Male",
    "avatar": "http://example.com/media/avatars/john.jpg",
    "address": "123 Main St",
    "city": "New York"
  }
}
```

---

### 23. Edit Profile
**Endpoint:** `POST /api/edit-profile/`

**Description:** Update user profile information.

**Authentication:** Required (JWT)

**Request Body (FormData):**
```
first_name: John
last_name: Doe
email: john.doe@example.com
phone: 1234567890
gender: Male
avatar: [file]
address: 123 Main St
city: New York
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully."
}
```

---

### 24. Change Password
**Endpoint:** `POST /api/change-password/`

**Description:** Change the user's password.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword123",
  "confirm_password": "newPassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully."
}
```

---

## Order APIs

### 25. Checkout
**Endpoint:** `POST /api/checkout/`

**Description:** Place an order with items from the cart.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "full_name": "John Doe",
  "phone": "1234567890",
  "email": "john.doe@example.com",
  "address": "123 Main St",
  "city": "New York",
  "province": "NY",
  "payment_method": "cod",
  "coupon_code": "SAVE10"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Order placed successfully.",
  "order_id": "ORD-20250107-001"
}
```

---

### 26. Order History
**Endpoint:** `GET /api/customer-orders/`

**Description:** Get all orders placed by the user.

**Authentication:** Required (JWT)

**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "id": 1,
      "products": [
        {
          "product_name": "iPhone 15 Pro",
          "main_image": "http://example.com/media/products/iphone.jpg",
          "quantity": 1,
          "price": 999.00
        }
      ],
      "order_number": "ORD-20250107-001",
      "total_amount": 1109.00,
      "status": "pending",
      "created_at": "2025-01-07T10:30:00Z"
    }
  ]
}
```

---

### 27. Order Details
**Endpoint:** `GET /api/customer-order/{order_id}/`

**Description:** Get detailed information about a specific order.

**Authentication:** Required (JWT)

**Example Request:**
```
GET /api/customer-order/ORD-20250107-001/
```

**Response:**
```json
{
  "success": true,
  "order": {
    "id": 1,
    "products": [
      {
        "product_name": "iPhone 15 Pro",
        "main_image": "http://example.com/media/products/iphone.jpg",
        "quantity": 1,
        "price": 999.00
      }
    ],
    "order_number": "ORD-20250107-001",
    "subtotal": 999.00,
    "shipping_cost": 100.00,
    "shipping_full_name": "John Doe",
    "shipping_phone": "1234567890",
    "shipping_address": "123 Main St",
    "shiiping_city": "New York",
    "shipping_province": "NY",
    "shipping_email": "john.doe@example.com",
    "shipping_postal_code": "10001",
    "discount": 10.00,
    "tax_amount": 20.00,
    "total_amount": 1109.00,
    "estimated_delivery_date": "2025-01-10",
    "status": "pending",
    "created_at": "2025-01-07T10:30:00Z"
  }
}
```

---

## Review APIs

### 28. Product Reviews
**Endpoint:** `GET /api/product/{product_id}/reviews/`

**Description:** Get all reviews for a specific product.

**Authentication:** Required (JWT)

**Example Request:**
```
GET /api/product/1/reviews/
```

**Response:**
```json
{
  "success": true,
  "reviews": [
    {
      "id": 1,
      "user": "John Doe",
      "rating": 5,
      "comment": "Excellent product!",
      "created_at": "2025-01-05 14:30:00"
    }
  ]
}
```

---

### 29. Submit Review
**Endpoint:** `POST /api/product/{product_id}/reviews/`

**Description:** Submit a review for a product.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great product, highly recommended!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Review submitted successfully."
}
```

---

## Coupon APIs

### 30. Verify Coupon
**Endpoint:** `POST /api/coupon/verify/`

**Description:** Verify a coupon code and get discount information.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "code": "SAVE10"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Coupon applied successfully",
  "discount_amount": 50.00,
  "code": "SAVE10"
}
```

---

## Notification APIs

### 31. Get Notifications
**Endpoint:** `GET /api/notifications/`

**Description:** Get all notifications for the logged-in user.

**Authentication:** Required (JWT)

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "order",
      "title": "Order ORD-20250107-001 Placed",
      "message": "Your order ORD-20250107-001 has been placed successfully.",
      "link": null,
      "is_read": false,
      "created_at": "2025-01-07T10:30:00Z"
    }
  ]
}
```

---

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

When the access token expires, use the refresh token to get a new one via the `/api/token/refresh/` endpoint.

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

---

## Notes

1. All endpoints return JSON responses
2. Dates are in ISO 8601 format
3. Prices are in decimal format
4. File uploads should use `multipart/form-data`
5. Regular POST requests should use `application/json`
6. The base URL should be updated to match your production domain

---

**Last Updated:** January 7, 2025
**API Version:** 1.0