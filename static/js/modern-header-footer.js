/* ========================================
   JavaScript برای هدر و فوتر مدرن - آسیا سلمان
   ======================================== */

(function() {
    'use strict';

    document.documentElement.classList.add('js-enabled');

    // متغیرهای سراسری
    let lastScrollTop = 0;
    let topBarVisible = true;
    let navbarScrolled = false;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ========================================
    // توابع کمکی
    // ========================================

    /**
     * Reveal footer sections on scroll
     */
    function initFooterReveal() {
        const sections = document.querySelectorAll('.footer-section');
        if (!sections.length) return;

        if (prefersReducedMotion || !('IntersectionObserver' in window)) {
            sections.forEach(section => section.classList.add('is-visible'));
            return;
        }

        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        sections.forEach(section => observer.observe(section));
    }

    /**
     * مدیریت Top Bar هنگام اسکرول
     */
    function handleTopBarScroll() {
        const topBar = document.querySelector('.top-bar');
        if (!topBar) return;

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // اسکرول به پایین - مخفی کردن
            if (topBarVisible) {
                topBar.classList.add('hidden');
                topBarVisible = false;
            }
        } else {
            // اسکرول به بالا - نمایش
            if (!topBarVisible) {
                topBar.classList.remove('hidden');
                topBarVisible = true;
            }
        }

        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    }

    /**
     * مدیریت Navbar هنگام اسکرول
     */
    function handleNavbarScroll() {
        const navbar = document.querySelector('.modern-navbar');
        if (!navbar) return;

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > 50) {
            if (!navbarScrolled) {
                navbar.classList.add('scrolled');
                navbarScrolled = true;
            }
        } else {
            if (navbarScrolled) {
                navbar.classList.remove('scrolled');
                navbarScrolled = false;
            }
        }
    }

    /**
     * دکمه بازگشت به بالا - حذف شد
     */
    function initScrollToTop() {
        // دکمه بازگشت به بالا حذف شد
    }

    /**
     * انیمیشن لینک‌های فوتر - حذف شد
     */
    function initFooterAnimations() {
        // انیمیشن‌ها حذف شدند
    }

    /**
     * انیمیشن آیکون‌های اجتماعی - حذف شد
     */
    function initSocialIconsAnimation() {
        // انیمیشن‌ها حذف شدند
    }

    /**
     * انیمیشن دکمه‌های ناوبری - حذف شد
     */
    function initNavLinksAnimation() {
        const navLinks = document.querySelectorAll('.modern-nav-link');
        
        navLinks.forEach(link => {
            // تشخیص لینک فعال
            if (window.location.pathname === link.getAttribute('href') || 
                window.location.pathname.startsWith(link.getAttribute('href') + '/')) {
                link.classList.add('active');
            }
        });
    }

    /**
     * Add staggered reveal for nav items - حذف شد
     */
    function initNavStagger() {
        // انیمیشن‌ها حذف شدند
    }

    /**
     * افکت Ripple برای دکمه‌ها - حذف شد
     */
    function initRippleEffect() {
        // انیمیشن‌ها حذف شدند
    }

    /**
     * مدیریت فرم خبرنامه
     */
    function initNewsletterForm() {
        const newsletterForm = document.querySelector('.newsletter-signup form');
        if (!newsletterForm) return;

        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('.newsletter-input');
            const email = emailInput.value.trim();

            if (!email || !isValidEmail(email)) {
                showNotification('لطفاً یک ایمیل معتبر وارد کنید', 'error');
                return;
            }

            // نمایش لودینگ
            const submitBtn = this.querySelector('button');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            submitBtn.disabled = true;

            // شبیه‌سازی ارسال (در پروژه واقعی باید به سرور ارسال شود)
            setTimeout(() => {
                showNotification('با موفقیت در خبرنامه عضو شدید!', 'success');
                emailInput.value = '';
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 1500);
        });
    }

    /**
     * اعتبارسنجی ایمیل
     */
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * نمایش نوتیفیکیشن
     */
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show notification-toast`;
            notification.style.cssText = `
            position: fixed;
            top: 100px;
            left: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    /**
     * انیمیشن Dropdown Menu - حذف شد
     */
    function initDropdownAnimations() {
        // انیمیشن‌ها حذف شدند
    }

    /**
     * بهینه‌سازی برای موبایل
     */
    function optimizeForMobile() {
        if (window.innerWidth <= 768) {
            // مخفی کردن متن دکمه‌ها در موبایل
            const buttons = document.querySelectorAll('.modern-cart-btn, .modern-wallet-btn, .modern-user-btn');
            buttons.forEach(btn => {
                const spans = btn.querySelectorAll('span:not(.badge)');
                spans.forEach(span => {
                    if (span.textContent.trim() && !span.classList.contains('d-none')) {
                        span.style.display = 'none';
                    }
                });
            });

            // تنظیم فوتر برای موبایل
        }
    }

    /**
     * Lazy Loading برای تصاویر
     */
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback برای مرورگرهای قدیمی
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }

    /**
     * مدیریت منوی موبایل
     */
    function initMobileMenu() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function() {
            });

            // بستن منو هنگام کلیک روی لینک
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    if (window.innerWidth < 992) {
                        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                        if (bsCollapse) {
                            bsCollapse.hide();
                        }
                    }
                });
            });
        }
    }

    /**
     * انیمیشن Badge سبد خرید - حذف شد
     */
    function animateCartBadge() {
        // انیمیشن‌ها حذف شدند
    }

    /**
     * بهینه‌سازی عملکرد
     */
    function throttle(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ========================================
    // مقداردهی اولیه
    // ========================================

    /**
     * مقداردهی اولیه همه توابع
     */
    function init() {
        // رویدادهای اسکرول
        const handleScroll = throttle(() => {
            handleTopBarScroll();
            handleNavbarScroll();
        }, 10);

        window.addEventListener('scroll', handleScroll, { passive: true });

        // مقداردهی اولیه توابع
        initScrollToTop();
        initFooterAnimations();
        initSocialIconsAnimation();
        initNavLinksAnimation();
        initNavStagger();
        initRippleEffect();
        initNewsletterForm();
        initDropdownAnimations();
        initMobileMenu();
        animateCartBadge();
        optimizeForMobile();
        initLazyLoading();
        initFooterReveal();

        // بررسی موقعیت اولیه
        handleNavbarScroll();
    }

    // اجرا پس از لود شدن DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // مدیریت تغییر اندازه پنجره
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            optimizeForMobile();
        }, 250);
    });

    // صادر کردن توابع برای استفاده در جاهای دیگر
    window.ModernHeaderFooter = {
        showNotification: showNotification
    };

})();

/* ========================================
   استایل‌های اضافی برای Ripple Effect
   ======================================== */
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .notification-toast {
    }

    .notification-toast.fade-out {
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(30px);
        }
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
`;
document.head.appendChild(style);

