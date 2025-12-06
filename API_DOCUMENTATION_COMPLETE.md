# 📚 مستندات کامل API موبایل - Asia Salman

## 🎯 مقدمه

این مستندات شامل تمام endpoint های API موبایل برای نرم‌افزار اندروید است. تمام API ها کامل شده و آماده استفاده هستند.

---

## 📍 Base URL

```
/api/mobile/v1
```

---

## 🔐 Authentication

### 1. ارسال کد تایید (OTP)
**POST** `/auth/send-otp`

**Request Body:**
```json
{
  "phone": "09123456789"
}
```

**Response:**
```json
{
  "success": true,
  "message": "کد تایید ارسال شد",
  "data": {
    "expires_in": 120
  }
}
```

---

### 2. تایید کد و ورود
**POST** `/auth/verify-otp`

**Request Body:**
```json
{
  "phone": "09123456789",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "ورود موفقیت‌آمیز",
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "user": {
      "id": 1,
      "full_name": "...",
      "phone": "..."
    }
  }
}
```

---

### 3. تازه‌سازی توکن
**POST** `/auth/refresh-token`

**Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "..."
  }
}
```

---

### 4. خروج از حساب
**POST** `/auth/logout`

**Headers:**
```
Authorization: Bearer {access_token}
```

---

## 📦 Products

### 1. لیست محصولات
**GET** `/products?page=1&per_page=20&brand_id=1&category_id=2&vehicle_type_id=3`

**Query Parameters:**
- `page` (optional): شماره صفحه
- `per_page` (optional): تعداد در هر صفحه (حداکثر 100)
- `brand_id` (optional): فیلتر بر اساس برند
- `category_id` (optional): فیلتر بر اساس دسته‌بندی
- `vehicle_type_id` (optional): فیلتر بر اساس نوع خودرو
- `min_price` (optional): حداقل قیمت
- `max_price` (optional): حداکثر قیمت
- `in_stock` (optional): فقط موجودی (true/false)

**Response:**
```json
{
  "success": true,
  "data": {
    "products": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 2. جزئیات محصول
**GET** `/products/{id}`

**Headers (optional):**
```
Authorization: Bearer {access_token}
```

---

### 3. جستجوی محصولات
**GET** `/products/search?q=ترمز&page=1&per_page=20`

---

### 4. دریافت فیلترها
**GET** `/products/filters`

---

## 📂 Categories

### 1. لیست دسته‌بندی‌ها
**GET** `/categories`

### 2. دسته‌بندی بر اساس خودرو
**GET** `/categories/vehicle-based`

### 3. دسته‌بندی بر اساس برند
**GET** `/categories/brand-based`

### 4. محصولات یک دسته
**GET** `/categories/{id}/products?page=1&per_page=20`

---

## 🛒 Cart

### 1. دریافت سبد خرید
**GET** `/cart?price_type=cash`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `price_type` (optional): 'cash' یا 'check'

**Response:**
```json
{
  "success": true,
  "data": {
    "cash_cart": {
      "items": [...],
      "total": 1000000,
      "item_count": 5
    },
    "check_cart": {
      "items": [...],
      "total": 950000,
      "item_count": 3
    },
    "grand_total": 1950000,
    "total_items": 8
  }
}
```

---

### 2. افزودن به سبد خرید
**POST** `/cart`

**Request Body:**
```json
{
  "product_id": 123,
  "quantity": 2,
  "price_type": "cash",
  "price_plan": "isaco_cash"
}
```

---

### 3. تغییر تعداد محصول
**PUT** `/cart/{cart_item_id}`

**Request Body:**
```json
{
  "quantity": 5
}
```

---

### 4. حذف از سبد خرید
**DELETE** `/cart/{cart_item_id}`

---

## 📝 Orders

### 1. لیست سفارشات
**GET** `/orders?page=1&per_page=10&status=pending`

**Headers:**
```
Authorization: Bearer {access_token}
```

---

### 2. ایجاد سفارش
**POST** `/orders`

**Request Body:**
```json
{
  "payment_type": "cash",
  "customer_notes": "لطفاً زودتر ارسال کنید"
}
```

**Response:**
```json
{
  "success": true,
  "message": "سفارش با موفقیت ایجاد شد",
  "data": {
    "order": {
      "id": 1,
      "invoice_number": "INV-20250127-ABC123",
      "total_amount": 1500000,
      "payment_type": "cash",
      "status": "pending",
      "items": [...],
      "created_at": "2025-01-27T10:30:00"
    }
  }
}
```

---

### 3. جزئیات سفارش
**GET** `/orders/{order_id}`

---

## 👤 User Profile

### 1. دریافت پروفایل
**GET** `/user/profile`

**Headers:**
```
Authorization: Bearer {access_token}
```

---

### 2. به‌روزرسانی پروفایل
**PUT** `/user/profile`

**Request Body:**
```json
{
  "full_name": "احمد محمدی",
  "email": "ahmad@example.com",
  "address": "تهران، میدان آزادی",
  "company_name": "شرکت نمونه"
}
```

---

### 3. درخواست خریدار عمده
**POST** `/user/bulk-buyer-request`

**Request Body:**
```json
{
  "company_name": "شرکت نمونه",
  "national_id": "1234567890",
  "address": "تهران",
  "landline_phone": "02112345678"
}
```

---

## ⚙️ Config

### 1. تنظیمات اپلیکیشن
**GET** `/config`

---

### 2. بنرها و اطلاعیه‌ها
**GET** `/config/banners`

---

### 3. اطلاعات شرکت
**GET** `/config/company-info`

---

### 4. تنظیمات صفحه ابتدایی
**GET** `/config/splash`

---

### 5. لیست جوایز
**GET** `/rewards`

**Headers (optional):**
```
Authorization: Bearer {access_token}
```

---

## 🔒 Error Responses

همه endpoint ها در صورت خطا، این فرمت را برمی‌گردانند:

```json
{
  "success": false,
  "message": "پیام خطا",
  "code": "ERROR_CODE"
}
```

### کدهای خطای رایج:

- `INVALID_PHONE`: شماره تلفن نامعتبر
- `INVALID_OTP`: کد تایید نامعتبر
- `OTP_EXPIRED`: کد تایید منقضی شده
- `UNAUTHORIZED`: نیاز به احراز هویت
- `PRODUCT_NOT_FOUND`: محصول یافت نشد
- `INSUFFICIENT_STOCK`: موجودی کافی نیست
- `EMPTY_CART`: سبد خرید خالی است
- `SERVER_ERROR`: خطای سرور

---

## 📝 نکات مهم

1. **Authentication**: اکثر endpoint ها نیاز به توکن دارند
2. **Pagination**: همه لیست‌ها از pagination پشتیبانی می‌کنند
3. **Error Handling**: همیشه کد خطا را بررسی کنید
4. **Rate Limiting**: محدودیت درخواست رعایت شود
5. **Caching**: برای بهبود عملکرد از caching استفاده کنید

---

## 🚀 شروع سریع

### نمونه کد (Python):

```python
import requests

BASE_URL = "https://yoursite.com/api/mobile/v1"

# ارسال OTP
response = requests.post(f"{BASE_URL}/auth/send-otp", json={
    "phone": "09123456789"
})
```

---

**آخرین به‌روزرسانی**: اکنون  
**نسخه API**: v1.0  
**وضعیت**: ✅ کامل

