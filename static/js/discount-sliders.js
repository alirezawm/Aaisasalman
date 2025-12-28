// Discount Sliders JavaScript
// Loads and displays daily and monthly discount products

let dailySwiper, monthlySwiper, dailySwiperHero, monthlySwiperHero;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Swiper instances
    initializeSliders();
    
    // Load products
    loadDailyDiscounts();
    loadMonthlyDiscounts();
    loadDailyDiscountsHero();
    loadMonthlyDiscountsHero();
});

function initializeSliders() {
    // Daily Discounts Swiper (main section)
    dailySwiper = new Swiper('.daily-discounts-swiper', {
        slidesPerView: 1,
        spaceBetween: 16,
        navigation: {
            nextEl: '.daily-discounts-swiper .swiper-button-next',
            prevEl: '.daily-discounts-swiper .swiper-button-prev',
        },
        pagination: {
            el: '.daily-discounts-swiper .swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            576: {
                slidesPerView: 2,
                spaceBetween: 16,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 20,
            },
            992: {
                slidesPerView: 4,
                spaceBetween: 20,
            },
            1200: {
                slidesPerView: 5,
                spaceBetween: 24,
            },
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });
    
    // Daily Discounts Swiper (Hero Section)
    dailySwiperHero = new Swiper('.daily-discounts-swiper-hero', {
        slidesPerView: 1,
        spaceBetween: 16,
        navigation: {
            nextEl: '.daily-discounts-swiper-hero .swiper-button-next',
            prevEl: '.daily-discounts-swiper-hero .swiper-button-prev',
        },
        pagination: {
            el: '.daily-discounts-swiper-hero .swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            576: {
                slidesPerView: 2,
                spaceBetween: 16,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 20,
            },
            992: {
                slidesPerView: 4,
                spaceBetween: 20,
            },
            1200: {
                slidesPerView: 5,
                spaceBetween: 24,
            },
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });
    
    // Monthly Discounts Swiper (main section)
    monthlySwiper = new Swiper('.monthly-discounts-swiper', {
        slidesPerView: 1,
        spaceBetween: 16,
        navigation: {
            nextEl: '.monthly-discounts-swiper .swiper-button-next',
            prevEl: '.monthly-discounts-swiper .swiper-button-prev',
        },
        pagination: {
            el: '.monthly-discounts-swiper .swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            576: {
                slidesPerView: 2,
                spaceBetween: 16,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 20,
            },
            992: {
                slidesPerView: 4,
                spaceBetween: 20,
            },
            1200: {
                slidesPerView: 5,
                spaceBetween: 24,
            },
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });
    
    // Monthly Discounts Swiper (Hero Section)
    monthlySwiperHero = new Swiper('.monthly-discounts-swiper-hero', {
        slidesPerView: 1,
        spaceBetween: 16,
        navigation: {
            nextEl: '.monthly-discounts-swiper-hero .swiper-button-next',
            prevEl: '.monthly-discounts-swiper-hero .swiper-button-prev',
        },
        pagination: {
            el: '.monthly-discounts-swiper-hero .swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            576: {
                slidesPerView: 2,
                spaceBetween: 16,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 20,
            },
            992: {
                slidesPerView: 4,
                spaceBetween: 20,
            },
            1200: {
                slidesPerView: 5,
                spaceBetween: 24,
            },
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });
}

