/**
 * Multi-Select Cart System
 * Advanced cart functionality with multi-select products
 */

class MultiSelectCartSystem {
    constructor() {
        this.selectedProducts = new Set();
        this.cartItems = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCartData();
        this.initializeCartSidebar();
    }

    bindEvents() {
        // Select all functionality
        $(document).on('change', '#selectAll, #selectAllHeader', this.handleSelectAll.bind(this));
        
        // Individual product selection
        $(document).on('change', '.product-checkbox', this.handleProductSelection.bind(this));
        
        // Add selected to cart
        $(document).on('click', '#addSelectedToCart', this.handleAddSelectedToCart.bind(this));
        
        // Cart sidebar events
        $(document).on('click', '.cart-toggle', this.toggleCartSidebar.bind(this));
        $(document).on('click', '.cart-close, .cart-overlay', this.closeCartSidebar.bind(this));
        
        // Cart item management
        $(document).on('click', '.remove-from-cart', this.handleRemoveFromCart.bind(this));
        $(document).on('change', '.cart-quantity', this.handleQuantityChange.bind(this));
        
        // Quantity controls
        $(document).on('click', '.quantity-btn', this.handleQuantityButton.bind(this));
        
        // ISACO price plan selection
        $(document).on('change', 'input[name^="price_plan_"]', this.handlePricePlanChange.bind(this));
        
        // Keyboard shortcuts
        $(document).on('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Checkout button
        $(document).on('click', '.checkout-btn', this.handleCheckout.bind(this));
    }

    handleSelectAll(e) {
        const isChecked = $(e.target).is(':checked');
        $('.product-checkbox').prop('checked', isChecked);
        $('#selectAll, #selectAllHeader').prop('checked', isChecked);
        
        if (isChecked) {
            $('.product-checkbox').each((index, checkbox) => {
                const productId = $(checkbox).data('product-id');
                this.selectedProducts.add(productId);
            });
        } else {
            this.selectedProducts.clear();
        }
        
        this.updateSelectedCount();
    }

    handleProductSelection(e) {
        const checkbox = $(e.target);
        const productId = checkbox.data('product-id');
        
        if (checkbox.is(':checked')) {
            this.selectedProducts.add(productId);
        } else {
            this.selectedProducts.delete(productId);
        }
        
        // Update select all checkboxes
        const totalCheckboxes = $('.product-checkbox').length;
        const checkedCheckboxes = $('.product-checkbox:checked').length;
        
        if (checkedCheckboxes === 0) {
            $('#selectAll, #selectAllHeader').prop('checked', false).prop('indeterminate', false);
        } else if (checkedCheckboxes === totalCheckboxes) {
            $('#selectAll, #selectAllHeader').prop('checked', true).prop('indeterminate', false);
        } else {
            $('#selectAll, #selectAllHeader').prop('checked', false).prop('indeterminate', true);
        }
        
        this.updateSelectedCount();
        this.updateIsacoInstructions();
    }

    updateSelectedCount() {
        const count = this.selectedProducts.size;
        $('.selected-count').text(`${count} محصول انتخاب شده`);
        
        // Check if all selected ISACO products have payment plans selected
        const canAddToCart = this.canAddSelectedToCart();
        const button = $('#addSelectedToCart');
        
        if (count === 0) {
            button.prop('disabled', true);
            button.attr('title', 'ابتدا محصولات را انتخاب کنید');
        } else if (!canAddToCart) {
            button.prop('disabled', true);
            button.attr('title', 'برای محصولات ایساکو گزینه پرداخت را انتخاب کنید');
        } else {
            button.prop('disabled', false);
            button.attr('title', 'افزودن محصولات انتخاب شده به سبد خرید');
        }
    }

    updateIsacoInstructions() {
        const hasSelectedIsacoProducts = Array.from(this.selectedProducts).some(productId => {
            return $(`input[name="price_plan_${productId}"]`).length > 0;
        });
        
        if (hasSelectedIsacoProducts) {
            $('#isacoInstructions').show();
        } else {
            $('#isacoInstructions').hide();
        }
    }

    canAddSelectedToCart() {
        if (this.selectedProducts.size === 0) {
            return false;
        }
        
        // Check if all selected ISACO products have payment plans selected
        for (const productId of this.selectedProducts) {
            const hasIsacoOptions = $(`input[name="price_plan_${productId}"]`).length > 0;
            if (hasIsacoOptions) {
                const selectedPlan = $(`input[name="price_plan_${productId}"]:checked`).val();
                if (!selectedPlan) {
                    return false;
                }
            }
        }
        
        return true;
    }

    validateSelectedProducts() {
        const errors = [];
        
        $('.product-checkbox:checked').each((index, checkbox) => {
            const productId = $(checkbox).data('product-id');
            const row = $(checkbox).closest('tr');
            const productName = row.find('td:nth-child(4) strong').text();
            const productCode = row.find('td:nth-child(5)').text().trim();
            
            // Check if this is an ISACO product (has price_plan radio buttons)
            const hasIsacoOptions = $(`input[name="price_plan_${productId}"]`).length > 0;
            
            if (hasIsacoOptions) {
                const selectedPlan = $(`input[name="price_plan_${productId}"]:checked`).val();
                if (!selectedPlan) {
                    // Highlight the product row to draw attention
                    row.addClass('table-warning');
                    errors.push(`کالا ${productCode}: انتخاب یکی از گزینه‌های ایساکو الزامی است`);
                } else {
                    // Remove highlight if plan is selected
                    row.removeClass('table-warning');
                }
            }
        });
        
        return errors;
    }

    async handleAddSelectedToCart(e) {
        e.preventDefault();
        
        if (this.selectedProducts.size === 0) {
            this.showNotification('لطفاً حداقل یک محصول انتخاب کنید', 'warning');
            return;
        }
        
        // Validate that all selected products have required payment options
        const validationErrors = this.validateSelectedProducts();
        if (validationErrors.length > 0) {
            this.showNotification(validationErrors.join(' '), 'error');
            return;
        }
        
        // Show confirmation modal
        const confirmed = await this.showConfirmationModal();
        if (!confirmed) return;
        
        const products = [];
        
        $('.product-checkbox:checked').each((index, checkbox) => {
            const productId = $(checkbox).data('product-id');
            const quantity = parseInt($(`#quantity_${productId}`).val()) || 1;
            const priceType = $(`input[name="price_type_${productId}"]:checked`).val() || 'cash';
            const pricePlan = $(`input[name="price_plan_${productId}"]:checked`).val() || null;
            
            
            const payload = {
                product_id: productId,
                quantity: quantity,
                price_type: priceType
            };
            if (pricePlan) {
                payload.price_plan = pricePlan;
            }
            products.push(payload);
        });
        
        this.showLoading($('#addSelectedToCart'));
        
        try {
            const response = await fetch('/api/cart/add-multiple', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ products: products })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(result.message, 'success');
                this.clearSelection();
                this.updateCartDisplay();
                this.animateCartIcon();
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Add to cart error:', error);
            this.showNotification('خطا در ارتباط با سرور', 'error');
        } finally {
            this.hideLoading($('#addSelectedToCart'));
        }
    }

