// Enhanced JavaScript for Asia Salman Automotive Parts Website

$(document).ready(function() {
    // Initialize enhanced features
    initializeModernHeader();
    initializeScrollAnimations();
    initializeLiveChat();
    initializeNewsletter();
    initializeCategoryCards();
    initializeBackToTop();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Initialize cart count on page load
    updateCartCount();
    
    // Product checkbox change event
    $('.product-checkbox').on('change', function() {
        updateCartPoints();
    });

    // Cart functionality
    $('.add-to-cart').on('click', function(e) {
        e.preventDefault();
        var button = $(this);
        var productId = button.data('product-id');
        var quantity = parseInt($('#quantity_' + productId).val()) || 1;
        var priceType = $('input[name="price_type_' + productId + '"]:checked').val();
        
        // For individual users (non-bulk buyers), default to cash
        if (!priceType) {
            priceType = 'cash';
        }

        button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> در حال اضافه کردن...');

        $.ajax({
            url: '/add_to_cart',
            method: 'POST',
            data: {
                product_id: productId,
                quantity: quantity,
                price_type: priceType
            },
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    updateCartDisplay();
                } else {
                    showAlert(response.message, 'error');
                }
            },
            error: function() {
                showAlert('خطا در ارتباط با سرور', 'error');
            },
            complete: function() {
                button.prop('disabled', false).html('<i class="fas fa-cart-plus"></i> اضافه به سبد');
            }
        });
    });

    // Update cart quantity
    $('.update-cart-quantity').on('change', function() {
        var cartId = $(this).data('cart-id');
        var quantity = parseInt($(this).val());
        
        // If quantity is 0 or less, remove the item
        if (quantity <= 0) {
            if (confirm('آیا مطمئن هستید که می‌خواهید این کالا را از سبد خرید حذف کنید؟')) {
                $.ajax({
                    url: '/remove_from_cart',
                    method: 'POST',
                    data: {
                        cart_id: cartId
                    },
                    success: function(response) {
                        if (response.success) {
                            showAlert('کالا از سبد خرید حذف شد', 'success');
                            updateCartDisplay();
                        } else {
                            showAlert(response.message, 'error');
                        }
                    },
                    error: function() {
                        showAlert('خطا در ارتباط با سرور', 'error');
                    }
                });
            } else {
                // Reset to 1 if user cancels
                $(this).val(1);
            }
            return;
        }
        
        $.ajax({
            url: '/update_cart',
            method: 'POST',
            data: {
                cart_id: cartId,
                quantity: quantity
            },
            success: function(response) {
                if (response.success) {
                    updateCartDisplay();
                } else {
                    showAlert(response.message, 'error');
                }
            },
            error: function() {
                showAlert('خطا در ارتباط با سرور', 'error');
            }
        });
    });

    // Remove from cart
    $('.remove-from-cart').on('click', function(e) {
        e.preventDefault();
        var cartId = $(this).data('cart-id');
        
        if (confirm('آیا مطمئن هستید که می‌خواهید این کالا را از سبد خرید حذف کنید؟')) {
            $.ajax({
                url: '/remove_from_cart',
                method: 'POST',
                data: {
                    cart_id: cartId
                },
                success: function(response) {
                    if (response.success) {
                        showAlert('کالا از سبد خرید حذف شد', 'success');
                        updateCartDisplay();
                    } else {
                        showAlert(response.message, 'error');
                    }
                },
                error: function() {
                    showAlert('خطا در ارتباط با سرور', 'error');
                }
            });
        }
    });

    // Quantity controls
    $('.quantity-btn').on('click', function() {
        var input = $(this).siblings('input');
        var currentValue = parseInt(input.val()) || 1;
        var change = $(this).data('change');
        var newValue = currentValue + change;
        
        // If this is a cart quantity control, handle auto-removal
        if (input.hasClass('update-cart-quantity')) {
            if (newValue <= 0) {
                // Ask for confirmation before removing
                if (confirm('آیا مطمئن هستید که می‌خواهید این کالا را از سبد خرید حذف کنید؟')) {
                    var cartId = input.data('cart-id');
                    $.ajax({
                        url: '/remove_from_cart',
                        method: 'POST',
                        data: {
                            cart_id: cartId
                        },
                        success: function(response) {
                            if (response.success) {
                                showAlert('کالا از سبد خرید حذف شد', 'success');
                                updateCartDisplay();
                            } else {
                                showAlert(response.message, 'error');
                            }
                        },
                        error: function() {
                            showAlert('خطا در ارتباط با سرور', 'error');
                        }
                    });
                }
                return;
            }
        }
        
        if (newValue >= 1) {
            input.val(newValue);
            // Trigger change event for cart items
            if (input.hasClass('update-cart-quantity')) {
                input.trigger('change');
            }
        }
    });

    // File upload preview
    $('.file-input').on('change', function() {
        var file = this.files[0];
        var preview = $(this).siblings('.file-preview');
        
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                preview.html('<img src="' + e.target.result + '" class="img-thumbnail" style="max-width: 200px;">');
            };
            reader.readAsDataURL(file);
        }
    });

    // Search functionality
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        var searchQuery = $('#search-input').val().trim();
        
        if (searchQuery.length < 2) {
            showAlert('لطفاً حداقل 2 کاراکتر وارد کنید', 'warning');
            return;
        }
        
        // Redirect to shop with search parameters
        window.location.href = '/shop?search=' + encodeURIComponent(searchQuery);
    });

    // Filter functionality
    $('.filter-checkbox').on('change', function() {
        var form = $(this).closest('form');
        form.submit();
    });

    // Invoice document upload
    $('.upload-document').on('click', function(e) {
        e.preventDefault();
        var invoiceId = $(this).data('invoice-id');
        var documentType = $(this).data('document-type');
        
        $('#document-type').val(documentType);
        $('#invoice-id').val(invoiceId);
        $('#document-upload-modal').modal('show');
    });

    // Document upload form submission
    $('#document-upload-form').on('submit', function(e) {
        e.preventDefault();
        
        var formData = new FormData(this);
        
        $.ajax({
            url: '/upload_invoice_document',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    $('#document-upload-modal').modal('hide');
                    location.reload();
                } else {
                    showAlert(response.message, 'error');
                }
            },
            error: function() {
                showAlert('خطا در بارگذاری فایل', 'error');
            }
        });
    });

    // Profile document upload
    $('#profile-document-form').on('submit', function(e) {
        e.preventDefault();
        
        var formData = new FormData(this);
        
        $.ajax({
            url: '/upload_profile_document',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    location.reload();
                } else {
                    showAlert(response.message, 'error');
                }
            },
            error: function() {
                showAlert('خطا در بارگذاری فایل', 'error');
            }
        });
    });

    // Excel import
    $('#excel-import-form').on('submit', function(e) {
        e.preventDefault();
        
        var formData = new FormData(this);
        var submitBtn = $(this).find('button[type="submit"]');
        
        submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> در حال پردازش...');
        
        $.ajax({
            url: '/admin/import_products',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                showAlert('فایل با موفقیت پردازش شد', 'success');
                location.reload();
            },
            error: function() {
                showAlert('خطا در پردازش فایل', 'error');
            },
            complete: function() {
                submitBtn.prop('disabled', false).html('<i class="fas fa-upload"></i> بارگذاری فایل');
            }
        });
    });

    // Enhanced price calculation with animations
    $('.price-type-radio').on('change', function() {
        var $this = $(this);
        var productId = $this.data('product-id');
        var priceType = $this.val();
        var isBulkBuyer = $this.data('bulk-buyer') === 'true';
        
        var $priceElement = $('#price-' + productId);
        var $savingsElement = $priceElement.siblings('.price-savings');
        
        // Get all price data attributes
        var prices = {
            bulkCash: parseFloat($this.data('bulk-cash-price')) || 0,
            bulkCheck: parseFloat($this.data('bulk-check-price')) || 0,
            retailCash: parseFloat($this.data('retail-cash-price')) || 0,
            retailCheck: parseFloat($this.data('retail-check-price')) || 0
        };
        
        var selectedPrice = 0;
        var savings = 0;
        
        // Calculate selected price and savings
        if (isBulkBuyer) {
            selectedPrice = priceType === 'cash' ? prices.bulkCash : prices.bulkCheck;
            var retailPrice = priceType === 'cash' ? prices.retailCash : prices.retailCheck;
            savings = retailPrice - selectedPrice;
        } else {
            selectedPrice = priceType === 'cash' ? prices.retailCash : prices.retailCheck;
        }
        
        // Animate price change
        animatePriceChange($priceElement, selectedPrice);
        
        // Update savings display
        if (isBulkBuyer && savings > 0) {
            $savingsElement.html('<i class="fas fa-tag me-1"></i>صرفه‌جویی: ' + formatPrice(savings) + ' هزار ریال');
        }
        
        // Update cart total
        updateCartTotal();
        
        // Save selection in localStorage
        localStorage.setItem('price_type_' + productId, priceType);
    });

    // Restore previous selections
    $('.price-type-radio').each(function() {
        var productId = $(this).data('product-id');
        var savedType = localStorage.getItem('price_type_' + productId);
        if (savedType) {
            $(this).filter('[value="' + savedType + '"]').prop('checked', true);
        }
    });

    // Initialize price display
    $('.price-type-radio:checked').each(function() {
        $(this).trigger('change');
    });
});