function loadDailyDiscounts() {
    const container = document.getElementById('daily-discounts-container');
    if (!container) return;
    
    fetch('/api/discounts/daily-products?limit=20')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.products.length > 0) {
                container.innerHTML = '';
                data.products.forEach(product => {
                    const slide = createProductSlide(product);
                    container.appendChild(slide);
                });
                dailySwiper.update();
            } else {
                container.innerHTML = `
                    <div class="swiper-slide">
                        <div class="empty-discounts">
                            <i class="fas fa-tags"></i>
                            <p>در حال حاضر تخفیف روزانه‌ای موجود نیست</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading daily discounts:', error);
            container.innerHTML = `
                <div class="swiper-slide">
                    <div class="empty-discounts">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>خطا در بارگذاری تخفیفات روزانه</p>
                    </div>
                </div>
            `;
        });
}

function loadDailyDiscountsHero() {
    const container = document.getElementById('daily-discounts-container-hero');
    if (!container) return;
    
    fetch('/api/discounts/daily-products?limit=20')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.products.length > 0) {
                container.innerHTML = '';
                data.products.forEach(product => {
                    const slide = createProductSlide(product, true); // true for hero section
                    container.appendChild(slide);
                });
                if (dailySwiperHero) dailySwiperHero.update();
            } else {
                container.innerHTML = `
                    <div class="swiper-slide">
                        <div class="empty-discounts text-white">
                            <i class="fas fa-tags"></i>
                            <p>در حال حاضر تخفیف روزانه‌ای موجود نیست</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading daily discounts hero:', error);
            container.innerHTML = `
                <div class="swiper-slide">
                    <div class="empty-discounts text-white">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>خطا در بارگذاری تخفیفات روزانه</p>
                    </div>
                </div>
            `;
        });
}

function loadMonthlyDiscountsHero() {
    const container = document.getElementById('monthly-discounts-container-hero');
    if (!container) return;
    
    fetch('/api/discounts/monthly-products?limit=20')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.products.length > 0) {
                container.innerHTML = '';
                data.products.forEach(product => {
                    const slide = createProductSlide(product, true); // true for hero section
                    container.appendChild(slide);
                });
                if (monthlySwiperHero) monthlySwiperHero.update();
            } else {
                container.innerHTML = `
                    <div class="swiper-slide">
                        <div class="empty-discounts text-white">
                            <i class="fas fa-tags"></i>
                            <p>در حال حاضر تخفیف ماهانه‌ای موجود نیست</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading monthly discounts hero:', error);
            container.innerHTML = `
                <div class="swiper-slide">
                    <div class="empty-discounts text-white">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>خطا در بارگذاری تخفیفات ماهانه</p>
                    </div>
                </div>
            `;
        });
}

function loadMonthlyDiscounts() {
    const container = document.getElementById('monthly-discounts-container');
    if (!container) return;
    
    fetch('/api/discounts/monthly-products?limit=20')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.products.length > 0) {
                container.innerHTML = '';
                data.products.forEach(product => {
                    const slide = createProductSlide(product);
                    container.appendChild(slide);
                });
                monthlySwiper.update();
            } else {
                container.innerHTML = `
                    <div class="swiper-slide">
                        <div class="empty-discounts">
                            <i class="fas fa-tags"></i>
                            <p>در حال حاضر تخفیف ماهانه‌ای موجود نیست</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading monthly discounts:', error);
            container.innerHTML = `
                <div class="swiper-slide">
                    <div class="empty-discounts">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>خطا در بارگذاری تخفیفات ماهانه</p>
                    </div>
                </div>
            `;
        });
}

