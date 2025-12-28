# مگاپرامپت حرفه‌ای: طراحی هدر و فوتر مدرن (Dark Theme)

## 📋 خلاصه پروژه
ایجاد هدر و فوتر با تم تاریک (Dark Theme) مشابه تصاویر مرجع با طراحی مینیمال و مدرن.

---

## 🎨 مشخصات طراحی هدر (Header/Navigation Bar)

### ساختار کلی
- **پس‌زمینه**: شیشه‌ای (Glassmorphism) - نیمه‌شفاف با Blur
  - `background: rgba(26, 26, 26, 0.7)` یا `rgba(45, 45, 45, 0.8)`
  - `backdrop-filter: blur(20px) saturate(180%)`
  - `-webkit-backdrop-filter: blur(20px) saturate(180%)`
- **Border**: نازک و نیمه‌شفاف
  - `border-bottom: 1px solid rgba(255, 255, 255, 0.1)`
- **متن**: سفید (#FFFFFF)
- **ارتفاع**: 60-70px
- **موقعیت**: **Fixed** (ثابت) در بالای صفحه - همیشه قابل مشاهده
- **Z-index**: 1000
- **Padding**: 20px افقی، 15px عمودی
- **Box Shadow**: سایه ملایم برای عمق
  - `box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37)`

### المان‌های هدر

#### 1. لوگو/برند (سمت راست - RTL)
- **متن**: "آسیا سلمان™" یا نام برند
- **فونت**: Bold, Sans-serif (Vazir یا IRANSans)
- **اندازه**: 1.5rem - 1.8rem
- **رنگ**: سفید (#FFFFFF)
- **پس‌زمینه**: کمی روشن‌تر از هدر (#3a3a3a) - حالت Active/Hover
- **TM Symbol**: کوچک‌تر، superscript
- **قابلیت کلیک**: لینک به صفحه اصلی

#### 2. منوی ناوبری (Navigation Menu)
- **آیتم‌ها**: خانه، محصولات، درباره ما، خدمات، تماس با ما
- **فاصله بین آیتم‌ها**: 30-40px
- **فونت**: Medium weight, 1rem
- **Hover Effect**: 
  - تغییر رنگ به #FF6B9D (صورتی روشن)
  - Transition: 0.3s ease
- **Active State**: رنگ صورتی روشن (#FF6B9D)

#### 3. دکمه منوی بیشتر (Ellipsis)
- **موقعیت**: سمت چپ (RTL)
- **نماد**: سه نقطه افقی (...)
- **اندازه**: 24px × 24px
- **Hover**: تغییر رنگ به صورتی روشن
- **عملکرد**: باز کردن منوی موبایل یا منوی اضافی

#### 4. المان تزئینی (Geometric Shape)
- **نوع**: منشور/شکل هندسی چندوجهی (Prism)
- **رنگ**: صورتی-قرمز درخشان (#FF6B9D تا #FF1744)
- **موقعیت**: گوشه پایین راست، به صورت مورب
- **افکت**: 
  - Glow effect (box-shadow با blur)
  - Translucent (نیمه‌شفاف)
  - Gradient: از صورتی روشن به قرمز تیره
- **انیمیشن**: 
  - چرخش ملایم (rotate)
  - تغییر اندازه (scale)
  - Fade in/out
- **Z-index**: زیر منو (z-index: 999)

---

## 🎨 مشخصات طراحی فوتر (Footer)

### ساختار کلی
- **پس‌زمینه**: شیشه‌ای (Glassmorphism) - نیمه‌شفاف با Blur
  - `background: rgba(10, 10, 10, 0.7)` یا `rgba(26, 26, 26, 0.8)`
  - `backdrop-filter: blur(20px) saturate(180%)`
  - `-webkit-backdrop-filter: blur(20px) saturate(180%)`
- **Border**: نازک و نیمه‌شفاف
  - `border-top: 1px solid rgba(255, 255, 255, 0.1)`
- **متن**: **سفید (#FFFFFF)** - تمام متن‌ها و لینک‌ها
- **Padding**: 60px عمودی، 40px افقی
- **موقعیت**: **Relative** (عادی) - در انتهای محتوا، نه ثابت
- **Layout**: Grid 3 ستونه (در دسکتاپ)
- **Box Shadow**: سایه ملایم برای عمق
  - `box-shadow: 0 -8px 32px 0 rgba(0, 0, 0, 0.37)`

### بخش‌های فوتر

#### 1. بخش "فهرست سایت" (Site Index)
- **عنوان**: "فهرست سایت" (Site index)
- **فونت عنوان**: Bold, 1.2rem
- **لیست لینک‌ها**:
  - خانه
  - محصولات
  - درباره ما
  - خدمات
  - حریم خصوصی
- **استایل لینک‌ها**:
  - رنگ: سفید
  - Hover: صورتی روشن (#FF6B9D)
  - فاصله عمودی: 12px
  - Transition: 0.2s ease

#### 2. بخش "شبکه‌های اجتماعی" (Social)
- **عنوان**: "شبکه‌های اجتماعی" (Social)
- **لیست لینک‌ها**:
  - اینستاگرام
  - فیسبوک
  - لینکدین
  - تلگرام
  - واتساپ
- **استایل مشابه بخش فهرست سایت**

#### 3. بخش "تماس با ما" (Contact Us)
- **باکس تماس**:
  - پس‌زمینه: Dark Gray (#2d2d2d)
  - Border-radius: 8px
  - Padding: 20px
  - **عنوان**: "تماس با ما" (Contact Us)
  - **نقطه سبز**: دایره کوچک سبز (#00FF00) کنار عنوان
- **اطلاعات تماس**:
  - "درباره پروژه‌تان به ما بگویید"
  - "بیایید همکاری کنیم"
  - شماره تلفن: "+98 51 3333 8881" با bullet point (♦)
  - "نوشتن به ما" با bullet point
  - "عضویت در خبرنامه" با bullet point
- **نمایش زمان**:
  - موقعیت: گوشه بالا راست بخش
  - فرمت: "HH:MM:SS (GMT+3:30)" - زمان ایران
  - فونت: Monospace
  - رنگ: سبز روشن (#00FF00)

#### 4. آیکون مرکزی (Central Icon)
- **موقعیت**: مرکز صفحه، کمی بالاتر از خط وسط
- **نوع**: آیکون انتزاعی (Abstract)
- **شکل**: ستاره 4 پر یا هواپیمای کاغذی استیلیزه
- **رنگ**: سفید (#FFFFFF)
- **اندازه**: 40px × 40px
- **Opacity**: 0.3-0.5 (نیمه‌شفاف)

#### 5. برندینگ پایین (Bottom Branding)
- **متن**: "آسیا سلمان" (نام برند)
- **اندازه**: خیلی بزرگ (8rem - 10rem)
- **فونت**: Bold, Sans-serif
- **رنگ**: سفید (#FFFFFF)
- **موقعیت**: پایین فوتر، عرض کامل
- **Opacity**: 0.1-0.2 (خیلی کم رنگ - به عنوان پس‌زمینه)

---

## 💻 پیاده‌سازی فنی

### HTML Structure
```html
<!-- Header -->
<header class="modern-header">
  <nav class="header-nav">
    <a href="/" class="brand-logo">آسیا سلمان™</a>
    <ul class="nav-menu">
      <li><a href="/">خانه</a></li>
      <li><a href="/products">محصولات</a></li>
      <li><a href="/about">درباره ما</a></li>
      <li><a href="/services">خدمات</a></li>
      <li><a href="/contact">تماس</a></li>
    </ul>
    <button class="menu-toggle">...</button>
    <div class="geometric-shape"></div>
  </nav>
</header>

<!-- Footer -->
<footer class="modern-footer">
  <div class="footer-container">
    <div class="footer-section site-index">
      <h3>فهرست سایت</h3>
      <ul>...</ul>
    </div>
    <div class="footer-section social">
      <h3>شبکه‌های اجتماعی</h3>
      <ul>...</ul>
    </div>
    <div class="footer-section contact">
      <div class="contact-box">
        <h3>تماس با ما <span class="green-dot"></span></h3>
        <p>درباره پروژه‌تان به ما بگویید</p>
        <p>بیایید همکاری کنیم</p>
        <p>♦ +98 51 3333 8881</p>
        <p>♦ نوشتن به ما</p>
        <p>♦ عضویت در خبرنامه</p>
        <div class="time-display">14:53:43 (GMT+3:30)</div>
      </div>
    </div>
    <div class="central-icon"></div>
    <div class="bottom-branding">آسیا سلمان</div>
  </div>
</footer>
```

### CSS Styling

#### Header Styles (Glassmorphism)
```css
.modern-header {
  /* Glassmorphism Effect */
  background: rgba(26, 26, 26, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  
  /* Border */
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  /* Fixed Position */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 1000;
  
  /* Styling */
  color: #FFFFFF;
  padding: 15px 20px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  
  /* Smooth transitions */
  transition: all 0.3s ease;
}

/* Optional: Add scroll effect */
.modern-header.scrolled {
  background: rgba(26, 26, 26, 0.85);
  backdrop-filter: blur(25px) saturate(200%);
  -webkit-backdrop-filter: blur(25px) saturate(200%);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
}

.brand-logo {
  /* Glassmorphism for brand logo */
  background: rgba(58, 58, 58, 0.6);
  backdrop-filter: blur(10px) saturate(150%);
  -webkit-backdrop-filter: blur(10px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 1.6rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.2);
}

.brand-logo:hover {
  background: rgba(58, 58, 58, 0.8);
  backdrop-filter: blur(15px) saturate(180%);
  -webkit-backdrop-filter: blur(15px) saturate(180%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.3);
}

.nav-menu a {
  color: #FFFFFF;
  transition: color 0.3s ease;
}

.nav-menu a:hover {
  color: #FF6B9D;
}

.geometric-shape {
  position: absolute;
  bottom: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #FF6B9D, #FF1744);
  opacity: 0.6;
  transform: rotate(45deg);
  filter: blur(20px);
  animation: float 3s ease-in-out infinite;
}
```

#### Footer Styles (Glassmorphism)
```css
.modern-footer {
  /* Glassmorphism Effect */
  background: rgba(10, 10, 10, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  
  /* Border */
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  
  /* Normal Position (Not Fixed) */
  position: relative;
  width: 100%;
  
  /* Styling */
  color: #FFFFFF; /* رنگ متن سفید */
  padding: 60px 40px;
  box-shadow: 0 -8px 32px 0 rgba(0, 0, 0, 0.37);
  
  /* Smooth transitions */
  transition: all 0.3s ease;
}

/* تمام متن‌ها و لینک‌ها سفید */
.modern-footer,
.modern-footer * {
  color: #FFFFFF;
}

.modern-footer a {
  color: #FFFFFF;
  text-decoration: none;
  transition: color 0.3s ease;
}

.modern-footer a:hover {
  color: #FF6B9D; /* تغییر رنگ در Hover */
}

/* Body padding فقط برای هدر Fixed */
body {
  padding-top: 70px; /* فقط برای هدر Fixed */
  /* padding-bottom حذف شده چون فوتر Fixed نیست */
}

.footer-section h3 {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 20px;
}

.contact-box {
  /* Glassmorphism for contact box */
  background: rgba(45, 45, 45, 0.6);
  backdrop-filter: blur(10px) saturate(150%);
  -webkit-backdrop-filter: blur(10px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
  position: relative;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}

.green-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #00FF00;
  border-radius: 50%;
  margin-right: 8px;
}

.time-display {
  position: absolute;
  top: 10px;
  left: 10px;
  font-family: monospace;
  color: #00FF00;
  font-size: 0.9rem;
}

.central-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  opacity: 0.4;
  /* SVG یا Font Icon */
}

.bottom-branding {
  font-size: 8rem;
  font-weight: bold;
  opacity: 0.1;
  text-align: center;
  margin-top: 40px;
}
```

### JavaScript Functionality

#### Time Display
```javascript
function updateTime() {
  const now = new Date();
  const iranTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Tehran"}));
  const hours = String(iranTime.getHours()).padStart(2, '0');
  const minutes = String(iranTime.getMinutes()).padStart(2, '0');
  const seconds = String(iranTime.getSeconds()).padStart(2, '0');
  document.querySelector('.time-display').textContent = 
    `${hours}:${minutes}:${seconds} (GMT+3:30)`;
}
setInterval(updateTime, 1000);
```

#### Geometric Shape Animation
```javascript
// CSS Animation
@keyframes float {
  0%, 100% { transform: rotate(45deg) translateY(0px); }
  50% { transform: rotate(45deg) translateY(-20px); }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 107, 157, 0.5); }
  50% { box-shadow: 0 0 40px rgba(255, 107, 157, 0.8); }
}
```

#### Scroll Effect for Fixed Header
```javascript
// Add scroll effect to header
window.addEventListener('scroll', function() {
  const header = document.querySelector('.modern-header');
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});
```

#### Body Padding for Fixed Footer
```javascript
// Adjust body padding based on footer height
function adjustBodyPadding() {
  const footer = document.querySelector('.modern-footer');
  const footerHeight = footer.offsetHeight;
  document.body.style.paddingBottom = footerHeight + 'px';
}

window.addEventListener('load', adjustBodyPadding);
window.addEventListener('resize', adjustBodyPadding);
```

---

## 🔮 Glassmorphism - راهنمای کامل

### ویژگی‌های Glassmorphism
Glassmorphism (شیشه‌گرایی) یک تکنیک طراحی مدرن است که المان‌ها را شبیه شیشه نیمه‌شفاف می‌کند.

#### CSS Properties مورد نیاز:
```css
/* پایه Glassmorphism */
.glass-effect {
  /* پس‌زمینه نیمه‌شفاف */
  background: rgba(26, 26, 26, 0.7);
  
  /* افکت Blur برای شیشه */
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  
  /* Border نازک و نیمه‌شفاف */
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  /* سایه برای عمق */
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}
```

### سطوح مختلف شفافیت:
- **Light Glass**: `rgba(255, 255, 255, 0.1)` - برای المان‌های روشن
- **Medium Glass**: `rgba(26, 26, 26, 0.7)` - برای هدر/فوتر
- **Heavy Glass**: `rgba(10, 10, 10, 0.9)` - برای المان‌های مهم

### تنظیمات Blur:
- **Subtle**: `blur(10px)` - برای المان‌های کوچک
- **Medium**: `blur(20px)` - برای هدر/فوتر (پیشنهادی)
- **Strong**: `blur(30px)` - برای افکت قوی‌تر

### Fallback برای مرورگرهای قدیمی:
```css
.modern-header {
  /* Fallback برای مرورگرهای قدیمی */
  background: #1a1a1a;
  
  /* Glassmorphism برای مرورگرهای مدرن */
  @supports (backdrop-filter: blur(20px)) {
    background: rgba(26, 26, 26, 0.7);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
  }
}
```

---

## 📌 موقعیت Fixed - نکات مهم

### تنظیمات Body برای Fixed Header:
```css
body {
  /* Padding فقط برای هدر Fixed */
  padding-top: 70px; /* ارتفاع هدر */
  
  /* فوتر Fixed نیست، پس padding-bottom نیاز نیست */
  /* min-height برای اطمینان از نمایش کامل محتوا */
  min-height: 100vh;
}
```

### محاسبه خودکار Padding (فقط برای هدر):
```javascript
// محاسبه و تنظیم خودکار padding فقط برای هدر
function adjustBodyPadding() {
  const header = document.querySelector('.modern-header');
  
  // فقط ارتفاع هدر را محاسبه می‌کنیم
  const headerHeight = header.offsetHeight;
  
  // فقط padding-top تنظیم می‌شود
  document.body.style.paddingTop = headerHeight + 'px';
  
  // فوتر Fixed نیست، پس padding-bottom نیاز نیست
}

// اجرا در لود و تغییر اندازه
window.addEventListener('load', adjustBodyPadding);
window.addEventListener('resize', adjustBodyPadding);
```

### جلوگیری از Overlap:
- استفاده از `z-index` مناسب
- اضافه کردن `padding` به محتوای اصلی
- استفاده از `margin` برای المان‌های داخلی

---

## 📱 Responsive Design

### Mobile (< 768px)
- منوی هدر به صورت Hamburger Menu
- فوتر به صورت تک ستونه
- اندازه فونت‌ها کاهش یابد
- المان هندسی کوچک‌تر یا حذف شود

### Tablet (768px - 1024px)
- فوتر 2 ستونه
- منو به صورت Collapsible

### Desktop (> 1024px)
- فوتر 3 ستونه
- منوی کامل نمایش داده شود

---

## ✅ چک‌لیست پیاده‌سازی

- [ ] ساختار HTML هدر
- [ ] ساختار HTML فوتر
- [ ] **پس‌زمینه شیشه‌ای (Glassmorphism) برای هدر**
- [ ] **پس‌زمینه شیشه‌ای (Glassmorphism) برای فوتر**
- [ ] **موقعیت Fixed برای هدر (ثابت در بالا)**
- [ ] **موقعیت Relative برای فوتر (ثابت نیست - در انتهای محتوا)**
- [ ] **رنگ متن سفید (#FFFFFF) برای تمام المان‌های فوتر**
- [ ] استایل‌های CSS هدر (Dark Theme + Glassmorphism)
- [ ] استایل‌های CSS فوتر (Dark Theme + Glassmorphism)
- [ ] Backdrop-filter و Webkit-backdrop-filter
- [ ] Border نیمه‌شفاف برای هدر و فوتر
- [ ] Box-shadow برای عمق
- [ ] المان هندسی درخشان (Geometric Shape)
- [ ] انیمیشن‌های Hover و Transition
- [ ] نمایش زمان زنده (Live Time)
- [ ] آیکون مرکزی
- [ ] برندینگ پایین (Bottom Branding)
- [ ] **تنظیم Padding-top برای Body (فقط برای هدر Fixed)**
- [ ] **Scroll Effect برای هدر (اختیاری)**
- [ ] **استایل‌دهی رنگ سفید برای تمام متن‌ها و لینک‌های فوتر**
- [ ] Responsive Design
- [ ] تست در مرورگرهای مختلف (خصوصاً Safari برای backdrop-filter)
- [ ] بهینه‌سازی عملکرد (Performance)
- [ ] دسترسی‌پذیری (Accessibility)

---

## 🎯 نکات مهم

1. **Glassmorphism (پس‌زمینه شیشه‌ای)**:
   - استفاده از `backdrop-filter: blur()` برای افکت شیشه
   - `-webkit-backdrop-filter` برای پشتیبانی Safari
   - پس‌زمینه نیمه‌شفاف با `rgba()`
   - Border نازک و نیمه‌شفاف برای لبه شیشه
   - Box-shadow برای عمق و واقع‌گرایی

2. **موقعیت Fixed (ثابت)**:
   - هدر: `position: fixed; top: 0;` - همیشه در بالای صفحه (ثابت)
   - فوتر: `position: relative;` - در انتهای محتوا (ثابت نیست)
   - اضافه کردن `padding-top` به body برای هدر
   - **فوتر Fixed نیست** - نیازی به `padding-bottom` نیست
   - Z-index مناسب برای لایه‌بندی (فقط برای هدر)

3. **رنگ‌ها**: استفاده از پالت رنگی Dark با Accent Color صورتی (#FF6B9D)
4. **تایپوگرافی**: فونت فارسی خوانا (Vazir یا IRANSans)
5. **انیمیشن‌ها**: ملایم و حرفه‌ای (0.3s ease)
6. **دسترسی‌پذیری**: Contrast Ratio مناسب، ARIA labels
7. **عملکرد**: استفاده از CSS transforms برای انیمیشن‌ها (GPU accelerated)
8. **سازگاری**: 
   - Chrome/Edge: پشتیبانی کامل از backdrop-filter
   - Firefox: پشتیبانی از نسخه 103+
   - Safari: نیاز به `-webkit-backdrop-filter`
   - Fallback: پس‌زمینه تیره برای مرورگرهای قدیمی

---

## 📝 دستورالعمل استفاده

1. این مگاپرامپت را به عنوان راهنمای کامل استفاده کنید
2. ابتدا ساختار HTML را ایجاد کنید
3. سپس استایل‌های CSS را اضافه کنید
4. در نهایت JavaScript برای تعاملات اضافه شود
5. تست و بهینه‌سازی انجام دهید

---

**تاریخ ایجاد**: 2024
**نسخه**: 1.2
**آخرین به‌روزرسانی**: فوتر ثابت نیست + رنگ متن سفید
**وضعیت**: آماده برای پیاده‌سازی

---

## 🔄 تغییرات نسخه 1.2

### تغییرات:
- ✅ فوتر از Fixed به Relative تغییر کرد (ثابت نیست)
- ✅ رنگ متن سفید (#FFFFFF) برای تمام المان‌های فوتر
- ✅ حذف padding-bottom از body (فقط padding-top برای هدر)
- ✅ به‌روزرسانی کدهای CSS و JavaScript

---

## 🔄 تغییرات نسخه 1.1

### اضافه شده:
- ✅ پس‌زمینه شیشه‌ای (Glassmorphism) برای هدر
- ✅ پس‌زمینه شیشه‌ای (Glassmorphism) برای فوتر
- ✅ موقعیت Fixed (ثابت) برای هدر
- ✅ موقعیت Relative (عادی) برای فوتر - **ثابت نیست**
- ✅ رنگ متن سفید (#FFFFFF) برای تمام المان‌های فوتر
- ✅ راهنمای کامل Glassmorphism
- ✅ تنظیمات Body Padding فقط برای هدر Fixed
- ✅ Fallback برای مرورگرهای قدیمی
- ✅ پشتیبانی از Safari با `-webkit-backdrop-filter`