// Enhanced price animation function
function animatePriceChange($element, newPrice) {
    $element.addClass('price-changing');
    
    $element.fadeOut(150, function() {
        var formattedPrice = formatPrice(newPrice);
        $element.text(formattedPrice + ' هزار ریال');
        
        $element.fadeIn(150, function() {
            $element.removeClass('price-changing');
        });
    });
}

// Enhanced price formatting function
function formatPrice(price) {
    // Price is stored in thousands Rials, convert to full Rials for display
    var fullPrice = price * 1000;
    return new Intl.NumberFormat('fa-IR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(fullPrice) + ' ریال';
}

// Enhanced cart total update function
function updateCartTotal() {
    var total = 0;
    $('.cart-item').each(function() {
        var quantity = parseInt($(this).find('.quantity').val()) || 1;
        var price = parseFloat($(this).data('unit-price')) || 0;
        total += quantity * price;
    });
    
    $('.cart-total').text(formatPrice(total) + ' هزار ریال');
}

// Update cart totals dynamically
function updateCartTotals() {
    $.get('/api/cart-totals', function(data) {
        // Update cash total
        if (data.cash_total > 0) {
            $('.cart-total-cash').html(
                '<div class="d-flex justify-content-between align-items-center">' +
                '<span class="d-flex align-items-center">' +
                '<i class="fas fa-money-bill-wave text-success me-2"></i>' +
                'مجموع نقدی:' +
                '</span>' +
                '<span class="fw-bold text-success">' + formatPrice(data.cash_total) + ' هزار ریال</span>' +
                '</div>'
            ).show();
        } else {
            $('.cart-total-cash').hide();
        }
        
        // Update check total
        if (data.check_total > 0) {
            $('.cart-total-check').html(
                '<div class="d-flex justify-content-between align-items-center">' +
                '<span class="d-flex align-items-center">' +
                '<i class="fas fa-file-invoice text-warning me-2"></i>' +
                'مجموع چکی:' +
                '</span>' +
                '<span class="fw-bold text-warning">' + formatPrice(data.check_total) + ' هزار ریال</span>' +
                '</div>'
            ).show();
        } else {
            $('.cart-total-check').hide();
        }
        
        // Update total if both exist
        if (data.cash_total > 0 && data.check_total > 0) {
            $('.cart-total-total').html(
                '<hr class="my-3">' +
                '<div class="d-flex justify-content-between align-items-center">' +
                '<span class="d-flex align-items-center">' +
                '<i class="fas fa-calculator text-danger me-2"></i>' +
                'مجموع کل:' +
                '</span>' +
                '<span class="fw-bold text-danger">' + formatPrice(data.total) + ' هزار ریال</span>' +
                '</div>'
            ).show();
        } else {
            $('.cart-total-total').hide();
        }
    }).fail(function() {
        console.log('Failed to update cart totals');
    });
}

// Utility functions
function showAlert(message, type) {
    var alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
    var alertHtml = '<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                   message +
                   '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                   '</div>';
    
    $('.container').first().prepend(alertHtml);
    
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

function updateCartDisplay() {
    // Update cart totals dynamically
    updateCartTotals();
    
    // Update cart count in navbar
    updateCartCount();
}

function updateCartCount() {
    // Update cart count in navbar
    $.get('/api/cart-count', function(data) {
        if (data.count > 0) {
            $('.cart-count').text(data.count).show();
        } else {
            $('.cart-count').hide();
        }
    });
    
    // Update cart points
    updateCartPoints();
}

function updateCartPoints() {
    // Calculate total points for all products in cart
    var totalPoints = 0;
    
    // Get all selected products
    $('.product-checkbox:checked').each(function() {
        var productId = $(this).data('product-id');
        var quantity = parseInt($('#quantity_' + productId).val()) || 1;
        var priceElement = $('#price_' + productId);
        var price = parseFloat(priceElement.text()) || 0;
        
        // Calculate points for this product
        var totalPrice = price * quantity;
        var basePoints = Math.floor((totalPrice / 100) * 500);
        var bonusPoints = Math.min((quantity - 1) * 50, 1000);
        var productPoints = basePoints + bonusPoints;
        
        totalPoints += productPoints;
    });
    
    // Update cart points display
    $('.cart-points').text(totalPoints.toLocaleString('fa-IR'));
}


function updatePriceDisplay(productId, price, priceElement) {
    // Validate price
    var displayPrice = validatePrice(price);
    
    // Animate price change
    animatePriceChange(priceElement, displayPrice);
}

function validatePrice(price) {
    if (price > 0) {
        return formatPrice(price);
    } else {
        return 'قیمت نامشخص';
    }
}

function animatePriceChange(element, newPrice) {
    // Fade out
    element.addClass('price-fade-out');
    
    setTimeout(function() {
        // Update content
        element.text(newPrice);
        
        // Fade in
        element.removeClass('price-fade-out').addClass('price-fade-in');
        
        // Clean up classes
        setTimeout(function() {
            element.removeClass('price-fade-in');
        }, 300);
    }, 150);
}

function updateCartTotal() {
    // Update cart total when price type changes
    var total = 0;
    $('.cart-item').each(function() {
        var quantity = parseInt($(this).find('.quantity-input').val()) || 0;
        var priceText = $(this).find('.item-price').text();
        var price = parseFloat(priceText.replace(/[^\d]/g, '')); // No conversion needed
        total += quantity * price;
    });
    
    $('.cart-total').text(formatPrice(total));
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('fa-IR', {
        style: 'currency',
        currency: 'IRR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Print functionality
function printInvoice(invoiceId) {
    window.print();
}

// Export functionality
function exportToExcel() {
    // This would implement Excel export functionality
    alert('قابلیت صادرات به اکسل در حال توسعه است');
}

// Enhanced Features

// Scroll Animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.category-card, .trust-card, .testimonial-card, .blog-card').forEach(el => {
        observer.observe(el);
    });
}

// Live Chat Functionality
function initializeLiveChat() {
    window.openChat = function() {
        showNotification('سیستم چت آنلاین به زودی راه‌اندازی خواهد شد', 'info');
    };
}

// Newsletter Signup
function initializeNewsletter() {
    $('.newsletter-signup form').on('submit', function(e) {
        e.preventDefault();
        const email = $(this).find('input[type="email"]').val();
        
        if (email && isValidEmail(email)) {
            const button = $(this).find('button');
            const originalText = button.html();
            button.html('<i class="fas fa-spinner fa-spin"></i>');
            
            setTimeout(() => {
                button.html('<i class="fas fa-check"></i>');
                showNotification('با موفقیت در خبرنامه عضو شدید', 'success');
                $(this)[0].reset();
                
                setTimeout(() => {
                    button.html(originalText);
                }, 2000);
            }, 1000);
        } else {
            showNotification('لطفاً ایمیل معتبر وارد کنید', 'error');
        }
    });
}

// Category Cards Enhancement
function initializeCategoryCards() {
    $('.category-card').hover(
        function() {
            $(this).find('.category-icon').addClass('animate__animated animate__pulse');
        },
        function() {
            $(this).find('.category-icon').removeClass('animate__animated animate__pulse');
        }
    );
}

// Back to Top Button
function initializeBackToTop() {
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            if (!$('.back-to-top').length) {
                $('body').append(`
                    <button class="btn btn-primary back-to-top position-fixed" 
                            style="bottom: 20px; right: 20px; z-index: 999; border-radius: 50%; width: 50px; height: 50px;">
                        <i class="fas fa-arrow-up"></i>
                    </button>
                `);
            }
        } else {
            $('.back-to-top').remove();
        }
    });

    $(document).on('click', '.back-to-top', function() {
        $('html, body').animate({scrollTop: 0}, 800);
    });
}

