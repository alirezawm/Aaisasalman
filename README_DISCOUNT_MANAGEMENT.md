# مستندات سیستم مدیریت تخفیفات

## خلاصه

این مگاپرامپت شامل تمام جزئیات لازم برای پیاده‌سازی سیستم کامل مدیریت تخفیفات در داشبورد مدیریت و نمایش محصولات تخفیف‌دار در صفحه اصلی با اسلایدرهای شبیه دیجی‌کالا است.

## ویژگی‌های اصلی

### 1. داشبورد مدیریت تخفیفات

- **صفحه اصلی مدیریت تخفیفات** (`/admin/discounts`)
  - لیست تمام تخفیفات (روزانه و ماهانه)
  - فیلتر بر اساس نوع و وضعیت
  - جستجو در نام تخفیفات
  - عملیات: مشاهده، ویرایش، حذف، فعال/غیرفعال

- **صفحه جزئیات تخفیف** (`/admin/discounts/<id>`)
  - ویرایش اطلاعات تخفیف
  - جستجو و افزودن محصولات
  - حذف محصولات از تخفیف
  - نمایش لیست محصولات تخفیف‌دار

- **جستجوی محصولات**
  - جستجو بر اساس نام، SKU، OEM، برند، دسته‌بندی
  - نمایش نتایج به صورت grid
  - افزودن چندتایی محصولات

### 2. اسلایدرهای صفحه اصلی

- **اسلایدر تخفیفات روزانه**
  - عنوان: "تخفیفات شگفت‌انگیز روزانه"
  - نمایش محصولات با تخفیف روزانه فعال
  - طراحی شبیه اسلایدر "شگفت‌انگیز" دیجی‌کالا

- **اسلایدر تخفیفات ماهانه**
  - عنوان: "تخفیفات ویژه ماهانه"
  - نمایش محصولات با تخفیف ماهانه فعال
  - طراحی مشابه اسلایدر روزانه

## ساختار فایل JSON

فایل `MEGAPROMPT_DISCOUNT_MANAGEMENT.json` شامل بخش‌های زیر است:

1. **Database Models**: تعریف مدل‌های دیتابیس و فیلدهای مورد نیاز
2. **Admin Dashboard Features**: جزئیات کامل داشبورد مدیریت
3. **Homepage Features**: جزئیات اسلایدرهای صفحه اصلی
4. **API Endpoints**: تمام endpoint های مورد نیاز
5. **Template Snippets**: کدهای HTML آماده
6. **Implementation Steps**: مراحل پیاده‌سازی به ترتیب
7. **Design Guidelines**: راهنمای طراحی و استایل
8. **Security Considerations**: ملاحظات امنیتی
9. **Performance Optimizations**: بهینه‌سازی‌های عملکرد
10. **Testing Checklist**: چک‌لیست تست

## مراحل پیاده‌سازی

1. به‌روزرسانی مدل دیتابیس (افزودن `discount_type` و `priority`)
2. ایجاد migration
3. ایجاد route های admin
4. ایجاد template های admin
5. افزودن منوی تخفیفات به sidebar
6. ایجاد API endpoints
7. افزودن اسلایدرها به صفحه اصلی
8. ایجاد CSS و JavaScript

## API Endpoints

### Admin APIs
- `GET /api/admin/discounts` - لیست تخفیفات
- `GET /api/admin/discounts/<id>` - جزئیات تخفیف
- `POST /api/admin/discounts/create` - ایجاد تخفیف
- `PUT /api/admin/discounts/<id>/update` - ویرایش تخفیف
- `DELETE /api/admin/discounts/<id>/delete` - حذف تخفیف
- `POST /api/admin/discounts/<id>/toggle-status` - تغییر وضعیت
- `GET /api/admin/discounts/search-products` - جستجوی محصولات
- `POST /api/admin/discounts/<id>/add-product` - افزودن محصول
- `DELETE /api/admin/discounts/<id>/remove-product` - حذف محصول

### Public APIs
- `GET /api/discounts/daily-products` - محصولات تخفیف روزانه
- `GET /api/discounts/monthly-products` - محصولات تخفیف ماهانه

## طراحی

### اسلایدرها
- استفاده از Swiper.js
- Navigation arrows (فلش‌های چپ/راست)
- Pagination dots (نقاط پایین)
- Responsive (1 تا 6 محصول در هر view)
- Touch/swipe support

### کارت محصول
- Badge تخفیف (درصد) در گوشه بالا-راست
- تصویر محصول
- نام محصول و برند
- قیمت اصلی (خط‌خورده) و قیمت با تخفیف
- دکمه افزودن به سبد (در hover)

## رنگ‌ها

- Badge تخفیف: `#ef4056` (قرمز دیجی‌کالا)
- قیمت اصلی: `#00bfd6` (آبی دیجی‌کالا)
- قیمت خط‌خورده: `#81858b` (خاکستری)
- متن تخفیف: `#00a049` (سبز)

## نکات مهم

1. قبل از اجرا، migration دیتابیس را اجرا کنید
2. مطمئن شوید Swiper.js به base template اضافه شده
3. تمام API endpoints را تست کنید
4. حالت‌های خالی (بدون تخفیف) را handle کنید
5. Loading states را نمایش دهید

## فایل‌های مورد نیاز

- `models.py` - به‌روزرسانی مدل ProductDiscount
- `routes.py` - افزودن route های جدید
- `templates/admin/discounts.html` - صفحه مدیریت تخفیفات
- `templates/admin/discount_detail.html` - صفحه جزئیات
- `templates/index.html` - افزودن اسلایدرها
- `static/css/discount-sliders.css` - استایل‌های اسلایدر
- `static/js/discount-sliders.js` - منطق اسلایدرها

## استفاده

این مگاپرامپت را می‌توانید به یک AI assistant (مثل ChatGPT، Claude، یا Cursor) بدهید تا تمام کدهای لازم را برای شما تولید کند.