    async showConfirmationModal() {
        return new Promise((resolve) => {
            const selectedCount = this.selectedProducts.size;
            const modalHtml = `
                <div class="modal fade" id="confirmAddModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-success text-white">
                                <h5 class="modal-title">
                                    <i class="fas fa-shopping-cart me-2"></i>تأیید افزودن به سبد خرید
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle me-2"></i>
                                    آیا مطمئن هستید که می‌خواهید ${selectedCount} محصول انتخاب شده را به سبد خرید اضافه کنید؟
                                </div>
                                <div class="selected-products-list">
                                    <h6>محصولات انتخاب شده:</h6>
                                    <ul class="list-group list-group-flush">
                                        ${this.getSelectedProductsList()}
                                    </ul>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    <i class="fas fa-times me-1"></i>انصراف
                                </button>
                                <button type="button" class="btn btn-success" id="confirmAddBtn">
                                    <i class="fas fa-check me-1"></i>تأیید و افزودن
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal
            $('#confirmAddModal').remove();
            
            // Add new modal
            $('body').append(modalHtml);
            
            const modal = new bootstrap.Modal(document.getElementById('confirmAddModal'));
            
            // Handle confirm button
            $('#confirmAddBtn').on('click', () => {
                modal.hide();
                resolve(true);
            });
            
            // Handle cancel
            $('#confirmAddModal').on('hidden.bs.modal', () => {
                resolve(false);
            });
            
            modal.show();
        });
    }

    getSelectedProductsList() {
        let html = '';
        $('.product-checkbox:checked').each((index, checkbox) => {
            const productId = $(checkbox).data('product-id');
            const row = $(checkbox).closest('tr');
            const productName = row.find('td:nth-child(4) strong').text();
            const quantity = parseInt($(`#quantity_${productId}`).val()) || 1;
            const pricePlan = $(`input[name="price_plan_${productId}"]:checked`).val() || null;
            const priceType = $(`input[name="price_type_${productId}"]:checked`).length ? $(`input[name="price_type_${productId}"]:checked`).val() : null;
            const priceTypeText = pricePlan ? (
                pricePlan === 'isaco_cash' ? 'ایساکو نقدی' :
                pricePlan === 'isaco_1m' ? 'ایساکو ۱ماهه' :
                pricePlan === 'isaco_2m' ? 'ایساکو ۲ماهه' :
                pricePlan === 'isaco_3m' ? 'ایساکو ۳ماهه' : 'ایساکو'
            ) : (priceType === 'cash' ? 'نقدی' : 'چکی');
            
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${productName}</strong>
                        <br>
                        <small class="text-muted">تعداد: ${quantity} - نوع: ${priceTypeText}</small>
                    </div>
                </li>
            `;
        });
        return html;
    }

    clearSelection() {
        this.selectedProducts.clear();
        $('.product-checkbox').prop('checked', false);
        $('#selectAll, #selectAllHeader').prop('checked', false).prop('indeterminate', false);
        this.updateSelectedCount();
    }

    async loadCartData() {
        try {
            const response = await fetch('/api/cart');
            const result = await response.json();
            
            if (result.success) {
                this.cartItems = result.items;
                this.updateCartDisplay();
            }
        } catch (error) {
            console.error('Load cart data error:', error);
        }
    }

    async updateCartDisplay() {
        await this.updateCartCount();
        await this.updateCartTotals();
        await this.updateCartItems();
    }

    async updateCartCount() {
        try {
            const response = await fetch('/api/cart/count');
            const result = await response.json();
            
            if (result.success) {
                const count = result.count;
                $('.cart-count').text(count).toggle(count > 0);
            }
        } catch (error) {
            console.error('Update cart count error:', error);
        }
    }

    async updateCartTotals() {
        try {
            const response = await fetch('/api/cart/totals');
            const result = await response.json();
            
            if (result.success) {
                this.updateCartTotalsDisplay(result);
            }
        } catch (error) {
            console.error('Update cart totals error:', error);
        }
    }

    updateCartTotalsDisplay(totals) {
        const totalsHtml = `
            <div class="cart-totals-breakdown">
                ${totals.cash_total > 0 ? `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="d-flex align-items-center">
                            <i class="fas fa-money-bill-wave text-success me-2"></i>
                            مجموع نقدی:
                        </span>
                        <span class="fw-bold text-success">${this.formatPrice(totals.cash_total)}</span>
                    </div>
                ` : ''}
                ${totals.check_total > 0 ? `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="d-flex align-items-center">
                            <i class="fas fa-file-invoice text-warning me-2"></i>
                            مجموع چکی:
                        </span>
                        <span class="fw-bold text-warning">${this.formatPrice(totals.check_total)}</span>
                    </div>
                ` : ''}
                ${totals.cash_total > 0 && totals.check_total > 0 ? `
                    <hr class="my-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="d-flex align-items-center">
                            <i class="fas fa-calculator text-danger me-2"></i>
                            مجموع کل:
                        </span>
                        <span class="fw-bold text-danger fs-5">${this.formatPrice(totals.grand_total)}</span>
                    </div>
                ` : ''}
            </div>
        `;
        
        $('.cart-totals-breakdown').html(totalsHtml);
    }

    async updateCartItems() {
        try {
            const response = await fetch('/api/cart');
            const result = await response.json();
            
            if (result.success) {
                this.cartItems = result.items;
                this.renderCartItems();
            }
        } catch (error) {
            console.error('Update cart items error:', error);
        }
    }

    renderCartItems() {
        const container = $('.cart-items');
        
        if (this.cartItems.length === 0) {
            container.html(`
                <div class="text-center text-muted py-4">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <p>سبد خرید خالی است</p>
                </div>
            `);
            return;
        }

        const itemsHtml = this.cartItems.map(item => this.renderCartItem(item)).join('');
        container.html(itemsHtml);
    }

    renderCartItem(item) {
        const isIsaco = item.price_plan && item.price_plan.startsWith('isaco');
        const priceDisplay = this.formatPrice(item.total_price, isIsaco);
        const priceIcon = item.price_type === 'cash' ? 'fa-money-bill-wave text-success' : 'fa-file-invoice text-warning';
        
        return `
            <div class="cart-item" data-cart-id="${item.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${item.product_name}</h6>
                        <small class="text-muted">کد: ${item.product_id}</small>
                        <div class="mt-2">
                            <div class="input-group input-group-sm">
                                <button class="btn btn-outline-danger quantity-btn" type="button" data-change="-1">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <input type="number" class="form-control text-center cart-quantity" 
                                       value="${item.quantity}" min="1" data-cart-id="${item.id}">
                                <button class="btn btn-outline-danger quantity-btn" type="button" data-change="1">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </div>
                        ${item.notes ? `<small class="text-muted d-block mt-1">${item.notes}</small>` : ''}
                    </div>
                    <div class="text-end">
                        <div class="product-price">
                            <i class="fas ${priceIcon} me-1"></i>
                            ${priceDisplay}
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-danger remove-from-cart" 
                                    data-cart-id="${item.id}" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    initializeCartSidebar() {
        // Create cart sidebar if it doesn't exist
        if ($('.cart-sidebar').length === 0) {
            $('body').append(`
                <div class="cart-sidebar">
                    <div class="cart-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                <i class="fas fa-shopping-cart me-2"></i>سبد خرید
                            </h5>
                            <button class="cart-close">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="cart-items">
                        <!-- Cart items will be loaded here -->
                    </div>
                    <div class="cart-totals">
                        <div class="cart-totals-breakdown"></div>
                        <button class="btn btn-danger w-100 checkout-btn">
                            <i class="fas fa-credit-card me-2"></i>تسویه حساب
                        </button>
                    </div>
                </div>
                <div class="cart-overlay"></div>
            `);
        }
    }

    toggleCartSidebar() {
        const sidebar = $('.cart-sidebar');
        const overlay = $('.cart-overlay');
        
        if (sidebar.hasClass('show')) {
            this.closeCartSidebar();
        } else {
            this.openCartSidebar();
        }
    }

    openCartSidebar() {
        const sidebar = $('.cart-sidebar');
        const overlay = $('.cart-overlay');
        
        sidebar.addClass('show');
        overlay.addClass('show');
        $('body').addClass('cart-sidebar-open');
        
        // Load cart data
        this.updateCartItems();
        this.updateCartTotals();
    }

    closeCartSidebar() {
        const sidebar = $('.cart-sidebar');
        const overlay = $('.cart-overlay');
        
        sidebar.removeClass('show');
        overlay.removeClass('show');
        $('body').removeClass('cart-sidebar-open');
    }

    async handleRemoveFromCart(e) {
        e.preventDefault();
        const button = $(e.currentTarget);
        const cartId = button.data('cart-id');

        if (!confirm('آیا مطمئن هستید که می‌خواهید این محصول را حذف کنید؟')) {
            return;
        }

        this.showLoading(button);

        try {
            const response = await fetch('/api/cart/remove', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cart_id: cartId
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.removeCartItem(cartId);
                this.updateCartDisplay();
                this.showNotification(result.message, 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Remove from cart error:', error);
            this.showNotification('خطا در ارتباط با سرور', 'error');
        } finally {
            this.hideLoading(button);
        }
    }

    async handleQuantityChange(e) {
        const input = $(e.currentTarget);
        const cartId = input.data('cart-id');
        const quantity = parseInt(input.val());

        if (quantity <= 0) {
            if (confirm('آیا می‌خواهید این محصول را حذف کنید؟')) {
                await this.handleRemoveFromCart({ currentTarget: input.closest('.cart-item').find('.remove-from-cart') });
            } else {
                input.val(1);
            }
            return;
        }

        try {
            const response = await fetch('/api/cart/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cart_id: cartId,
                    quantity: quantity
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.updateCartDisplay();
            } else {
                this.showNotification(result.message, 'error');
                input.val(input.data('original-value') || 1);
            }
        } catch (error) {
            console.error('Update quantity error:', error);
            this.showNotification('خطا در به‌روزرسانی تعداد', 'error');
            input.val(input.data('original-value') || 1);
        }
    }

    handleQuantityButton(e) {
        const button = $(e.currentTarget);
        const input = button.siblings('input');
        const change = parseInt(button.data('change'));
        const currentValue = parseInt(input.val()) || 1;
        const newValue = Math.max(1, currentValue + change);
        
        input.val(newValue);
        
        // Trigger change event for cart items
        if (input.hasClass('cart-quantity')) {
            input.trigger('change');
        }
    }

    handlePricePlanChange(e) {
        const radio = $(e.currentTarget);
        const productId = radio.attr('name').replace('price_plan_', '');
        const row = $(`input[data-product-id="${productId}"]`).closest('tr');
        
        // Remove warning highlight when a plan is selected
        row.removeClass('table-warning');
        
        // Update button state
        this.updateSelectedCount();
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K to open cart
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.toggleCartSidebar();
        }
        
        // Escape to close cart
        if (e.key === 'Escape') {
            this.closeCartSidebar();
        }
    }

    // Animation methods
    showLoading(button) {
        this.isLoading = true;
        const originalText = button.html();
        button.data('original-text', originalText);
        button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>');
    }

    hideLoading(button) {
        this.isLoading = false;
        const originalText = button.data('original-text');
        button.prop('disabled', false).html(originalText);
    }

    animateCartIcon() {
        const cartIcon = $('.cart-count');
        cartIcon.addClass('animate__animated animate__bounce');
        
        setTimeout(() => {
            cartIcon.removeClass('animate__animated animate__bounce');
        }, 1000);
    }

    removeCartItem(cartId) {
        $(`.cart-item[data-cart-id="${cartId}"]`).fadeOut(300, function() {
            $(this).remove();
        });
    }

    showNotification(message, type = 'info') {
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; max-width: 400px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    }

    // Utility methods
    formatPrice(price, isIsaco = false) {
        if (price === null || price === undefined) {
            return "0 ریال";
        }
        // Price is already in full Rials; display as full Rials
        let priceValue = Math.round(Number(price));
        
        // Add 10% markup for ISACO products (applied on full Rial unit)
        if (isIsaco) {
            priceValue = Math.round(priceValue * 1.10);
        }
        
        return `${priceValue.toLocaleString('fa-IR')} ریال`;
    }

    async handleCheckout(e) {
        e.preventDefault();
        
        // Check if cart is empty
        if (this.cartItems.length === 0) {
            this.showNotification('سبد خرید شما خالی است', 'warning');
            return;
        }

        // Show payment type selection modal
        const paymentType = await this.showPaymentTypeModal();
        if (!paymentType) {
            return;
        }

        const button = $(e.currentTarget);
        this.showLoading(button);

        // Create a form and submit it to handle redirects properly
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/create-invoice';
        form.style.display = 'none';

        const paymentTypeInput = document.createElement('input');
        paymentTypeInput.type = 'hidden';
        paymentTypeInput.name = 'payment_type';
        paymentTypeInput.value = paymentType;

        form.appendChild(paymentTypeInput);
        document.body.appendChild(form);

        // Submit the form - this will handle the redirect automatically
        form.submit();
    }

    showPaymentTypeModal() {
        return new Promise((resolve) => {
            const modalHtml = `
                <div class="modal fade" id="paymentTypeModal" tabindex="-1" aria-labelledby="paymentTypeModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="paymentTypeModalLabel">انتخاب نوع پرداخت</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="radio" name="payment_type" id="payment_cash" value="cash" checked>
                                    <label class="form-check-label" for="payment_cash">
                                        <i class="fas fa-money-bill-wave text-success me-2"></i>
                                        پرداخت نقدی (کارت به کارت)
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="payment_type" id="payment_check" value="check">
                                    <label class="form-check-label" for="payment_check">
                                        <i class="fas fa-file-invoice text-warning me-2"></i>
                                        پرداخت چکی
                                    </label>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">انصراف</button>
                                <button type="button" class="btn btn-danger" id="confirmPaymentType">
                                    <i class="fas fa-credit-card me-2"></i>تایید و ادامه
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal if any
            $('#paymentTypeModal').remove();
            
            // Add modal to body
            $('body').append(modalHtml);
            
            const modal = new bootstrap.Modal(document.getElementById('paymentTypeModal'));
            
            // Handle confirm button
            $('#confirmPaymentType').on('click', () => {
                const selectedPaymentType = $('input[name="payment_type"]:checked').val();
                modal.hide();
                resolve(selectedPaymentType);
            });
            
            // Handle cancel
            $('#paymentTypeModal').on('hidden.bs.modal', () => {
                resolve(null);
            });
            
            modal.show();
        });
    }
}

// Initialize cart system when DOM is ready
$(document).ready(function() {
    console.log('DOM ready, initializing multi-select cart system');
    window.multiSelectCartSystem = new MultiSelectCartSystem();
    console.log('Multi-select cart system initialized:', window.multiSelectCartSystem);
});

// Export for global access
window.MultiSelectCartSystem = MultiSelectCartSystem;