function createProductSlide(product, isHero = false) {
    const slide = document.createElement('div');
    slide.className = 'swiper-slide';
    
    const originalPrice = product.original_price || 0;
    const discountedPrice = product.discounted_price || 0;
    const discountPercentage = product.discount_percentage || 0;
    const discountAmount = product.discount_amount || 0;
    const stockQuantity = product.stock_quantity || 0;
    
    // Format prices
    const formattedOriginalPrice = originalPrice.toLocaleString('fa-IR') + ' ریال';
    const formattedDiscountedPrice = discountedPrice.toLocaleString('fa-IR') + ' ریال';
    const formattedDiscountAmount = discountAmount.toLocaleString('fa-IR') + ' ریال';
    
    const productUrl = `/product/${product.id}`;
    const cardClass = isHero ? 'product-card discount-card discount-card-hero h-100' : 'product-card discount-card h-100';
    const uniqueId = `product-qty-${product.id}-${Date.now()}`;
    
    slide.innerHTML = `
        <div class="${cardClass}">
            <div class="discount-badge">${Math.round(discountPercentage)}%</div>
            <div class="product-info-no-image">
                <a href="${productUrl}" class="text-decoration-none">
                    <h6 class="product-name">${product.name_fa}</h6>
                </a>
                <div class="product-sku">
                    <i class="fas fa-barcode me-1"></i>
                    <strong>کد کالا:</strong> ${product.sku || 'N/A'}
                </div>
                <div class="price-section">
                    <div class="price-type-badge">
                        <i class="fas fa-money-check-alt me-1"></i>
                        قیمت چکی
                    </div>
                    <div class="price-row">
                        <span class="price-label">قیمت اصلی:</span>
                        <span class="original-price">${formattedOriginalPrice}</span>
                    </div>
                    <div class="price-row">
                        <span class="price-label">درصد تخفیف:</span>
                        <span class="discount-percentage">${Math.round(discountPercentage)}%</span>
                    </div>
                    <div class="price-row">
                        <span class="price-label">قیمت بعد از تخفیف:</span>
                        <span class="discounted-price">${formattedDiscountedPrice}</span>
                    </div>
                    ${discountAmount > 0 ? `
                        <div class="price-row">
                            <span class="price-label">مبلغ تخفیف:</span>
                            <span class="discount-amount">${formattedDiscountAmount}</span>
                        </div>
                    ` : ''}
                </div>
                <div class="quantity-section">
                    <label for="${uniqueId}" class="quantity-label">
                        <i class="fas fa-sort-numeric-up me-1"></i>تعداد:
                    </label>
                    <input type="number" 
                           id="${uniqueId}"
                           class="form-control quantity-input" 
                           value="1" 
                           min="1" 
                           max="${stockQuantity > 0 ? stockQuantity : 999}"
                           data-product-id="${product.id}">
                </div>
                <div class="add-to-cart-section">
                    <button class="btn btn-primary w-100 add-to-cart-btn" 
                            data-product-id="${product.id}"
                            data-quantity-input="${uniqueId}"
                            ${stockQuantity <= 0 ? 'disabled' : ''}>
                        <i class="fas fa-shopping-cart me-1"></i>
                        ${stockQuantity > 0 ? 'افزودن به سبد خرید' : 'ناموجود'}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return slide;
}

// Add to cart function with quantity
function addToCartWithQuantity(productId, quantity, priceType = 'cash', btnElement = null) {
    // Disable button and show loading
    const btn = btnElement || document.querySelector(`.add-to-cart-btn[data-product-id="${productId}"]`);
    if (btn) {
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>در حال افزودن...';
        
        // Make API call
        fetch('/add-to-cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity,
                price_type: priceType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                if (typeof showAlert === 'function') {
                    showAlert(data.message || `${quantity} عدد به سبد خرید اضافه شد`, 'success');
                } else {
                    alert(data.message || `${quantity} عدد به سبد خرید اضافه شد`);
                }
                
                // Update cart display if function exists
                if (typeof updateCartDisplay === 'function') {
                    updateCartDisplay();
                }
            } else {
                // Show error message
                if (typeof showAlert === 'function') {
                    showAlert(data.message || 'خطا در افزودن به سبد خرید', 'error');
                } else {
                    alert(data.message || 'خطا در افزودن به سبد خرید');
                }
            }
        })
        .catch(error => {
            console.error('Add to cart error:', error);
            if (typeof showAlert === 'function') {
                showAlert('خطا در ارتباط با سرور', 'error');
            } else {
                alert('خطا در ارتباط با سرور');
            }
        })
        .finally(() => {
            // Re-enable button
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        });
    }
}

// Initialize add to cart buttons after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation for dynamically added buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.add-to-cart-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.add-to-cart-btn');
            
            if (btn.disabled) return;
            
            const productId = btn.getAttribute('data-product-id');
            const quantityInputId = btn.getAttribute('data-quantity-input');
            
            if (productId && quantityInputId) {
                const quantityInput = document.getElementById(quantityInputId);
                const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
                
                if (quantity > 0) {
                    // Use check price type for discount products
                    addToCartWithQuantity(parseInt(productId), quantity, 'check', btn);
                } else {
                    alert('لطفاً تعداد معتبری وارد کنید');
                }
            }
        }
    });
});