// Enhanced Notification System
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 'alert-info';
    
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(notification);
    
    setTimeout(() => {
        notification.alert('close');
    }, 5000);
}

// Utility Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Search suggestions
function initSearchSuggestions() {
    $('#search-input').autocomplete({
        source: function(request, response) {
            $.ajax({
                url: '/api/search_suggestions',
                data: {
                    query: request.term
                },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 2
    });
}

// ========================================
// MODERN HEADER FUNCTIONALITY
// ========================================

// Initialize Modern Header Features
function initializeModernHeader() {
    initializeNavbarScroll();
    initializeCartAnimations();
    initializeMobileMenu();
    initializeTopBarInteractions();
}

// Navbar Scroll Effects
function initializeNavbarScroll() {
    const navbar = document.querySelector('.modern-navbar');
    if (!navbar) return;

    let lastScrollTop = 0;
    let ticking = false;

    function updateNavbar() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Hide/show navbar on scroll (optional)
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick, { passive: true });
}


// Cart Animations
function initializeCartAnimations() {
    // Cart button hover effects
    const cartBtn = document.querySelector('.modern-cart-btn');
    if (cartBtn) {
        cartBtn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        cartBtn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    }

    // Cart count animation
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        // Observe cart count changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' || mutation.type === 'characterData') {
                    cartCount.classList.add('bounce');
                    setTimeout(() => {
                        cartCount.classList.remove('bounce');
                    }, 600);
                }
            });
        });
        
        observer.observe(cartCount, {
            childList: true,
            characterData: true,
            subtree: true
        });
    }
}

// Mobile Menu Enhancements
function initializeMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarToggler || !navbarCollapse) return;

    // Animate hamburger icon
    navbarToggler.addEventListener('click', function() {
        this.classList.toggle('active');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
            if (navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        }
    });

    // Close mobile menu when clicking on nav links
    navbarCollapse.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                navbarToggler.click();
            }
        });
    });
}

// Top Bar Interactions
function initializeTopBarInteractions() {
    const topBar = document.querySelector('.top-bar');
    if (!topBar) return;

    // Social links hover effects
    topBar.querySelectorAll('.social-links a').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Hide top bar on scroll (optional)
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            topBar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            topBar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    }, { passive: true });
}

// Enhanced Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed modern-notification" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;">
            <div class="d-flex align-items-center">
                <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
    
    $('body').append(notification);
    
    // Animate in
    notification.hide().slideDown(300);
    
    setTimeout(() => {
        notification.alert('close');
    }, duration);
}

// Get notification icon based on type
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
