from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import uuid
import psutil
import time
from models import *
from app import app
import models

# ------- Persian/Arabic text normalization helpers (for robust search) -------
# These helpers are used across endpoints to ensure characters like ی/ي, ک/ك,
# ZWNJ, Arabic digits, and diacritics do not break matching.
ARABIC_DIACRITICS = [
    '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652', '\u0640'
]
PERSIAN_CHAR_MAP = {
    'ي': 'ی', 'ك': 'ک',
    'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
    'ة': 'ه', 'ۀ': 'ه',
    '\u200c': ' ',  # ZWNJ → space
    '٠': '0','١': '1','٢': '2','٣': '3','٤': '4','٥': '5','٦': '6','٧': '7','٨': '8','٩': '9',
    '۰': '0','۱': '1','۲': '2','۳': '3','۴': '4','۵': '5','۶': '6','۷': '7','۸': '8','۹': '9',
}

def normalize_fa_text(text_value: str) -> str:
    """Normalize Persian/Arabic variants on the Python side."""
    import re
    if not text_value:
        return ''
    t = str(text_value)
    for src, dst in PERSIAN_CHAR_MAP.items():
        t = t.replace(src, dst)
    t = re.sub('[' + ''.join(ARABIC_DIACRITICS) + ']', '', t)
    t = re.sub(r'\s+', ' ', t.strip())
    return t

def normalize_sql_expr(col):
    """Build SQL expression that normalizes a column similar to normalize_fa_text."""
    from sqlalchemy import func
    expr = col
    for src, dst in PERSIAN_CHAR_MAP.items():
        expr = func.replace(expr, src, dst)
    for ch in ARABIC_DIACRITICS:
        expr = func.replace(expr, ch, '')
    return expr

# -------- ISACO Warehouse 15 helpers --------
def is_isaco_feature_enabled():
    return app.config.get('ENABLE_ISACO_WH15', False)

def is_isaco_brand(brand_id: int) -> bool:
    return brand_id == app.config.get('ISACO_BRAND_ID')

def isaco_allowed_plans():
    return set(app.config.get('ISACO_ALLOWED_PLANS', []))

def get_isaco_unit_price(product: Product, plan: str) -> float:
    base_price = 0
    if plan == 'isaco_cash':
        base_price = product.isaco_cash or 0
    elif plan == 'isaco_1m':
        base_price = product.isaco_1m or 0
    elif plan == 'isaco_2m':
        base_price = product.isaco_2m or 0
    elif plan == 'isaco_3m':
        base_price = product.isaco_3m or 0
    
    # Apply 10% markup to base price (keep in thousands Rials)
    if base_price > 0:
        return base_price * 1.10  # Apply 10% markup
    return 0

# Define format_price function here to avoid circular import
def format_price(price):
    """Format price for display - prices are stored in thousands Rials"""
    if price is None:
        return "0 هزار ریال"
    # Prices are stored directly in thousands Rials (no conversion needed)
    price_in_thousands = int(price)
    return f"{price_in_thousands:,} هزار ریال"

# ==================== MAIN ROUTES ====================

@app.route('/')
def index():
    """Homepage"""
    # Get featured products
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    
    # Get latest products
    latest_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    
    # Get announcements
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(3).all()
    
    # Get company info
    company_info = CompanyInfo.query.first()
    
    return render_template('index.html', 
                         featured_products=featured_products,
                         latest_products=latest_products,
                         announcements=announcements,
                         company_info=company_info)

@app.route('/about')
def about():
    """About page"""
    company_info = CompanyInfo.query.first()
    return render_template('about.html', company_info=company_info)

@app.route('/shop')
def shop():
    """Shop page with products"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get filter parameters
    brand_id = request.args.get('brand_id', type=int)
    category_id = request.args.get('category_id', type=int)
    vehicle_type_id = request.args.get('vehicle_type_id', type=int)
    search_query = request.args.get('search', '')
    in_stock_only = request.args.get('in_stock_only', type=bool)
    
    # Build query
    query = Product.query.filter_by(is_active=True)

    # Note: ISACO WH15 products are now included in general listings
    # The original filter was hiding almost all products
    
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if vehicle_type_id:
        # Filter by vehicle type through the relationship
        query = query.join(ProductVehicleType).filter(
            ProductVehicleType.vehicle_type_id == vehicle_type_id
        )
    
    if search_query:
        try:
            norm_q = normalize_fa_text(search_query)
            name_norm = normalize_sql_expr(Product.name)
            name_fa_norm = normalize_sql_expr(Product.name_fa)

            query = query.filter(
                models.db.or_(
                    name_norm.contains(norm_q),
                    name_fa_norm.contains(norm_q),
                    Product.sku.contains(norm_q),
                    Product.oem_code.contains(norm_q)
                )
            )
        except Exception as e:
            # Fallback to simple search if normalization fails
            app.logger.error(f"Search normalization failed: {e}")
            query = query.filter(
                models.db.or_(
                    Product.name.contains(search_query),
                    Product.name_fa.contains(search_query),
                    Product.sku.contains(search_query),
                    Product.oem_code.contains(search_query)
                )
            )
    
    if in_stock_only:
        query = query.filter(Product.stock_quantity > 0)
    
    products = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get brands, categories, and vehicle types for filters
    brands = Brand.query.filter_by(is_active=True).all()
    categories = PartCategory.query.filter_by(is_active=True).all()
    vehicle_types = VehicleType.query.all()
    
    # Create current_filters object for template
    current_filters = {
        'search': search_query,
        'brand_id': brand_id,
        'category_id': category_id,
        'vehicle_type_id': vehicle_type_id,
        'in_stock_only': in_stock_only
    }
    
    return render_template('shop.html', 
                          products=products,
                          brands=brands,
                          categories=categories,
                          vehicle_types=vehicle_types,
                          current_filters=current_filters)

@app.route('/brands')
def brands():
    """Brands page"""
    brands = Brand.query.filter_by(is_active=True).all()
    return render_template('brands.html', brands=brands)

@app.route('/brand/<int:brand_id>/models')
def brand_models(brand_id):
    """Vehicle models for a specific brand"""
    brand = Brand.query.get_or_404(brand_id)
    models = VehicleModel.query.filter_by(brand_id=brand_id, is_active=True).all()
    
    # Group models by year range
    models_by_year = {}
    for model in models:
        if model.year_from and model.year_to:
            year_range = f"{model.year_from}-{model.year_to}"
        elif model.year_from:
            year_range = f"{model.year_from}+"
        else:
            year_range = "نامشخص"
        
        if year_range not in models_by_year:
            models_by_year[year_range] = []
        models_by_year[year_range].append(model)
    
    # Sort year ranges
    sorted_models_by_year = {}
    for year_range in sorted(models_by_year.keys(), key=lambda x: x if x != "نامشخص" else "9999"):
        sorted_models_by_year[year_range] = models_by_year[year_range]
    
    return render_template('brand_models.html', brand=brand, models=models, models_by_year=sorted_models_by_year)

@app.route('/brand/<int:brand_id>/products')
def brand_products(brand_id):
    """Products for a specific brand"""
    brand = Brand.query.get_or_404(brand_id)
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    search_query = request.args.get('search', '')
    in_stock_only = request.args.get('in_stock_only', type=bool)
    
    # Build query for products of this brand
    query = Product.query.filter_by(brand_id=brand_id, is_active=True)

    # If ISACO brand, only show ISACO WH15 or items with ISACO prices
    if is_isaco_feature_enabled() and is_isaco_brand(brand_id):
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Product.is_isaco_wh15 == True,
                (Product.isaco_cash.isnot(None)) |
                (Product.isaco_1m.isnot(None)) |
                (Product.isaco_2m.isnot(None)) |
                (Product.isaco_3m.isnot(None))
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search_query:
        try:
            norm_q = normalize_fa_text(search_query)
            name_norm = normalize_sql_expr(Product.name)
            name_fa_norm = normalize_sql_expr(Product.name_fa)

            query = query.filter(
                models.db.or_(
                    name_norm.contains(norm_q),
                    name_fa_norm.contains(norm_q),
                    Product.sku.contains(norm_q),
                    Product.oem_code.contains(norm_q)
                )
            )
        except Exception as e:
            # Fallback to simple search if normalization fails
            app.logger.error(f"Search normalization failed: {e}")
            query = query.filter(
                models.db.or_(
                    Product.name.contains(search_query),
                    Product.name_fa.contains(search_query),
                    Product.sku.contains(search_query),
                    Product.oem_code.contains(search_query)
                )
            )
    
    if in_stock_only:
        query = query.filter(Product.stock_quantity > 0)
    
    products = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get categories that have products for this brand
    categories = models.db.session.query(PartCategory).join(Product).filter(
        Product.brand_id == brand_id,
        Product.is_active == True,
        PartCategory.is_active == True
    ).distinct().all()
    
    # Create current_filters object for template
    current_filters = {
        'search': search_query,
        'category_id': category_id,
        'in_stock_only': in_stock_only
    }
    
    return render_template('brand_products.html', 
                         brand=brand, 
                         products=products,
                         categories=categories,
                         current_filters=current_filters)

@app.route('/model/<int:model_id>/categories')
def model_categories(model_id):
    """Categories for a specific vehicle model"""
    model = VehicleModel.query.get_or_404(model_id)
    # Get categories that have products for this model
    categories = models.db.session.query(PartCategory).join(Product).join(
        ProductVehicleModel
    ).filter(
        ProductVehicleModel.vehicle_model_id == model_id,
        Product.is_active == True,
        PartCategory.is_active == True
    ).distinct().all()
    
    return render_template('model_categories.html', model=model, categories=categories)

@app.route('/category/<int:category_id>/products')
def category_products(category_id):
    """Products in a specific category"""
    category = PartCategory.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    products = Product.query.filter_by(
        category_id=category_id, 
        is_active=True
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('category_products.html', 
                         category=category, 
                         products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    
    # Get related products (same category)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('product_detail.html', 
                         product=product, 
                         related_products=related_products)

@app.route('/bulk-conditions')
def bulk_conditions():
    """Bulk purchase conditions page"""
    company_info = CompanyInfo.query.first()
    return render_template('bulk_conditions.html', company_info=company_info)

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user)
                
                # Use retry mechanism for database operations
                from database_utils import retry_on_database_lock, database_transaction
                
                @retry_on_database_lock(max_retries=3, delay=0.5, backoff=2)
                def update_last_login():
                    with database_transaction(models.db.session):
                        user.last_login = datetime.utcnow()
                
                try:
                    update_last_login()
                except Exception as e:
                    # Log the error but don't fail the login
                    from database_utils import logger
                    logger.error(f"Failed to update last_login: {e}")
                    # Continue with login even if last_login update fails
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('حساب کاربری شما غیرفعال است.', 'error')
        else:
            flash('نام کاربری یا رمز عبور اشتباه است.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        company_name = request.form.get('company_name')
        is_bulk_buyer_request = request.form.get('is_bulk_buyer') == 'on'
        
        # Normalize optional fields
        username = username.strip() if isinstance(username, str) else username
        email = (email.strip() if isinstance(email, str) else None) or None  # store NULL instead of ''
        full_name = full_name.strip() if isinstance(full_name, str) else full_name
        phone = phone.strip() if isinstance(phone, str) else phone
        company_name = company_name.strip() if isinstance(company_name, str) else company_name
        
        # Validation
        if password != confirm_password:
            flash('رمزهای عبور مطابقت ندارند.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('نام کاربری قبلاً استفاده شده است.', 'error')
            return render_template('register.html')
        
        if email and User.query.filter_by(email=email).first():
            flash('ایمیل قبلاً استفاده شده است.', 'error')
            return render_template('register.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            phone=phone,
            company_name=company_name,
            is_bulk_buyer=is_bulk_buyer_request,  # Set based on checkbox
            user_type='bulk_buyer' if is_bulk_buyer_request else 'regular',
            bulk_buyer_approval_status='pending' if is_bulk_buyer_request else 'approved'  # Regular users are auto-approved
        )
        
        models.db.session.add(user)
        models.db.session.commit()
        
        # Send notification to admin if bulk buyer request
        if is_bulk_buyer_request:
            # Find admin user (first admin user)
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                admin_notification = UserNotification(
                    user_id=admin_user.id,
                    notification_type='bulk_buyer_request',
                    title='درخواست خریدار عمده جدید',
                    message=f'کاربر {full_name} ({username}) درخواست خریدار عمده کرده است. لطفاً بررسی کنید.'
                )
                models.db.session.add(admin_notification)
                models.db.session.commit()
            
            flash('ثبت نام با موفقیت انجام شد. درخواست خریدار عمده شما در انتظار تایید مدیریت است.', 'success')
        else:
            flash('ثبت نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('با موفقیت خارج شدید.', 'info')
    return redirect(url_for('index'))

# ==================== USER DASHBOARD ROUTES ====================

# Dashboard route removed - only admin dashboard is available for admins and order managers

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        # Update profile fields
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.email = request.form.get('email', current_user.email)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.company_name = request.form.get('company_name', current_user.company_name)
        current_user.national_id = request.form.get('national_id', current_user.national_id)
        current_user.address = request.form.get('address', current_user.address)
        current_user.landline_phone = request.form.get('landline_phone', current_user.landline_phone)
        current_user.secondary_phone = request.form.get('secondary_phone', current_user.secondary_phone)
        
        # Calculate profile completion
        current_user.calculate_profile_completion()
        
        models.db.session.commit()
        flash('پروفایل با موفقیت به‌روزرسانی شد.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/change-username', methods=['POST'])
@login_required
def change_username():
    """Change user username"""
    new_username = request.form.get('new_username', '').strip()
    
    # Validation
    if not new_username:
        flash('نام کاربری جدید الزامی است.', 'error')
        return redirect(url_for('profile'))
    
    if len(new_username) < 3:
        flash('نام کاربری باید حداقل 3 کاراکتر باشد.', 'error')
        return redirect(url_for('profile'))
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user and existing_user.id != current_user.id:
        flash('این نام کاربری قبلاً استفاده شده است.', 'error')
        return redirect(url_for('profile'))
    
    # Update username
    old_username = current_user.username
    current_user.username = new_username
    models.db.session.commit()
    
    flash(f'نام کاربری از "{old_username}" به "{new_username}" تغییر یافت.', 'success')
    return redirect(url_for('profile'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    if not current_password or not new_password or not confirm_password:
        flash('تمام فیلدها الزامی است.', 'error')
        return redirect(url_for('profile'))
    
    # Verify current password
    if not check_password_hash(current_user.password_hash, current_password):
        flash('رمز عبور فعلی اشتباه است.', 'error')
        return redirect(url_for('profile'))
    
    # Check if new password matches confirmation
    if new_password != confirm_password:
        flash('رمزهای عبور جدید مطابقت ندارند.', 'error')
        return redirect(url_for('profile'))
    
    # Check password strength
    if len(new_password) < 6:
        flash('رمز عبور باید حداقل 6 کاراکتر باشد.', 'error')
        return redirect(url_for('profile'))
    
    # Update password
    current_user.password_hash = generate_password_hash(new_password)
    models.db.session.commit()
    
    flash('رمز عبور با موفقیت تغییر یافت.', 'success')
    return redirect(url_for('profile'))

@app.route('/notifications')
@login_required
def notifications():
    """User notifications page"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    notifications = UserNotification.query.filter_by(user_id=current_user.id).order_by(
        UserNotification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = UserNotification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    notification.mark_as_read()
    models.db.session.commit()
    
    return jsonify({'success': True})

@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    UserNotification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True, 'read_at': datetime.utcnow()})
    
    models.db.session.commit()
    
    return jsonify({'success': True})

# ==================== CART ROUTES ====================

@app.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_amount = sum(item.get_total_price() for item in cart_items)
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         total_amount=total_amount)

@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add product to cart"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    price_type = request.form.get('price_type', 'cash')
    price_plan = request.form.get('price_plan')  # ISACO plan when applicable
    
    product = Product.query.get_or_404(product_id)
    
    # ISACO validation
    if is_isaco_feature_enabled() and getattr(product, 'is_isaco_wh15', False):
        # Check if product has valid Isaco pricing
        has_valid_isaco_pricing = any([
            product.isaco_cash and product.isaco_cash > 0,
            product.isaco_1m and product.isaco_1m > 0,
            product.isaco_2m and product.isaco_2m > 0,
            product.isaco_3m and product.isaco_3m > 0
        ])
        
        if has_valid_isaco_pricing:
            # Product has valid Isaco pricing, require plan selection
            if not price_plan or price_plan not in isaco_allowed_plans():
                flash('لطفاً یکی از گزینه‌های ایساکو را انتخاب کنید (نقدی/یک‌ماهه/دوماهه/سه‌ماهه).', 'danger')
                return redirect(request.referrer or url_for('brand_products', brand_id=app.config.get('ISACO_BRAND_ID')))
            unit_price_candidate = get_isaco_unit_price(product, price_plan)
            if not unit_price_candidate or unit_price_candidate <= 0:
                flash('قیمت انتخاب‌شده برای این کالا معتبر نیست.', 'danger')
                return redirect(request.referrer or url_for('brand_products', brand_id=app.config.get('ISACO_BRAND_ID')))
        else:
            # Product is marked as Isaco but has no valid Isaco pricing, use regular pricing
            if current_user.is_bulk_buyer and current_user.bulk_buyer_approval_status == 'approved':
                unit_price_candidate = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
            else:
                unit_price_candidate = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
            
            if not unit_price_candidate or unit_price_candidate <= 0:
                flash('قیمت انتخاب‌شده برای این کالا معتبر نیست.', 'danger')
                return redirect(request.referrer or url_for('brand_products', brand_id=app.config.get('ISACO_BRAND_ID')))

    # Check if item already exists in cart (include plan)
    existing_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        price_type=price_type,
        price_plan=price_plan
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        # Determine unit price
        if is_isaco_feature_enabled() and getattr(product, 'is_isaco_wh15', False):
            unit_price = get_isaco_unit_price(product, price_plan)
            # Fallback to regular pricing if Isaco prices are not available
            if not unit_price or unit_price <= 0:
                if current_user.is_bulk_buyer and current_user.bulk_buyer_approval_status == 'approved':
                    unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
                else:
                    unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
        else:
            if current_user.is_bulk_buyer and current_user.bulk_buyer_approval_status == 'approved':
                unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
            else:
                unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
        
        cart_item = Cart(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            price_type=price_type,
            price_plan=price_plan,
            unit_price=unit_price
        )
        models.db.session.add(cart_item)
    
    models.db.session.commit()
    flash('محصول به سبد خرید اضافه شد.', 'success')
    
    return redirect(request.referrer or url_for('shop'))

@app.route('/remove-from-cart/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    cart_item = Cart.query.filter_by(
        id=cart_item_id,
        user_id=current_user.id
    ).first_or_404()
    
    models.db.session.delete(cart_item)
    models.db.session.commit()
    
    flash('محصول از سبد خرید حذف شد.', 'info')
    return redirect(url_for('cart'))

@app.route('/update-cart-quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    """Update cart item quantity"""
    cart_item_id = request.form.get('cart_item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    cart_item = Cart.query.filter_by(
        id=cart_item_id,
        user_id=current_user.id
    ).first_or_404()
    
    if quantity > 0:
        cart_item.quantity = quantity
        models.db.session.commit()
        flash('تعداد محصول به‌روزرسانی شد.', 'success')
    else:
        models.db.session.delete(cart_item)
        models.db.session.commit()
        flash('محصول از سبد خرید حذف شد.', 'info')
    
    return redirect(url_for('cart'))

@app.route('/create-invoice', methods=['POST'])
@login_required
def create_invoice():
    """Create invoice from cart items"""
    payment_type = request.form.get('payment_type', 'cash')
    
    # Get cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('سبد خرید شما خالی است.', 'error')
        return redirect(url_for('cart'))
    
    # Generate invoice number
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate total amount
    total_amount = sum(item.get_total_price() for item in cart_items)
    
    # Create invoice
    invoice = Invoice(
        invoice_number=invoice_number,
        user_id=current_user.id,
        total_amount=total_amount,
        payment_type=payment_type,
        status='pending'
    )
    
    models.db.session.add(invoice)
    models.db.session.flush()  # Get the invoice ID
    
    # Create invoice items
    for cart_item in cart_items:
        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.get_total_price(),
            price_type=cart_item.price_type
        )
        models.db.session.add(invoice_item)
    
    # Clear cart
    Cart.query.filter_by(user_id=current_user.id).delete()
    
    models.db.session.commit()
    
    # اعطای امتیاز برای فاکتور
    try:
        from points_service import PointsService
        points_service = PointsService()
        points_result = points_service.award_points_for_invoice(invoice.id)
        if points_result['success']:
            flash(f'فاکتور با موفقیت ایجاد شد. {points_result["points"]["total_points"]} امتیاز اعطا شد.', 'success')
        else:
            flash('فاکتور با موفقیت ایجاد شد.', 'success')
    except Exception as e:
        flash('فاکتور با موفقیت ایجاد شد.', 'success')
    
    return redirect(url_for('invoice_detail', invoice_id=invoice.id))

# ==================== INVOICE ROUTES ====================

@app.route('/invoices')
@login_required
def invoices():
    """User invoices list"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(
        Invoice.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('invoices.html', invoices=invoices)

@app.route('/invoice/<int:invoice_id>')
@login_required
def invoice_detail(invoice_id):
    """Invoice detail page"""
    invoice = Invoice.query.filter_by(
        id=invoice_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('invoice_detail.html', invoice=invoice)

@app.route('/invoice/<int:invoice_id>/print')
@login_required
def invoice_print(invoice_id):
    """Print invoice"""
    invoice = Invoice.query.filter_by(
        id=invoice_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('invoice_print.html', invoice=invoice)

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard - only for admins and order managers"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    # Get statistics
    total_users = User.query.count()
    total_products = Product.query.count()
    total_invoices = Invoice.query.count()
    total_brands = Brand.query.count()
    
    # Create stats object for template
    stats = {
        'total_users': total_users,
        'total_products': total_products,
        'total_invoices': total_invoices,
        'total_brands': total_brands
    }
    
    # Get recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_invoices=recent_invoices)

@app.route('/admin/products')
@login_required
def admin_products():
    """Admin products management"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    products = Product.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get brands for the add product form
    brands = Brand.query.filter_by(is_active=True).all()
    
    return render_template('admin/products.html', products=products, brands=brands)

@app.route('/admin/add-product', methods=['POST'])
@login_required
def admin_add_product():
    """Add new product (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        # Get form data
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        brand_id = request.form.get('brand_id', type=int) or None
        stock_quantity = request.form.get('stock_quantity', type=int) or 0
        bulk_price_cash = request.form.get('bulk_price_cash', type=float) or 0
        retail_price_cash = request.form.get('retail_price_cash', type=float) or 0
        bulk_price_check = request.form.get('bulk_price_check', type=float) or 0
        retail_price_check = request.form.get('retail_price_check', type=float) or 0
        settlement_period = request.form.get('settlement_period', type=int) or 0
        credit_amount = request.form.get('credit_amount', type=float) or 0
        cash_discount_percentage = request.form.get('cash_discount_percentage', type=float) or 0
        
        # Validation
        if not code or not name:
            flash('کد کالا و نام کالا الزامی است.', 'error')
            return redirect(url_for('admin_products'))
        
        # Check if code already exists
        if Product.query.filter_by(code=code).first():
            flash('کد کالا قبلاً استفاده شده است.', 'error')
            return redirect(url_for('admin_products'))
        
        # Create new product
        product = Product(
            code=code,
            sku=code,  # Use code as SKU for now
            name=name,
            name_fa=name,  # Use same name for Persian
            description=description,
            description_fa=description,  # Use same description for Persian
            brand_id=brand_id,
            stock_quantity=stock_quantity,
            bulk_price_cash=bulk_price_cash,
            retail_price_cash=retail_price_cash,
            bulk_price_check=bulk_price_check,
            retail_price_check=retail_price_check,
            settlement_period=settlement_period,
            credit_amount=credit_amount,
            cash_discount_percentage=cash_discount_percentage,
            is_active=True
        )
        
        models.db.session.add(product)
        models.db.session.commit()
        
        flash(f'محصول "{name}" با موفقیت اضافه شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در افزودن محصول. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    """Edit product (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            code = request.form.get('code', '').strip()
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            brand_id = request.form.get('brand_id', type=int) or None
            stock_quantity = request.form.get('stock_quantity', type=int) or 0
            bulk_price_cash = request.form.get('bulk_price_cash', type=float) or 0
            retail_price_cash = request.form.get('retail_price_cash', type=float) or 0
            bulk_price_check = request.form.get('bulk_price_check', type=float) or 0
            retail_price_check = request.form.get('retail_price_check', type=float) or 0
            settlement_period = request.form.get('settlement_period', type=int) or 0
            credit_amount = request.form.get('credit_amount', type=float) or 0
            cash_discount_percentage = request.form.get('cash_discount_percentage', type=float) or 0
            is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not code or not name:
                flash('کد کالا و نام کالا الزامی است.', 'error')
                return redirect(url_for('admin_edit_product', product_id=product_id))
            
            # Check if code already exists (excluding current product)
            existing_product = Product.query.filter(Product.code == code, Product.id != product_id).first()
            if existing_product:
                flash('کد کالا قبلاً استفاده شده است.', 'error')
                return redirect(url_for('admin_edit_product', product_id=product_id))
            
            # Update product
            product.code = code
            product.sku = code  # Use code as SKU
            product.name = name
            product.name_fa = name  # Use same name for Persian
            product.description = description
            product.description_fa = description  # Use same description for Persian
            product.brand_id = brand_id
            product.stock_quantity = stock_quantity
            product.bulk_price_cash = bulk_price_cash
            product.retail_price_cash = retail_price_cash
            product.bulk_price_check = bulk_price_check
            product.retail_price_check = retail_price_check
            product.settlement_period = settlement_period
            product.credit_amount = credit_amount
            product.cash_discount_percentage = cash_discount_percentage
            product.is_active = is_active
            
            models.db.session.commit()
            
            flash(f'محصول "{name}" با موفقیت به‌روزرسانی شد.', 'success')
            return redirect(url_for('admin_products'))
            
        except Exception as e:
            models.db.session.rollback()
            flash('خطا در به‌روزرسانی محصول. لطفاً دوباره تلاش کنید.', 'error')
    
    # Get brands for the edit form
    brands = Brand.query.filter_by(is_active=True).all()
    
    return render_template('admin/edit_product.html', product=product, brands=brands)

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    """Delete product (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    
    try:
        # Check if product has associated cart items or invoice items
        cart_items = Cart.query.filter_by(product_id=product_id).count()
        invoice_items = InvoiceItem.query.filter_by(product_id=product_id).count()
        
        if cart_items > 0 or invoice_items > 0:
            flash(f'نمی‌توان محصول "{product_name}" را حذف کرد زیرا در سبد خرید یا فاکتورها استفاده شده است.', 'error')
            return redirect(url_for('admin_products'))
        
        # Delete the product
        models.db.session.delete(product)
        models.db.session.commit()
        
        flash(f'محصول "{product_name}" با موفقیت حذف شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در حذف محصول. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_products'))


@app.route('/admin/export-products-excel')
@login_required
def admin_export_products_excel():
    """Export products to Excel (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        # This is a placeholder for Excel export logic
        # You can implement the actual Excel export using openpyxl or xlsxwriter
        flash('صادرات اکسل در حال توسعه است.', 'info')
    except Exception as e:
        flash('خطا در صادرات اکسل. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/brands')
@login_required
def admin_brands():
    """Admin brands management"""
    if not current_user.is_admin:
        abort(403)
    
    brands = Brand.query.all()
    return render_template('admin/brands.html', brands=brands)

@app.route('/admin/add-brand', methods=['POST'])
@login_required
def admin_add_brand():
    """Add new brand (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        name_fa = request.form.get('name_fa', '').strip()
        
        # Validation
        if not name:
            flash('نام برند الزامی است.', 'error')
            return redirect(url_for('admin_brands'))
        
        # Use name as name_fa if not provided
        if not name_fa:
            name_fa = name
        
        # Check if brand already exists
        if Brand.query.filter_by(name=name).first():
            flash('این برند قبلاً وجود دارد.', 'error')
            return redirect(url_for('admin_brands'))
        
        # Create new brand
        brand = Brand(
            name=name,
            name_fa=name_fa,
            is_active=True
        )
        
        models.db.session.add(brand)
        models.db.session.commit()
        
        flash(f'برند "{name}" با موفقیت اضافه شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در افزودن برند. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_brands'))

@app.route('/admin/delete-brand/<int:brand_id>', methods=['POST'])
@login_required
def admin_delete_brand(brand_id):
    """Delete brand (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        brand = Brand.query.get_or_404(brand_id)
        brand_name = brand.name
        
        # Check if brand has associated products
        if brand.products:
            flash(f'نمی‌توان برند "{brand_name}" را حذف کرد زیرا دارای محصولات مرتبط است.', 'error')
            return redirect(url_for('admin_brands'))
        
        # Delete the brand
        models.db.session.delete(brand)
        models.db.session.commit()
        
        flash(f'برند "{brand_name}" با موفقیت حذف شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در حذف برند. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_brands'))

@app.route('/admin/add-vehicle-type', methods=['POST'])
@login_required
def admin_add_vehicle_type():
    """Add new vehicle type (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        
        # Validation
        if not name:
            flash('نام نوع خودرو الزامی است.', 'error')
            return redirect(url_for('admin_vehicle_types'))
        
        # Check if vehicle type already exists
        if VehicleType.query.filter_by(name=name).first():
            flash('این نوع خودرو قبلاً وجود دارد.', 'error')
            return redirect(url_for('admin_vehicle_types'))
        
        # Create new vehicle type
        vehicle_type = VehicleType(name=name)
        
        models.db.session.add(vehicle_type)
        models.db.session.commit()
        
        flash(f'نوع خودرو "{name}" با موفقیت اضافه شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در افزودن نوع خودرو. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_vehicle_types'))

@app.route('/admin/delete-vehicle-type/<int:vehicle_type_id>', methods=['POST'])
@login_required
def admin_delete_vehicle_type(vehicle_type_id):
    """Delete vehicle type (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        vehicle_type = VehicleType.query.get_or_404(vehicle_type_id)
        vehicle_type_name = vehicle_type.name
        
        # Check if vehicle type has associated products
        if vehicle_type.products:
            flash(f'نمی‌توان نوع خودرو "{vehicle_type_name}" را حذف کرد زیرا دارای محصولات مرتبط است.', 'error')
            return redirect(url_for('admin_vehicle_types'))
        
        # Delete the vehicle type
        models.db.session.delete(vehicle_type)
        models.db.session.commit()
        
        flash(f'نوع خودرو "{vehicle_type_name}" با موفقیت حذف شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در حذف نوع خودرو. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_vehicle_types'))

@app.route('/admin/add-announcement', methods=['POST'])
@login_required
def admin_add_announcement():
    """Add new announcement (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        # Get form data
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not title or not content:
            flash('عنوان و محتوا الزامی است.', 'error')
            return redirect(url_for('admin_announcements'))
        
        # Create new announcement
        announcement = Announcement(
            title=title,
            content=content,
            is_active=is_active
        )
        
        models.db.session.add(announcement)
        models.db.session.commit()
        
        flash(f'اطلاعیه "{title}" با موفقیت اضافه شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در افزودن اطلاعیه. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_announcements'))

@app.route('/admin/update-company-info', methods=['POST'])
@login_required
def admin_update_company_info():
    """Update company info (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        # Get form data
        company_name = request.form.get('company_name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        description = request.form.get('description', '').strip()
        
        # Get or create company info
        company_info = CompanyInfo.query.first()
        if not company_info:
            company_info = CompanyInfo()
            models.db.session.add(company_info)
        
        # Update fields
        company_info.company_name = company_name
        company_info.address = address
        company_info.phone = phone
        company_info.email = email
        company_info.description = description
        
        models.db.session.commit()
        
        flash('اطلاعات شرکت با موفقیت به‌روزرسانی شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در به‌روزرسانی اطلاعات شرکت. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_company_info'))

@app.route('/admin/invoices/management')
@login_required
def admin_invoice_management():
    """صفحه اصلی مدیریت فاکتورهای مشتریان"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    approval_status = request.args.get('approval_status', '')
    payment_type = request.args.get('payment_type', '')
    user_search = request.args.get('user_search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    amount_min = request.args.get('amount_min', type=float)
    amount_max = request.args.get('amount_max', type=float)
    
    # Build query - specify join condition to avoid ambiguous foreign key error
    query = Invoice.query.join(User, Invoice.user_id == User.id)
    
    if approval_status:
        query = query.filter_by(approval_status=approval_status)
    
    if payment_type:
        query = query.filter_by(payment_type=payment_type)
    
    if user_search:
        query = query.filter(
            models.db.or_(
                User.username.contains(user_search),
                User.full_name.contains(user_search),
                User.company_name.contains(user_search)
            )
        )
    
    if date_from:
        query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    if date_to:
        query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    if amount_min:
        query = query.filter(Invoice.total_amount >= amount_min * 1000)  # Convert to full rials
    
    if amount_max:
        query = query.filter(Invoice.total_amount <= amount_max * 1000)  # Convert to full rials
    
    # Get statistics
    all_invoices = Invoice.query.all()
    stats = {
        'total_invoices': len(all_invoices),
        'pending_approval': len([i for i in all_invoices if i.approval_status == 'pending']),
        'approved': len([i for i in all_invoices if i.approval_status == 'approved']),
        'rejected': len([i for i in all_invoices if i.approval_status == 'rejected']),
        'under_review': len([i for i in all_invoices if i.approval_status == 'under_review']),
        'total_amount': sum(i.total_amount for i in all_invoices) / 1000000  # Convert to millions
    }
    
    # Paginate results
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Current filters for template
    current_filters = {
        'approval_status': approval_status,
        'payment_type': payment_type,
        'user_search': user_search,
        'date_from': date_from,
        'date_to': date_to,
        'amount_min': amount_min,
        'amount_max': amount_max
    }
    
    return render_template('admin/invoice_management.html',
                         invoices=invoices,
                         stats=stats,
                         current_filters=current_filters)

@app.route('/admin/invoices')
@login_required
def admin_invoices():
    """View all customer invoices (order managers only)."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    approval_status = request.args.get('approval_status', '')
    payment_type = request.args.get('payment_type', '')
    user_search = request.args.get('user_search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = Invoice.query
    
    if approval_status:
        query = query.filter_by(approval_status=approval_status)
    
    if payment_type:
        query = query.filter_by(payment_type=payment_type)
    
    if user_search:
        query = query.join(User, Invoice.user_id == User.id).filter(
            models.db.or_(
                User.username.contains(user_search),
                User.full_name.contains(user_search),
                User.company_name.contains(user_search)
            )
        )
    
    if date_from:
        query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    if date_to:
        query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Get all invoices for statistics (before filtering)
    all_invoices = Invoice.query.all()
    
    # Calculate statistics
    total_invoices = len(all_invoices)
    pending_approval = len([inv for inv in all_invoices if inv.approval_status == 'pending'])
    approved = len([inv for inv in all_invoices if inv.approval_status == 'approved'])
    rejected = len([inv for inv in all_invoices if inv.approval_status == 'rejected'])
    under_review = len([inv for inv in all_invoices if inv.approval_status == 'under_review'])
    
    # Create stats object for template
    stats = {
        'total_invoices': total_invoices,
        'pending_approval': pending_approval,
        'approved': approved,
        'rejected': rejected,
        'under_review': under_review
    }
    
    # Create current_filters object for template
    current_filters = {
        'approval_status': approval_status,
        'payment_type': payment_type,
        'user_search': user_search,
        'date_from': date_from,
        'date_to': date_to
    }
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/invoices.html', invoices=invoices, stats=stats, current_filters=current_filters)

@app.route('/admin/invoice/<int:invoice_id>')
@login_required
def admin_invoice_detail(invoice_id):
    """View invoice details (order managers only)."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('admin/invoice_detail.html', invoice=invoice)

# ==================== CUSTOMER INVOICES IN PROFILE ====================

@app.route('/profile/customer-invoices')
@login_required
def profile_customer_invoices():
    """Display customer invoices in profile for order managers."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    # Get filter parameters
    approval_status = request.args.get('approval_status', '')
    payment_type = request.args.get('payment_type', '')
    user_search = request.args.get('user_search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = Invoice.query
    
    if approval_status:
        query = query.filter_by(approval_status=approval_status)
    
    if payment_type:
        query = query.filter_by(payment_type=payment_type)
    
    if user_search:
        query = query.join(User, Invoice.user_id == User.id).filter(
            models.db.or_(
                User.username.contains(user_search),
                User.full_name.contains(user_search),
                User.company_name.contains(user_search)
            )
        )
    
    if date_from:
        try:
            query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass
    
    if date_to:
        try:
            query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
        except ValueError:
            pass
    
    # Get all invoices for statistics (before filtering)
    all_invoices = Invoice.query.all()
    
    # Calculate statistics
    total_invoices = len(all_invoices)
    pending_approval = len([inv for inv in all_invoices if inv.approval_status == 'pending'])
    approved = len([inv for inv in all_invoices if inv.approval_status == 'approved'])
    rejected = len([inv for inv in all_invoices if inv.approval_status == 'rejected'])
    under_review = len([inv for inv in all_invoices if inv.approval_status == 'under_review'])
    
    # Calculate total amounts
    total_pending_amount = sum([inv.total_amount for inv in all_invoices if inv.approval_status == 'pending'])
    total_approved_amount = sum([inv.total_amount for inv in all_invoices if inv.approval_status == 'approved'])
    
    # Create stats object for template
    stats = {
        'total_invoices': total_invoices,
        'pending_approval': pending_approval,
        'approved': approved,
        'rejected': rejected,
        'under_review': under_review,
        'total_pending_amount': total_pending_amount,
        'total_approved_amount': total_approved_amount
    }
    
    # Create current_filters object for template
    current_filters = {
        'approval_status': approval_status,
        'payment_type': payment_type,
        'user_search': user_search,
        'date_from': date_from,
        'date_to': date_to
    }
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('profile_customer_invoices.html', 
                         invoices=invoices, 
                         stats=stats, 
                         current_filters=current_filters)

# ==================== CUSTOMER INVOICES API ENDPOINTS ====================

@app.route('/api/profile/customer-invoices')
@login_required
def api_profile_customer_invoices():
    """Get customer invoices data as JSON for order managers."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        return jsonify({'error': 'دسترسی غیرمجاز'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 15
        
        # Get filter parameters
        approval_status = request.args.get('approval_status', '')
        payment_type = request.args.get('payment_type', '')
        user_search = request.args.get('user_search', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query
        query = Invoice.query
        
        if approval_status:
            query = query.filter_by(approval_status=approval_status)
        
        if payment_type:
            query = query.filter_by(payment_type=payment_type)
        
        if user_search:
            query = query.join(User, Invoice.user_id == User.id).filter(
                models.db.or_(
                    User.username.contains(user_search),
                    User.full_name.contains(user_search),
                    User.company_name.contains(user_search)
                )
            )
        
        if date_from:
            try:
                query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
            except ValueError:
                pass
        
        if date_to:
            try:
                query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
            except ValueError:
                pass
        
        # Get paginated results
        invoices_paginated = query.order_by(Invoice.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get all invoices for statistics
        all_invoices = Invoice.query.all()
        
        # Calculate statistics
        stats = {
            'total_invoices': len(all_invoices),
            'pending_approval': len([inv for inv in all_invoices if inv.approval_status == 'pending']),
            'approved': len([inv for inv in all_invoices if inv.approval_status == 'approved']),
            'rejected': len([inv for inv in all_invoices if inv.approval_status == 'rejected']),
            'under_review': len([inv for inv in all_invoices if inv.approval_status == 'under_review']),
            'total_pending_amount': sum([inv.total_amount for inv in all_invoices if inv.approval_status == 'pending']),
            'total_approved_amount': sum([inv.total_amount for inv in all_invoices if inv.approval_status == 'approved'])
        }
        
        # Format invoices data
        invoices_data = []
        for invoice in invoices_paginated.items:
            invoice_data = {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'user_id': invoice.user_id,
                'customer_name': invoice.user.full_name if invoice.user else 'نامشخص',
                'customer_username': invoice.user.username if invoice.user else 'نامشخص',
                'company_name': invoice.user.company_name if invoice.user and invoice.user.company_name else None,
                'total_amount': invoice.total_amount,
                'payment_type': invoice.payment_type,
                'payment_type_display': 'نقدی' if invoice.payment_type == 'cash' else 'چکی',
                'approval_status': invoice.approval_status,
                'approval_status_display': {
                    'pending': 'در انتظار تایید',
                    'approved': 'تایید شده',
                    'rejected': 'رد شده',
                    'under_review': 'در حال بررسی'
                }.get(invoice.approval_status, invoice.approval_status),
                'created_at': invoice.created_at.isoformat(),
                'created_at_persian': invoice.created_at.strftime('%Y/%m/%d %H:%M'),
                'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                'approval_date': invoice.approval_date.isoformat() if invoice.approval_date else None,
                'approved_by': invoice.approver.full_name if invoice.approver else None,
                'rejection_reason': invoice.rejection_reason,
                'admin_notes': invoice.admin_notes,
                'items_count': len(invoice.items),
                'can_approve': invoice.approval_status in ['pending', 'under_review'],
                'can_reject': invoice.approval_status in ['pending', 'under_review']
            }
            invoices_data.append(invoice_data)
        
        # Pagination info
        pagination = {
            'page': invoices_paginated.page,
            'pages': invoices_paginated.pages,
            'per_page': invoices_paginated.per_page,
            'total': invoices_paginated.total,
            'has_next': invoices_paginated.has_next,
            'has_prev': invoices_paginated.has_prev,
            'next_num': invoices_paginated.next_num,
            'prev_num': invoices_paginated.prev_num
        }
        
        # Current filters
        current_filters = {
            'approval_status': approval_status,
            'payment_type': payment_type,
            'user_search': user_search,
            'date_from': date_from,
            'date_to': date_to
        }
        
        return jsonify({
            'success': True,
            'invoices': invoices_data,
            'pagination': pagination,
            'statistics': stats,
            'filters': current_filters
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/customer-invoices/<int:invoice_id>/approve', methods=['PUT'])
@login_required
def api_profile_approve_invoice(invoice_id):
    """Approve a customer invoice."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        return jsonify({'error': 'دسترسی غیرمجاز'}), 403
    
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        invoice = Invoice.query.get_or_404(invoice_id)
        
        if invoice.approval_status not in ['pending', 'under_review']:
            return jsonify({'error': 'فاکتور در وضعیت قابل تایید نیست'}), 400
        
        # Update invoice
        invoice.approval_status = 'approved'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        if admin_notes:
            invoice.admin_notes = admin_notes
        
        models.db.session.commit()
        
        # Create audit log
        audit_log = models.AuditLog(
            actor_id=current_user.id,
            action='approve_invoice',
            target_type='invoice',
            target_id=invoice.id,
            request_id=f"approve_{invoice.id}_{int(datetime.utcnow().timestamp())}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        audit_log.set_details({
            'invoice_number': invoice.invoice_number,
            'customer_name': invoice.user.full_name if invoice.user else 'نامشخص',
            'total_amount': invoice.total_amount,
            'admin_notes': admin_notes
        })
        models.db.session.add(audit_log)
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'فاکتور با موفقیت تایید شد',
            'invoice': {
                'id': invoice.id,
                'approval_status': invoice.approval_status,
                'approval_date': invoice.approval_date.isoformat(),
                'approved_by': current_user.full_name
            }
        }), 200
        
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/customer-invoices/<int:invoice_id>/reject', methods=['PUT'])
@login_required
def api_profile_reject_invoice(invoice_id):
    """Reject a customer invoice."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        return jsonify({'error': 'دسترسی غیرمجاز'}), 403
    
    try:
        data = request.get_json() or {}
        rejection_reason = data.get('rejection_reason', '')
        admin_notes = data.get('admin_notes', '')
        
        if not rejection_reason:
            return jsonify({'error': 'دلیل رد فاکتور الزامی است'}), 400
        
        invoice = Invoice.query.get_or_404(invoice_id)
        
        if invoice.approval_status not in ['pending', 'under_review']:
            return jsonify({'error': 'فاکتور در وضعیت قابل رد نیست'}), 400
        
        # Update invoice
        invoice.approval_status = 'rejected'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        invoice.rejection_reason = rejection_reason
        if admin_notes:
            invoice.admin_notes = admin_notes
        
        models.db.session.commit()
        
        # Create audit log
        audit_log = models.AuditLog(
            actor_id=current_user.id,
            action='reject_invoice',
            target_type='invoice',
            target_id=invoice.id,
            request_id=f"reject_{invoice.id}_{int(datetime.utcnow().timestamp())}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        audit_log.set_details({
            'invoice_number': invoice.invoice_number,
            'customer_name': invoice.user.full_name if invoice.user else 'نامشخص',
            'total_amount': invoice.total_amount,
            'rejection_reason': rejection_reason,
            'admin_notes': admin_notes
        })
        models.db.session.add(audit_log)
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'فاکتور با موفقیت رد شد',
            'invoice': {
                'id': invoice.id,
                'approval_status': invoice.approval_status,
                'approval_date': invoice.approval_date.isoformat(),
                'rejection_reason': rejection_reason,
                'rejected_by': current_user.full_name
            }
        }), 200
        
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/customer-invoices/<int:invoice_id>/details')
@login_required
def api_profile_invoice_details(invoice_id):
    """Get detailed invoice information."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        return jsonify({'error': 'دسترسی غیرمجاز'}), 403
    
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        # Get invoice items
        items_data = []
        for item in invoice.items:
            item_data = {
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'محصول حذف شده',
                'product_sku': item.product.sku if item.product else 'نامشخص',
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'price_type': item.price_type,
                'price_plan': item.price_plan
            }
            items_data.append(item_data)
        
        # Get invoice documents
        documents_data = []
        for doc in invoice.documents:
            doc_data = {
                'id': doc.id,
                'document_type': doc.document_type,
                'document_type_display': 'چک' if doc.document_type == 'check' else 'رسید',
                'file_path': doc.file_path,
                'uploaded_at': doc.uploaded_at.isoformat(),
                'is_approved': doc.is_approved,
                'approval_date': doc.approval_date.isoformat() if doc.approval_date else None,
                'approved_by': doc.approver.full_name if doc.approver else None,
                'rejection_reason': doc.rejection_reason,
                'admin_notes': doc.admin_notes
            }
            documents_data.append(doc_data)
        
        # Customer information
        customer_data = {
            'id': invoice.user.id if invoice.user else None,
            'username': invoice.user.username if invoice.user else 'نامشخص',
            'full_name': invoice.user.full_name if invoice.user else 'نامشخص',
            'company_name': invoice.user.company_name if invoice.user and invoice.user.company_name else None,
            'phone': invoice.user.phone if invoice.user else 'نامشخص',
            'email': invoice.user.email if invoice.user else None,
            'address': invoice.user.address if invoice.user else None,
            'is_bulk_buyer': invoice.user.is_bulk_buyer if invoice.user else False,
            'bulk_buyer_approval_status': invoice.user.bulk_buyer_approval_status if invoice.user else None
        }
        
        # Detailed invoice data
        invoice_data = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'customer': customer_data,
            'total_amount': invoice.total_amount,
            'payment_type': invoice.payment_type,
            'payment_type_display': 'نقدی' if invoice.payment_type == 'cash' else 'چکی',
            'approval_status': invoice.approval_status,
            'approval_status_display': {
                'pending': 'در انتظار تایید',
                'approved': 'تایید شده',
                'rejected': 'رد شده',
                'under_review': 'در حال بررسی'
            }.get(invoice.approval_status, invoice.approval_status),
            'created_at': invoice.created_at.isoformat(),
            'created_at_persian': invoice.created_at.strftime('%Y/%m/%d %H:%M'),
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'approval_date': invoice.approval_date.isoformat() if invoice.approval_date else None,
            'approved_by': invoice.approver.full_name if invoice.approver else None,
            'rejection_reason': invoice.rejection_reason,
            'admin_notes': invoice.admin_notes,
            'items': items_data,
            'documents': documents_data,
            'items_count': len(invoice.items),
            'documents_count': len(invoice.documents)
        }
        
        return jsonify({
            'success': True,
            'invoice': invoice_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==== Invoice approval actions (for admins and order managers) ====
@app.route('/admin/invoice/<int:invoice_id>/approve', methods=['POST'])
@login_required
def admin_approve_invoice(invoice_id):
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    invoice = Invoice.query.get_or_404(invoice_id)
    try:
        invoice.approval_status = 'approved'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        invoice.rejection_reason = None
        models.db.session.commit()
        flash(f'فاکتور {invoice.invoice_number} تایید شد.', 'success')
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در تایید فاکتور.', 'error')
    return redirect(url_for('admin_invoice_detail', invoice_id=invoice_id))

@app.route('/admin/invoice/<int:invoice_id>/reject', methods=['POST'])
@login_required
def admin_reject_invoice(invoice_id):
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    invoice = Invoice.query.get_or_404(invoice_id)
    rejection_reason = request.form.get('rejection_reason', '').strip()
    try:
        invoice.approval_status = 'rejected'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        invoice.rejection_reason = rejection_reason or 'بدون دلیل'
        models.db.session.commit()
        flash(f'فاکتور {invoice.invoice_number} رد شد.', 'success')
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در رد فاکتور.', 'error')
    return redirect(url_for('admin_invoice_detail', invoice_id=invoice_id))

@app.route('/admin/document/<int:document_id>/approve', methods=['POST'])
@login_required
def admin_approve_document(document_id):
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    document = InvoiceDocument.query.get_or_404(document_id)
    try:
        document.is_approved = True
        document.approval_date = datetime.utcnow()
        document.approved_by = current_user.id
        document.rejection_reason = None
        models.db.session.commit()
        flash('سند پرداخت تایید شد.', 'success')
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در تایید سند.', 'error')
    return redirect(url_for('admin_invoice_detail', invoice_id=document.invoice_id))

@app.route('/admin/document/<int:document_id>/reject', methods=['POST'])
@login_required
def admin_reject_document(document_id):
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    document = InvoiceDocument.query.get_or_404(document_id)
    rejection_reason = request.form.get('rejection_reason', '').strip()
    try:
        document.is_approved = False
        document.approval_date = datetime.utcnow()
        document.approved_by = current_user.id
        document.rejection_reason = rejection_reason or 'بدون دلیل'
        models.db.session.commit()
        flash('سند پرداخت رد شد.', 'success')
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در رد سند.', 'error')
    return redirect(url_for('admin_invoice_detail', invoice_id=document.invoice_id))

@app.route('/admin/document/<int:document_id>')
@login_required
def admin_view_document(document_id):
    """View invoice document (order managers only)."""
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    
    document = InvoiceDocument.query.get_or_404(document_id)
    
    # Check if file exists
    file_path = document.file_path
    if not file_path:
        abort(404)
    
    if not os.path.isabs(file_path):
        base_upload = app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(base_upload, file_path)
    
    if not os.path.exists(file_path):
        abort(404)
    
    # Determine content type based on file extension
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    return send_file(file_path, as_attachment=False, mimetype=content_type)

@app.route('/admin/invoice/<int:invoice_id>/set-review', methods=['POST'])
@login_required
def admin_set_review_invoice(invoice_id):
    if not current_user.has_role('مدیر_سفارشات', scope='site'):
        abort(403)
    invoice = Invoice.query.get_or_404(invoice_id)
    admin_notes = request.form.get('admin_notes', '').strip()
    try:
        invoice.approval_status = 'under_review'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        if admin_notes:
            invoice.admin_notes = admin_notes
        models.db.session.commit()
        flash('فاکتور به حالت بررسی تنظیم شد.', 'success')
    except Exception:
        models.db.session.rollback()
        flash('خطا در تنظیم وضعیت فاکتور.', 'error')
    return redirect(url_for('admin_invoice_detail', invoice_id=invoice_id))

@app.route('/admin/roles')
@login_required
def admin_roles():
    """Admin roles management"""
    if not current_user.is_admin:
        abort(403)
    
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@app.route('/admin/user-roles')
@login_required
def admin_user_roles():
    """Admin user roles management"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    roles = Role.query.all()
    
    return render_template('admin/user_roles.html', users=users, roles=roles)

@app.route('/admin/announcements')
@login_required
def admin_announcements():
    """Admin announcements management"""
    if not current_user.is_admin:
        abort(403)
    
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/company-info')
@login_required
def admin_company_info():
    """Admin company info management"""
    if not current_user.is_admin:
        abort(403)
    
    company_info = CompanyInfo.query.first()
    return render_template('admin/company_info.html', company_info=company_info)

@app.route('/admin/vehicle-types')
@login_required
def admin_vehicle_types():
    """Admin vehicle types management"""
    if not current_user.is_admin:
        abort(403)
    
    vehicle_types = VehicleType.query.all()
    return render_template('admin/vehicle_types.html', vehicle_types=vehicle_types)

@app.route('/admin/audit-logs')
@login_required
def admin_audit_logs():
    """Admin audit logs"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/audit_logs.html', audit_logs=audit_logs)

@app.route('/admin/delete-invoice/<int:invoice_id>', methods=['POST'])
@login_required
def admin_delete_invoice(invoice_id):
    """Delete invoice (admin only)"""
    if not current_user.is_admin:
        abort(403)
    
    invoice = Invoice.query.get_or_404(invoice_id)
    
    try:
        # Delete the invoice (cascade will handle related items and documents)
        models.db.session.delete(invoice)
        models.db.session.commit()
        
        flash(f'فاکتور {invoice.invoice_number} با موفقیت حذف شد.', 'success')
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در حذف فاکتور. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_invoices'))

@app.route('/admin/text-color-optimization')
@login_required
def admin_text_color_optimization():
    """Admin text color optimization tool"""
    if not current_user.is_admin:
        abort(403)
    
    return render_template('admin/text_color_optimization.html')

@app.route('/admin/excel-reconstruction')
@login_required
def excel_reconstruction():
    """Admin Excel reconstruction tool"""
    if not current_user.is_admin:
        abort(403)
    
    return render_template('admin/excel_reconstruction.html')

@app.route('/admin/bulk-buyer-requests')
@login_required
def admin_bulk_buyer_requests():
    """Admin bulk buyer requests management"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    approval_status = request.args.get('approval_status', '')
    user_search = request.args.get('user_search', '')
    
    # Build query
    query = User.query.filter(User.is_bulk_buyer == True)
    
    if approval_status:
        query = query.filter_by(bulk_buyer_approval_status=approval_status)
    
    if user_search:
        query = query.filter(
            models.db.or_(
                User.username.contains(user_search),
                User.full_name.contains(user_search),
                User.company_name.contains(user_search)
            )
        )
    
    # Get all bulk buyer requests for statistics
    all_requests = User.query.filter(User.is_bulk_buyer == True).all()
    
    # Calculate statistics
    total_requests = len(all_requests)
    pending_requests = len([req for req in all_requests if req.bulk_buyer_approval_status == 'pending'])
    approved_requests = len([req for req in all_requests if req.bulk_buyer_approval_status == 'approved'])
    rejected_requests = len([req for req in all_requests if req.bulk_buyer_approval_status == 'rejected'])
    
    # Create stats object for template
    stats = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests
    }
    
    # Create current_filters object for template
    current_filters = {
        'approval_status': approval_status,
        'user_search': user_search
    }
    
    requests = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/bulk_buyer_requests.html', 
                         requests=requests, 
                         stats=stats, 
                         current_filters=current_filters)

@app.route('/admin/approve-bulk-buyer/<int:user_id>', methods=['POST'])
@login_required
def admin_approve_bulk_buyer(user_id):
    """Approve bulk buyer request"""
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if not user.is_bulk_buyer:
        flash('این کاربر درخواست خریدار عمده نداشته است.', 'error')
        return redirect(url_for('admin_bulk_buyer_requests'))
    
    try:
        # Update user approval status
        user.bulk_buyer_approval_status = 'approved'
        user.bulk_buyer_approved_at = datetime.utcnow()
        user.bulk_buyer_approved_by = current_user.id
        
        # Send notification to user
        notification = UserNotification(
            user_id=user.id,
            notification_type='bulk_buyer_approved',
            title='تایید خریدار عمده',
            message='درخواست خریدار عمده شما تایید شد. اکنون می‌توانید از قیمت‌های ویژه و شرایط خاص بهره‌مند شوید.'
        )
        models.db.session.add(notification)
        
        models.db.session.commit()
        
        flash(f'درخواست خریدار عمده کاربر {user.full_name} تایید شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در تایید درخواست. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_bulk_buyer_requests'))

@app.route('/admin/reject-bulk-buyer/<int:user_id>', methods=['POST'])
@login_required
def admin_reject_bulk_buyer(user_id):
    """Reject bulk buyer request"""
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    rejection_reason = request.form.get('rejection_reason', '')
    
    if not user.is_bulk_buyer:
        flash('این کاربر درخواست خریدار عمده نداشته است.', 'error')
        return redirect(url_for('admin_bulk_buyer_requests'))
    
    try:
        # Update user approval status
        user.bulk_buyer_approval_status = 'rejected'
        user.bulk_buyer_approved_at = datetime.utcnow()
        user.bulk_buyer_approved_by = current_user.id
        
        # Send notification to user
        notification = UserNotification(
            user_id=user.id,
            notification_type='bulk_buyer_rejected',
            title='رد درخواست خریدار عمده',
            message=f'متأسفانه درخواست خریدار عمده شما رد شد. دلیل: {rejection_reason if rejection_reason else "لطفاً با پشتیبانی تماس بگیرید."}'
        )
        models.db.session.add(notification)
        
        models.db.session.commit()
        
        flash(f'درخواست خریدار عمده کاربر {user.full_name} رد شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در رد درخواست. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_bulk_buyer_requests'))

# ==================== API ROUTES ====================

@app.route('/api/search')
def api_search():
    """Search API endpoint"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify([])
        
        # Try normalized search first
        try:
            norm_q = normalize_fa_text(query)
            name_norm = normalize_sql_expr(Product.name)
            name_fa_norm = normalize_sql_expr(Product.name_fa)
            
            products = Product.query.filter(
                models.db.or_(
                    name_norm.contains(norm_q),
                    name_fa_norm.contains(norm_q),
                    Product.sku.contains(norm_q),
                    Product.oem_code.contains(norm_q)
                ),
                Product.is_active == True
            ).limit(limit).all()
        except Exception as e:
            # Fallback to simple search
            app.logger.error(f"API search normalization failed: {e}")
            products = Product.query.filter(
                models.db.or_(
                    Product.name.contains(query),
                    Product.name_fa.contains(query),
                    Product.sku.contains(query),
                    Product.oem_code.contains(query)
                ),
                Product.is_active == True
            ).limit(limit).all()
        
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name_fa,
                'sku': product.sku,
                'price': product.retail_price_cash,
                'image': product.primary_image,
                'url': url_for('product_detail', product_id=product.id)
            })
        
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"API search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/cart-count')
def api_cart_count():
    """Get cart items count (returns 0 for anonymous users)"""
    if current_user.is_authenticated:
        count = Cart.query.filter_by(user_id=current_user.id).count()
    else:
        count = 0
    return jsonify({'count': count})

# Alias for legacy frontend path
@app.route('/api/cart/count')
def api_cart_count_alias():
    return api_cart_count()

@app.route('/api/cart/add-multiple', methods=['POST'])
@login_required
def api_add_multiple_to_cart():
    """Add multiple products to cart via API"""
    try:
        data = request.get_json()
        products = data.get('products', [])
        
        if not products:
            return jsonify({'success': False, 'message': 'هیچ محصولی انتخاب نشده است'}), 400
        
        added_count = 0
        errors = []
        
        for product_data in products:
            try:
                product_id = product_data.get('product_id')
                quantity = product_data.get('quantity', 1)
                price_type = product_data.get('price_type', 'cash')
                price_plan = product_data.get('price_plan')
                notes = product_data.get('notes', '')
                
                
                if not product_id:
                    continue
                
                product = Product.query.get(product_id)
                if not product:
                    errors.append(f"محصول با شناسه {product_id} یافت نشد")
                    continue
                
                # ISACO validation
                if is_isaco_feature_enabled() and getattr(product, 'is_isaco_wh15', False):
                    # Check if product has valid Isaco pricing
                    has_valid_isaco_pricing = any([
                        product.isaco_cash and product.isaco_cash > 0,
                        product.isaco_1m and product.isaco_1m > 0,
                        product.isaco_2m and product.isaco_2m > 0,
                        product.isaco_3m and product.isaco_3m > 0
                    ])
                    
                    if has_valid_isaco_pricing:
                        # Product has valid Isaco pricing, require plan selection
                        if not price_plan or price_plan not in isaco_allowed_plans():
                            errors.append(f"کالا {product.sku}: انتخاب یکی از گزینه‌های ایساکو الزامی است")
                            continue
                        unit_price_candidate = get_isaco_unit_price(product, price_plan)
                        if not unit_price_candidate or unit_price_candidate <= 0:
                            errors.append(f"کالا {product.sku}: قیمت انتخاب‌شده نامعتبر است")
                            continue
                    else:
                        # Product is marked as Isaco but has no valid Isaco pricing, use regular pricing
                        if current_user.is_bulk_buyer and current_user.bulk_buyer_approval_status == 'approved':
                            unit_price_candidate = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
                        else:
                            unit_price_candidate = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
                        
                        if not unit_price_candidate or unit_price_candidate <= 0:
                            errors.append(f"کالا {product.sku}: قیمت انتخاب‌شده نامعتبر است")
                            continue

                # Check if item already exists in cart (include plan)
                existing_item = Cart.query.filter_by(
                    user_id=current_user.id,
                    product_id=product_id,
                    price_type=price_type,
                    price_plan=price_plan
                ).first()
                
                if existing_item:
                    existing_item.quantity += quantity
                else:
                    # Determine unit price
                    if is_isaco_feature_enabled() and getattr(product, 'is_isaco_wh15', False):
                        unit_price = get_isaco_unit_price(product, price_plan)
                        # Fallback to regular pricing if Isaco prices are not available
                        if not unit_price or unit_price <= 0:
                            if current_user.is_bulk_buyer and current_user.bulk_buyer_approval_status == 'approved':
                                unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
                            else:
                                unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
                    else:
                        if current_user.is_bulk_buyer and current_user.bulk_buyer_approval_status == 'approved':
                            unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
                        else:
                            unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
                    
                    cart_item = Cart(
                        user_id=current_user.id,
                        product_id=product_id,
                        quantity=quantity,
                        price_type=price_type,
                        price_plan=price_plan,
                        unit_price=unit_price,
                        notes=notes
                    )
                    models.db.session.add(cart_item)
                
                added_count += 1
                
            except Exception as e:
                errors.append(f"خطا در افزودن محصول {product_id}: {str(e)}")
                continue
        
        models.db.session.commit()
        
        message = f"{added_count} محصول به سبد خرید اضافه شد"
        if errors:
            message += f". خطاها: {'; '.join(errors)}"
        
        return jsonify({
            'success': True,
            'message': message,
            'added_count': added_count,
            'errors': errors
        })
        
    except Exception as e:
        models.db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در افزودن محصولات به سبد خرید'
        }), 500

@app.route('/api/cart', methods=['GET'])
@login_required
def api_get_cart():
    """Get cart items via API"""
    try:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        items_data = [item.to_dict() for item in cart_items]
        
        return jsonify({
            'success': True,
            'items': items_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت سبد خرید'
        }), 500

@app.route('/api/cart/remove', methods=['DELETE'])
@login_required
def api_remove_from_cart():
    """Remove item from cart via API"""
    try:
        data = request.get_json()
        cart_id = data.get('cart_id')
        
        if not cart_id:
            return jsonify({'success': False, 'message': 'شناسه آیتم سبد الزامی است'}), 400
        
        cart_item = Cart.query.filter_by(
            id=cart_id,
            user_id=current_user.id
        ).first_or_404()
        
        models.db.session.delete(cart_item)
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'محصول از سبد خرید حذف شد'
        })
        
    except Exception as e:
        models.db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در حذف محصول از سبد خرید'
        }), 500

@app.route('/api/cart/update', methods=['PUT'])
@login_required
def api_update_cart_quantity():
    """Update cart item quantity via API"""
    try:
        data = request.get_json()
        cart_id = data.get('cart_id')
        quantity = data.get('quantity', 1)
        
        if not cart_id:
            return jsonify({'success': False, 'message': 'شناسه آیتم سبد الزامی است'}), 400
        
        cart_item = Cart.query.filter_by(
            id=cart_id,
            user_id=current_user.id
        ).first_or_404()
        
        if quantity > 0:
            cart_item.quantity = quantity
            models.db.session.commit()
            return jsonify({
                'success': True,
                'message': 'تعداد محصول به‌روزرسانی شد'
            })
        else:
            models.db.session.delete(cart_item)
            models.db.session.commit()
            return jsonify({
                'success': True,
                'message': 'محصول از سبد خرید حذف شد'
            })
        
    except Exception as e:
        models.db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در به‌روزرسانی تعداد'
        }), 500

@app.route('/api/cart/totals', methods=['GET'])
@login_required
def api_get_cart_totals():
    """Get cart totals with breakdown"""
    try:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        
        cash_total = 0
        check_total = 0
        
        for item in cart_items:
            total_price = item.unit_price * item.quantity
            if item.price_type == 'cash':
                cash_total += total_price
            else:
                check_total += total_price
        
        grand_total = cash_total + check_total
        
        # Format prices for display (prices are stored in thousands Rials)
        def format_price(price):
            if price is None or price == 0:
                return "0 هزار ریال"
            price_in_thousands = int(price)
            return f"{price_in_thousands:,} هزار ریال"
        
        return jsonify({
            'success': True,
            'cash_total': cash_total,
            'check_total': check_total,
            'grand_total': grand_total,
            'formatted_cash_total': format_price(cash_total),
            'formatted_check_total': format_price(check_total),
            'formatted_grand_total': format_price(grand_total)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'خطا در محاسبه مجموع قیمت‌ها'
        }), 500


# ==================== BRAND VEHICLE DETECTION ====================

@app.route('/admin/brand-detection')
@login_required
def admin_brand_detection():
    """صفحه مدیریت تشخیص برند و نوع خودرو"""
    if not current_user.is_admin:
        flash('شما دسترسی لازم برای این صفحه را ندارید', 'error')
        return redirect(url_for('index'))
    
    # آمار تشخیص
    from brand_vehicle_detector import get_detector
    detector = get_detector()
    stats = detector.get_detection_stats()
    
    return render_template('admin/brand_detection.html', stats=stats)

# Aliases expected by frontend
@app.route('/admin/detection-status')
@login_required
def admin_detection_status_alias():
    # Return stats in the shape expected by admin templates
    try:
        from brand_vehicle_detector import get_detector
        detector = get_detector()
        stats = detector.get_detection_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/run-batch-detection', methods=['POST'])
@login_required
def admin_run_batch_detection_alias():
    # Run batch detection and return simplified response for dashboard
    try:
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': 'شما دسترسی لازم برای این عملیات را ندارید'}), 403

        from brand_vehicle_detector import get_detector
        detector = get_detector()
        result = detector.batch_detect_products()

        if result.get('status') == 'success':
            data = result.get('data', {})
            message = (
                f"اجرای تشخیص با موفقیت انجام شد. تعداد پردازش‌شده: "
                f"{data.get('total_processed', 0)}, به‌روزرسانی‌شده: {data.get('updated_count', 0)}"
            )
            return jsonify({'success': True, 'message': message, 'data': data})
        else:
            return jsonify({'success': False, 'message': result.get('message', 'خطا در تشخیص دسته‌ای')}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/detect-brand-vehicle', methods=['POST'])
@login_required
def api_detect_brand_vehicle():
    """API تشخیص برند و نوع خودرو"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        
        if not product_name:
            return jsonify({
                'success': False,
                'message': 'نام محصول نمی‌تواند خالی باشد'
            }), 400
        
        from brand_vehicle_detector import get_detector
        detector = get_detector()
        result = detector.detect_brand_and_vehicle_types(product_name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در تشخیص: {str(e)}'
        }), 500

@app.route('/api/batch-detect-products', methods=['POST'])
@login_required
def api_batch_detect_products():
    """API تشخیص دسته‌ای محصولات"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        data = request.get_json()
        product_ids = data.get('product_ids')
        
        from brand_vehicle_detector import get_detector
        detector = get_detector()
        
        if product_ids and len(product_ids) > 0:
            result = detector.batch_detect_products(product_ids)
        else:
            result = detector.batch_detect_products()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در تشخیص دسته‌ای: {str(e)}'
        }), 500

@app.route('/api/detection-stats', methods=['GET'])
@login_required
def api_detection_stats():
    """API آمار تشخیص"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from brand_vehicle_detector import get_detector
        detector = get_detector()
        stats = detector.get_detection_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت آمار: {str(e)}'
        }), 500

@app.route('/api/refresh-detection-cache', methods=['POST'])
@login_required
def api_refresh_detection_cache():
    """API به‌روزرسانی کش تشخیص"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from brand_vehicle_detector import get_detector
        detector = get_detector()
        detector.refresh_cache()
        
        return jsonify({
            'success': True,
            'message': 'کش تشخیص با موفقیت به‌روزرسانی شد'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در به‌روزرسانی کش: {str(e)}'
        }), 500

@app.route('/api/category/<int:category_id>/brand-vehicle-stats', methods=['GET'])
def api_category_brand_vehicle_stats(category_id):
    """آمار برندها و انواع خودرو برای یک دسته‌بندی بر اساس تعداد محصولات (نزولی)"""
    try:
        from sqlalchemy import func

        # Validate category exists
        category = PartCategory.query.get_or_404(category_id)

        # Brand counts within category
        brand_counts = (
            models.db.session
                .query(Brand.id, Brand.name, Brand.name_fa, func.count(Product.id).label('cnt'))
                .join(Product, Product.brand_id == Brand.id)
                .filter(Product.category_id == category_id)
                .group_by(Brand.id, Brand.name, Brand.name_fa)
                .order_by(func.count(Product.id).desc())
                .all()
        )

        brands = [
            {
                'id': b.id,
                'name': b.name,
                'name_fa': b.name_fa,
                'count': int(b.cnt)
            }
            for b in brand_counts
        ]

        # Vehicle type counts within category
        vt_counts = (
            models.db.session
                .query(VehicleType.id, VehicleType.name, func.count(Product.id).label('cnt'))
                .join(ProductVehicleType, ProductVehicleType.vehicle_type_id == VehicleType.id)
                .join(Product, Product.id == ProductVehicleType.product_id)
                .filter(Product.category_id == category_id)
                .group_by(VehicleType.id, VehicleType.name)
                .order_by(func.count(Product.id).desc())
                .all()
        )

        vehicle_types = [
            {
                'id': vt.id,
                'name': vt.name,
                'count': int(vt.cnt)
            }
            for vt in vt_counts
        ]

        return jsonify({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.category_name,
                'name_fa': category.category_name_fa,
            },
            'brands': brands,
            'vehicle_types': vehicle_types
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== TADBIR ACCOUNTING SYSTEM ROUTES ====================

@app.route('/admin/accounting/dashboard')
@login_required
def admin_accounting_dashboard():
    """داشبورد حسابداری تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        from tadbir_sync_service import TadbirSyncService
        from tadbir_scheduler_service import get_scheduler
        
        sync_service = TadbirSyncService()
        scheduler = get_scheduler()
        
        # Get sync status
        sync_status = sync_service.get_sync_status()
        scheduler_status = scheduler.get_scheduler_status()
        
        # Get recent sync logs
        recent_logs = TadbirSyncLog.query.order_by(
            TadbirSyncLog.started_at.desc()
        ).limit(10).all()
        
        # Get cache statistics
        products_count = TadbirProductCache.query.count()
        inventory_count = TadbirInventoryCache.query.count()
        prices_count = TadbirPriceCache.query.count()
        
        stats = {
            'products_count': products_count,
            'inventory_count': inventory_count,
            'prices_count': prices_count,
            'total_cached_items': products_count + inventory_count + prices_count
        }
        
        return render_template('admin/accounting_dashboard.html',
                             sync_status=sync_status,
                             scheduler_status=scheduler_status,
                             recent_logs=recent_logs,
                             stats=stats)
        
    except Exception as e:
        flash(f'خطا در بارگذاری داشبورد حسابداری: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/accounting/sync/manual', methods=['POST'])
@login_required
def admin_accounting_manual_sync():
    """همگام‌سازی دستی تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        from tadbir_scheduler_service import get_scheduler
        
        sync_type = request.form.get('sync_type', 'full')
        scheduler = get_scheduler()
        
        # Run sync
        result = scheduler.run_sync_now(sync_type)
        
        if sync_type == 'full':
            flash('همگام‌سازی کامل با موفقیت انجام شد.', 'success')
        else:
            flash(f'همگام‌سازی {sync_type} با موفقیت انجام شد.', 'success')
        
        return redirect(url_for('admin_accounting_dashboard'))
        
    except Exception as e:
        flash(f'خطا در همگام‌سازی: {str(e)}', 'error')
        return redirect(url_for('admin_accounting_dashboard'))

@app.route('/admin/accounting/sync/history')
@login_required
def admin_accounting_sync_history():
    """تاریخچه همگام‌سازی تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    sync_type = request.args.get('sync_type', '')
    status = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = TadbirSyncLog.query
    
    if sync_type:
        query = query.filter_by(sync_type=sync_type)
    
    if status:
        query = query.filter_by(status=status)
    
    if date_from:
        query = query.filter(TadbirSyncLog.started_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    if date_to:
        query = query.filter(TadbirSyncLog.started_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Get statistics
    total_logs = TadbirSyncLog.query.count()
    successful_logs = TadbirSyncLog.query.filter_by(status='completed').count()
    failed_logs = TadbirSyncLog.query.filter_by(status='failed').count()
    
    stats = {
        'total_logs': total_logs,
        'successful_logs': successful_logs,
        'failed_logs': failed_logs
    }
    
    # Create current_filters object for template
    current_filters = {
        'sync_type': sync_type,
        'status': status,
        'date_from': date_from,
        'date_to': date_to
    }
    
    logs = query.order_by(TadbirSyncLog.started_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/accounting_sync_history.html',
                         logs=logs,
                         stats=stats,
                         current_filters=current_filters)

@app.route('/admin/accounting/products')
@login_required
def admin_accounting_products():
    """لیست کالاهای تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    search = request.args.get('search', '')
    is_active = request.args.get('is_active', '')
    last_update_from = request.args.get('last_update_from', '')
    last_update_to = request.args.get('last_update_to', '')
    
    # Build query
    query = TadbirProductCache.query
    
    if search:
        query = query.filter(
            models.db.or_(
                TadbirProductCache.item_code.contains(search),
                TadbirProductCache.description.contains(search),
                TadbirProductCache.alias.contains(search)
            )
        )
    
    if is_active == 'true':
        query = query.filter_by(is_active=True)
    elif is_active == 'false':
        query = query.filter_by(is_active=False)
    
    if last_update_from:
        query = query.filter(TadbirProductCache.last_update >= datetime.strptime(last_update_from, '%Y-%m-%d'))
    
    if last_update_to:
        query = query.filter(TadbirProductCache.last_update <= datetime.strptime(last_update_to, '%Y-%m-%d'))
    
    # Get statistics
    total_products = TadbirProductCache.query.count()
    active_products = TadbirProductCache.query.filter_by(is_active=True).count()
    inactive_products = TadbirProductCache.query.filter_by(is_active=False).count()
    
    stats = {
        'total_products': total_products,
        'active_products': active_products,
        'inactive_products': inactive_products
    }
    
    # Create current_filters object for template
    current_filters = {
        'search': search,
        'is_active': is_active,
        'last_update_from': last_update_from,
        'last_update_to': last_update_to
    }
    
    products = query.order_by(TadbirProductCache.cached_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/accounting_products.html',
                         products=products,
                         stats=stats,
                         current_filters=current_filters)

@app.route('/admin/accounting/inventory')
@login_required
def admin_accounting_inventory():
    """موجودی انبار تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    search = request.args.get('search', '')
    stock_filter = request.args.get('stock_filter', 'all')
    
    # Build query
    query = TadbirInventoryCache.query
    
    if search:
        query = query.filter(
            models.db.or_(
                TadbirInventoryCache.item_code.contains(search)
            )
        )
    
    if stock_filter == 'in_stock':
        query = query.filter(TadbirInventoryCache.quantity > 0)
    elif stock_filter == 'out_of_stock':
        query = query.filter(TadbirInventoryCache.quantity == 0)
    elif stock_filter == 'low_stock':
        query = query.filter(TadbirInventoryCache.quantity > 0, TadbirInventoryCache.quantity < 10)
    
    # Get statistics
    total_items = TadbirInventoryCache.query.count()
    in_stock_items = TadbirInventoryCache.query.filter(TadbirInventoryCache.quantity > 0).count()
    out_of_stock_items = TadbirInventoryCache.query.filter(TadbirInventoryCache.quantity == 0).count()
    low_stock_items = TadbirInventoryCache.query.filter(
        TadbirInventoryCache.quantity > 0, 
        TadbirInventoryCache.quantity < 10
    ).count()
    
    stats = {
        'total_items': total_items,
        'in_stock_items': in_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'low_stock_items': low_stock_items
    }
    
    # Create current_filters object for template
    current_filters = {
        'search': search,
        'stock_filter': stock_filter
    }
    
    inventory = query.order_by(TadbirInventoryCache.cached_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/accounting_inventory.html',
                         inventory=inventory,
                         stats=stats,
                         current_filters=current_filters)

@app.route('/admin/accounting/prices')
@login_required
def admin_accounting_prices():
    """قیمت‌های کالاهای تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    price_type = request.args.get('price_type', '')
    search = request.args.get('search', '')
    
    # Build query
    query = TadbirPriceCache.query
    
    if price_type:
        query = query.filter_by(price_type=price_type)
    
    if search:
        query = query.filter(
            models.db.or_(
                TadbirPriceCache.item_code.contains(search)
            )
        )
    
    # Get statistics
    total_prices = TadbirPriceCache.query.count()
    retail_check_prices = TadbirPriceCache.query.filter_by(price_type='retail_check').count()
    bulk_check_prices = TadbirPriceCache.query.filter_by(price_type='bulk_check').count()
    bulk_cash_prices = TadbirPriceCache.query.filter_by(price_type='bulk_cash').count()
    
    stats = {
        'total_prices': total_prices,
        'retail_check_prices': retail_check_prices,
        'bulk_check_prices': bulk_check_prices,
        'bulk_cash_prices': bulk_cash_prices
    }
    
    # Create current_filters object for template
    current_filters = {
        'price_type': price_type,
        'search': search
    }
    
    prices = query.order_by(TadbirPriceCache.cached_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/accounting_prices.html',
                         prices=prices,
                         stats=stats,
                         current_filters=current_filters)

@app.route('/admin/accounting/settings', methods=['GET', 'POST'])
@login_required
def admin_accounting_settings():
    """تنظیمات سیستم حسابداری تدبیر"""
    if not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        try:
            # Get form data
            settings = {
                'auto_sync_enabled': request.form.get('auto_sync_enabled') == 'on',
                'sync_interval': int(request.form.get('sync_interval', 3)),
                'batch_size': int(request.form.get('batch_size', 1000)),
                'retry_attempts': int(request.form.get('retry_attempts', 3)),
                'enable_incremental_sync': request.form.get('enable_incremental_sync') == 'on',
                'sync_products': request.form.get('sync_products') == 'on',
                'sync_inventory': request.form.get('sync_inventory') == 'on',
                'sync_prices': request.form.get('sync_prices') == 'on',
                'default_markup_percentage': float(request.form.get('default_markup_percentage', 10)),
                'price_rounding': request.form.get('price_rounding', 'round'),
                'currency_format': request.form.get('currency_format', 'هزار تومان')
            }
            
            # Validate decimal values
            markup_percentage = settings['default_markup_percentage']
            if not isinstance(markup_percentage, (int, float)) or markup_percentage < 0 or markup_percentage > 100:
                flash('درصد اضافی باید عددی بین 0 تا 100 باشد', 'error')
                return redirect(url_for('admin_accounting_settings'))
            
            # Update settings in database
            for key, value in settings.items():
                setting = TadbirSyncSettings.query.filter_by(setting_key=key).first()
                if setting:
                    setting.setting_value = str(value)
                    setting.updated_at = datetime.utcnow()
                    setting.updated_by = current_user.id
                else:
                    setting = TadbirSyncSettings(
                        setting_key=key,
                        setting_value=str(value),
                        updated_at=datetime.utcnow(),
                        updated_by=current_user.id
                    )
                    models.db.session.add(setting)
            
            models.db.session.commit()
            
            # Update scheduler if needed
            from tadbir_scheduler_service import get_scheduler
            scheduler = get_scheduler()
            scheduler.update_settings(settings)
            
            flash('تنظیمات با موفقیت به‌روزرسانی شد.', 'success')
            return redirect(url_for('admin_accounting_settings'))
            
        except Exception as e:
            models.db.session.rollback()
            flash(f'خطا در به‌روزرسانی تنظیمات: {str(e)}', 'error')
    
    # Get current settings
    settings = {}
    for setting in TadbirSyncSettings.query.all():
        # Convert to appropriate type
        value = setting.setting_value
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        settings[setting.setting_key] = value
    
    return render_template('admin/accounting_settings.html', settings=settings)

@app.route('/api/accounting/test-connection', methods=['POST'])
@login_required
def api_accounting_test_connection():
    """تست اتصال به API تدبیر"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_api_service import TadbirAPIService
        
        api_service = TadbirAPIService()
        result = api_service.test_connection()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در تست اتصال: {str(e)}'
        }), 500

@app.route('/api/accounting/sync-status', methods=['GET'])
@login_required
def api_accounting_sync_status():
    """دریافت وضعیت همگام‌سازی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_sync_service import TadbirSyncService
        from tadbir_scheduler_service import get_scheduler
        
        sync_service = TadbirSyncService()
        scheduler = get_scheduler()
        
        sync_status = sync_service.get_sync_status()
        scheduler_status = scheduler.get_scheduler_status()
        
        return jsonify({
            'success': True,
            'sync_status': sync_status,
            'scheduler_status': scheduler_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت وضعیت: {str(e)}'
        }), 500

@app.route('/api/accounting/debug-api', methods=['POST'])
@login_required
def api_accounting_debug_api():
    """Debug API endpoints"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_api_service import TadbirAPIService
        
        api_service = TadbirAPIService()
        debug_info = api_service.debug_api_endpoints()
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دیباگ API: {str(e)}'
        }), 500

@app.route('/api/accounting/total-counts', methods=['GET'])
@login_required
def api_accounting_total_counts():
    """دریافت تعداد کل کالاها و قیمت‌ها"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_api_service import TadbirAPIService
        
        api_service = TadbirAPIService()
        counts = api_service.get_total_counts()
        
        return jsonify({
            'success': True,
            'counts': counts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت تعداد کل: {str(e)}'
        }), 500

@app.route('/api/accounting/scheduler/start', methods=['POST'])
@login_required
def api_accounting_scheduler_start():
    """شروع سرویس زمان‌بندی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_scheduler_service import get_scheduler
        
        scheduler = get_scheduler()
        scheduler.start_scheduler()
        
        status = scheduler.get_scheduler_status()
        
        return jsonify({
            'success': True,
            'message': 'سرویس زمان‌بندی با موفقیت شروع شد',
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در شروع سرویس زمان‌بندی: {str(e)}'
        }), 500

@app.route('/api/accounting/scheduler/stop', methods=['POST'])
@login_required
def api_accounting_scheduler_stop():
    """توقف سرویس زمان‌بندی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_scheduler_service import get_scheduler
        
        scheduler = get_scheduler()
        scheduler.stop_scheduler()
        
        status = scheduler.get_scheduler_status()
        
        return jsonify({
            'success': True,
            'message': 'سرویس زمان‌بندی با موفقیت متوقف شد',
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در توقف سرویس زمان‌بندی: {str(e)}'
        }), 500

@app.route('/api/accounting/scheduler/status', methods=['GET'])
@login_required
def api_accounting_scheduler_status():
    """دریافت وضعیت سرویس زمان‌بندی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_scheduler_service import get_scheduler
        
        scheduler = get_scheduler()
        status = scheduler.get_scheduler_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت وضعیت سرویس زمان‌بندی: {str(e)}'
        }), 500

@app.route('/api/accounting/sync/prices-to-products', methods=['POST'])
@login_required
def api_accounting_sync_prices_to_products():
    """همگام‌سازی قیمت‌های تدبیر با محصولات محلی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        from tadbir_sync_service import TadbirSyncService
        
        sync_service = TadbirSyncService()
        result = sync_service.sync_prices_to_products()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'همگام‌سازی قیمت‌ها با موفقیت انجام شد. {result["updated_count"]} محصول بروزرسانی شد.',
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'message': f'خطا در همگام‌سازی قیمت‌ها: {result.get("error", "خطای نامشخص")}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در همگام‌سازی قیمت‌ها: {str(e)}'
        }), 500

@app.route('/api/accounting/validate-decimal', methods=['POST'])
@login_required
def api_accounting_validate_decimal():
    """اعتبارسنجی اعداد اعشاری"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'شما دسترسی لازم برای این عملیات را ندارید'
        }), 403
    
    try:
        data = request.get_json()
        value = data.get('value', '')
        
        # Validate decimal input
        try:
            float_value = float(value)
            is_valid = 0 <= float_value <= 100
            formatted_value = f"{float_value:.2f}"
            
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'value': float_value,
                'formatted_value': formatted_value,
                'message': 'عدد معتبر است' if is_valid else 'عدد باید بین 0 تا 100 باشد'
            })
        except ValueError:
            return jsonify({
                'success': False,
                'is_valid': False,
                'message': 'لطفاً عدد معتبر وارد کنید'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در اعتبارسنجی: {str(e)}'
        }), 500


# ==================== POINTS SYSTEM ROUTES ====================

@app.route('/points')
@login_required
def user_points():
    """صفحه امتیازات کاربر"""
    from points_service import PointsService
    
    points_service = PointsService()
    user_points_data = points_service.get_user_points(current_user.id)
    user_transactions = points_service.get_user_transactions(current_user.id)
    available_rewards = points_service.get_available_rewards(current_user.id)
    
    return render_template('points/user_points.html',
                         user_points=user_points_data,
                         transactions=user_transactions,
                         available_rewards=available_rewards)

@app.route('/api/points/user')
@login_required
def api_get_user_points():
    """API دریافت امتیازات کاربر"""
    from points_service import PointsService
    
    points_service = PointsService()
    user_points_data = points_service.get_user_points(current_user.id)
    
    return jsonify({
        'success': True,
        'data': user_points_data
    })

@app.route('/api/points/transactions')
@login_required
def api_get_user_transactions():
    """API دریافت تاریخچه تراکنش‌های امتیازی"""
    from points_service import PointsService
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    points_service = PointsService()
    transactions = points_service.get_user_transactions(current_user.id, page, per_page)
    
    transactions_data = []
    for transaction in transactions.items:
        transactions_data.append({
            'id': transaction.id,
            'points_amount': transaction.points_amount,
            'transaction_type': transaction.transaction_type,
            'source_type': transaction.source_type,
            'description': transaction.description,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
            'expires_at': transaction.expires_at.isoformat() if transaction.expires_at else None
        })
    
    return jsonify({
        'success': True,
        'data': transactions_data,
        'pagination': {
            'page': transactions.page,
            'pages': transactions.pages,
            'per_page': transactions.per_page,
            'total': transactions.total
        }
    })

@app.route('/api/points/level')
@login_required
def api_get_user_level():
    """API دریافت سطح کاربر"""
    from points_service import PointsService
    
    points_service = PointsService()
    user_level = points_service.get_user_level(current_user.id)
    
    return jsonify({
        'success': True,
        'data': user_level
    })

@app.route('/api/rewards')
@login_required
def api_get_available_rewards():
    """API دریافت جوایز قابل استفاده"""
    from points_service import PointsService
    
    points_service = PointsService()
    rewards = points_service.get_available_rewards(current_user.id)
    
    rewards_data = []
    for reward in rewards:
        rewards_data.append({
            'id': reward.id,
            'name': reward.name,
            'name_fa': reward.name_fa,
            'description': reward.description,
            'description_fa': reward.description_fa,
            'points_required': reward.points_required,
            'discount_percentage': reward.discount_percentage,
            'discount_amount': reward.discount_amount,
            'reward_type': reward.reward_type
        })
    
    return jsonify({
        'success': True,
        'data': rewards_data
    })

@app.route('/api/rewards/redeem', methods=['POST'])
@login_required
def api_redeem_reward():
    """API استفاده از جایزه"""
    from points_service import PointsService
    
    data = request.get_json()
    reward_id = data.get('reward_id')
    invoice_id = data.get('invoice_id')
    
    if not reward_id:
        return jsonify({
            'success': False,
            'message': 'شناسه جایزه الزامی است'
        }), 400
    
    points_service = PointsService()
    result = points_service.redeem_reward(current_user.id, reward_id, invoice_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/rewards/history')
@login_required
def api_get_rewards_history():
    """API تاریخچه استفاده از جوایز"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    redemptions = RewardRedemption.query.filter_by(user_id=current_user.id)\
        .order_by(RewardRedemption.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    redemptions_data = []
    for redemption in redemptions.items:
        redemptions_data.append({
            'id': redemption.id,
            'reward_name': redemption.reward.name_fa,
            'points_spent': redemption.points_spent,
            'status': redemption.status,
            'used_at': redemption.used_at.isoformat() if redemption.used_at else None,
            'created_at': redemption.created_at.isoformat() if redemption.created_at else None
        })
    
    return jsonify({
        'success': True,
        'data': redemptions_data,
        'pagination': {
            'page': redemptions.page,
            'pages': redemptions.pages,
            'per_page': redemptions.per_page,
            'total': redemptions.total
        }
    })

# ==================== ADMIN POINTS SYSTEM ROUTES ====================

@app.route('/admin/points')
@login_required
def admin_points_dashboard():
    """داشبورد مدیریت امتیازات"""
    if not current_user.is_admin:
        abort(403)
    
    from points_service import PointsService, PointsAnalytics
    
    points_service = PointsService()
    analytics = PointsAnalytics()
    
    # آمار کلی
    statistics = analytics.get_points_statistics()
    top_users = analytics.get_top_users_by_points(10)
    points_trend = analytics.get_points_trend(30)
    
    return render_template('admin/points/dashboard.html',
                         statistics=statistics,
                         top_users=top_users,
                         points_trend=points_trend)

@app.route('/admin/points/users')
@login_required
def admin_points_users():
    """مدیریت امتیازات کاربران"""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # فیلترها
    search = request.args.get('search', '')
    min_points = request.args.get('min_points', type=int)
    max_points = request.args.get('max_points', type=int)
    
    # ساخت کوئری
    query = db.session.query(UserPoints, User).join(User, UserPoints.user_id == User.id)
    
    if search:
        query = query.filter(
            models.db.or_(
                User.username.contains(search),
                User.full_name.contains(search),
                User.company_name.contains(search)
            )
        )
    
    if min_points is not None:
        query = query.filter(UserPoints.current_points >= min_points)
    
    if max_points is not None:
        query = query.filter(UserPoints.current_points <= max_points)
    
    users = query.order_by(UserPoints.current_points.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/points/users.html', users=users)

@app.route('/admin/points/adjust', methods=['POST'])
@login_required
def admin_adjust_user_points():
    """تنظیم دستی امتیازات کاربر"""
    if not current_user.is_admin:
        abort(403)
    
    user_id = request.form.get('user_id', type=int)
    points_amount = request.form.get('points_amount', type=int)
    description = request.form.get('description', '')
    
    if not user_id or points_amount is None:
        flash('تمام فیلدها الزامی است.', 'error')
        return redirect(url_for('admin_points_users'))
    
    from points_service import PointsService
    points_service = PointsService()
    
    result = points_service.adjust_user_points(
        user_id, points_amount, description, current_user.id
    )
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin_points_users'))

@app.route('/admin/rewards')
@login_required
def admin_rewards():
    """مدیریت جوایز"""
    if not current_user.is_admin:
        abort(403)
    
    rewards = Reward.query.order_by(Reward.created_at.desc()).all()
    return render_template('admin/points/rewards.html', rewards=rewards)

@app.route('/admin/rewards/add', methods=['POST'])
@login_required
def admin_add_reward():
    """اضافه کردن جایزه جدید"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        name = request.form.get('name', '').strip()
        name_fa = request.form.get('name_fa', '').strip()
        description = request.form.get('description', '').strip()
        description_fa = request.form.get('description_fa', '').strip()
        points_required = request.form.get('points_required', type=int)
        reward_type = request.form.get('reward_type', '')
        discount_percentage = request.form.get('discount_percentage', type=float)
        discount_amount = request.form.get('discount_amount', type=float)
        max_redemptions = request.form.get('max_redemptions', type=int)
        valid_from = request.form.get('valid_from', '')
        valid_until = request.form.get('valid_until', '')
        is_active = request.form.get('is_active') == 'on'
        
        # اعتبارسنجی
        if not name or not name_fa or not points_required:
            flash('نام، نام فارسی و امتیاز مورد نیاز الزامی است.', 'error')
            return redirect(url_for('admin_rewards'))
        
        # تبدیل تاریخ‌ها
        valid_from_date = None
        valid_until_date = None
        
        if valid_from:
            try:
                valid_from_date = datetime.strptime(valid_from, '%Y-%m-%d')
            except ValueError:
                flash('فرمت تاریخ شروع صحیح نیست.', 'error')
                return redirect(url_for('admin_rewards'))
        
        if valid_until:
            try:
                valid_until_date = datetime.strptime(valid_until, '%Y-%m-%d')
            except ValueError:
                flash('فرمت تاریخ پایان صحیح نیست.', 'error')
                return redirect(url_for('admin_rewards'))
        
        # ایجاد جایزه
        reward = Reward(
            name=name,
            name_fa=name_fa,
            description=description,
            description_fa=description_fa,
            points_required=points_required,
            reward_type=reward_type,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            max_redemptions=max_redemptions,
            valid_from=valid_from_date,
            valid_until=valid_until_date,
            is_active=is_active
        )
        
        models.db.session.add(reward)
        models.db.session.commit()
        
        flash(f'جایزه "{name_fa}" با موفقیت اضافه شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در افزودن جایزه. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_rewards'))

@app.route('/admin/rewards/edit/<int:reward_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_reward(reward_id):
    """ویرایش جایزه"""
    if not current_user.is_admin:
        abort(403)
    
    reward = Reward.query.get_or_404(reward_id)
    
    if request.method == 'POST':
        try:
            reward.name = request.form.get('name', '').strip()
            reward.name_fa = request.form.get('name_fa', '').strip()
            reward.description = request.form.get('description', '').strip()
            reward.description_fa = request.form.get('description_fa', '').strip()
            reward.points_required = request.form.get('points_required', type=int)
            reward.reward_type = request.form.get('reward_type', '')
            reward.discount_percentage = request.form.get('discount_percentage', type=float)
            reward.discount_amount = request.form.get('discount_amount', type=float)
            reward.max_redemptions = request.form.get('max_redemptions', type=int)
            reward.is_active = request.form.get('is_active') == 'on'
            
            # تبدیل تاریخ‌ها
            valid_from = request.form.get('valid_from', '')
            valid_until = request.form.get('valid_until', '')
            
            if valid_from:
                try:
                    reward.valid_from = datetime.strptime(valid_from, '%Y-%m-%d')
                except ValueError:
                    reward.valid_from = None
            else:
                reward.valid_from = None
            
            if valid_until:
                try:
                    reward.valid_until = datetime.strptime(valid_until, '%Y-%m-%d')
                except ValueError:
                    reward.valid_until = None
            else:
                reward.valid_until = None
            
            models.db.session.commit()
            
            flash(f'جایزه "{reward.name_fa}" با موفقیت به‌روزرسانی شد.', 'success')
            return redirect(url_for('admin_rewards'))
            
        except Exception as e:
            models.db.session.rollback()
            flash('خطا در به‌روزرسانی جایزه. لطفاً دوباره تلاش کنید.', 'error')
    
    return render_template('admin/points/edit_reward.html', reward=reward)

@app.route('/admin/rewards/delete/<int:reward_id>', methods=['POST'])
@login_required
def admin_delete_reward(reward_id):
    """حذف جایزه"""
    if not current_user.is_admin:
        abort(403)
    
    reward = Reward.query.get_or_404(reward_id)
    reward_name = reward.name_fa
    
    try:
        # بررسی استفاده از جایزه
        if reward.redemptions:
            flash(f'نمی‌توان جایزه "{reward_name}" را حذف کرد زیرا استفاده شده است.', 'error')
            return redirect(url_for('admin_rewards'))
        
        models.db.session.delete(reward)
        models.db.session.commit()
        
        flash(f'جایزه "{reward_name}" با موفقیت حذف شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در حذف جایزه. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_rewards'))

@app.route('/admin/points/rules')
@login_required
def admin_points_rules():
    """مدیریت قوانین امتیازدهی"""
    if not current_user.is_admin:
        abort(403)
    
    rules = PointsRule.query.order_by(PointsRule.created_at.desc()).all()
    return render_template('admin/points/rules.html', rules=rules)

@app.route('/admin/points/rules/add', methods=['POST'])
@login_required
def admin_add_points_rule():
    """اضافه کردن قانون امتیازدهی جدید"""
    if not current_user.is_admin:
        abort(403)
    
    try:
        rule_name = request.form.get('rule_name', '').strip()
        rule_name_fa = request.form.get('rule_name_fa', '').strip()
        points_per_100k_rials = request.form.get('points_per_100k_rials', type=int)
        bonus_points_per_product = request.form.get('bonus_points_per_product', type=int)
        max_bonus_points = request.form.get('max_bonus_points', type=int)
        is_active = request.form.get('is_active') == 'on'
        
        # اعتبارسنجی
        if not rule_name or not rule_name_fa or not points_per_100k_rials:
            flash('نام قانون، نام فارسی و امتیاز به ازای هر 100 هزار ریال الزامی است.', 'error')
            return redirect(url_for('admin_points_rules'))
        
        # ایجاد قانون
        rule = PointsRule(
            rule_name=rule_name,
            rule_name_fa=rule_name_fa,
            points_per_100k_rials=points_per_100k_rials,
            bonus_points_per_product=bonus_points_per_product,
            max_bonus_points=max_bonus_points,
            is_active=is_active
        )
        
        models.db.session.add(rule)
        models.db.session.commit()
        
        flash(f'قانون "{rule_name_fa}" با موفقیت اضافه شد.', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در افزودن قانون. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('admin_points_rules'))

@app.route('/admin/points/analytics')
@login_required
def admin_points_analytics():
    """آمار و تحلیل سیستم امتیازدهی"""
    if not current_user.is_admin:
        abort(403)
    
    from points_service import PointsAnalytics
    
    analytics = PointsAnalytics()
    statistics = analytics.get_points_statistics()
    top_users = analytics.get_top_users_by_points(20)
    points_trend = analytics.get_points_trend(90)
    
    return render_template('admin/points/analytics.html',
                         statistics=statistics,
                         top_users=top_users,
                         points_trend=points_trend)

@app.route('/admin/points/expire', methods=['POST'])
@login_required
def admin_expire_points():
    """انقضای امتیازات قدیمی"""
    if not current_user.is_admin:
        abort(403)
    
    from points_service import PointsService
    
    points_service = PointsService()
    result = points_service.expire_old_points()
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin_points_dashboard'))

# ==================== STATIC FILES ====================

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== ROLE MANAGEMENT API ROUTES ====================

@app.route('/api/v1/roles', methods=['GET'])
@login_required
def api_get_roles():
    """Get all roles"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        roles = Role.query.all()
        roles_data = []
        for role in roles:
            roles_data.append({
                'id': role.id,
                'slug': role.slug,
                'name': role.name,
                'description': role.description,
                'permissions': role.get_permissions(),
                'scope': role.scope,
                'is_active': role.is_active,
                'is_immutable': role.is_immutable,
                'created_at': role.created_at.isoformat() if role.created_at else None,
                'updated_at': role.updated_at.isoformat() if role.updated_at else None
            })
        
        return jsonify({'roles': roles_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/roles', methods=['POST'])
@login_required
def api_create_role():
    """Create a new role"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        role_data = data.get('role', {})
        audit_reason = data.get('audit_reason', 'Creating new role')
        
        # Validate required fields
        required_fields = ['slug', 'name']
        for field in required_fields:
            if not role_data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if role with same slug already exists
        existing_role = Role.query.filter_by(slug=role_data['slug']).first()
        if existing_role:
            return jsonify({'error': 'Role with this slug already exists'}), 400
        
        # Create new role
        new_role = Role(
            slug=role_data['slug'],
            name=role_data['name'],
            description=role_data.get('description', ''),
            scope=role_data.get('scope', 'site'),
            is_active=role_data.get('is_active', True),
            is_immutable=role_data.get('is_immutable', False)
        )
        
        # Set permissions
        permissions = role_data.get('permissions', [])
        new_role.set_permissions(permissions)
        
        db.session.add(new_role)
        db.session.commit()
        
        # Log the action
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action='role.create',
                resource_type='role',
                resource_id=new_role.id,
                details={
                    'role_slug': new_role.slug,
                    'role_name': new_role.name,
                    'permissions': permissions,
                    'scope': new_role.scope
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                request_id=request.headers.get('X-Request-ID', ''),
                reason=audit_reason
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            # Don't fail the role creation if audit logging fails
            print(f"Audit logging failed: {e}")
        
        return jsonify({
            'message': 'Role created successfully',
            'role': {
                'id': new_role.id,
                'slug': new_role.slug,
                'name': new_role.name,
                'description': new_role.description,
                'permissions': new_role.get_permissions(),
                'scope': new_role.scope,
                'is_active': new_role.is_active,
                'is_immutable': new_role.is_immutable
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/roles/<int:role_id>', methods=['PUT'])
@login_required
def api_update_role(role_id):
    """Update a role"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        role = Role.query.get_or_404(role_id)
        
        # Check if role is immutable
        if role.is_immutable:
            return jsonify({'error': 'Cannot modify immutable role'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        role_data = data.get('role', {})
        audit_reason = data.get('audit_reason', 'Updating role')
        
        # Update fields
        if 'name' in role_data:
            role.name = role_data['name']
        if 'description' in role_data:
            role.description = role_data['description']
        if 'scope' in role_data:
            role.scope = role_data['scope']
        if 'is_active' in role_data:
            role.is_active = role_data['is_active']
        if 'permissions' in role_data:
            role.set_permissions(role_data['permissions'])
        
        role.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the action
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action='role.update',
                resource_type='role',
                resource_id=role.id,
                details={
                    'role_slug': role.slug,
                    'role_name': role.name,
                    'permissions': role.get_permissions(),
                    'scope': role.scope
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                request_id=request.headers.get('X-Request-ID', ''),
                reason=audit_reason
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            print(f"Audit logging failed: {e}")
        
        return jsonify({
            'message': 'Role updated successfully',
            'role': {
                'id': role.id,
                'slug': role.slug,
                'name': role.name,
                'description': role.description,
                'permissions': role.get_permissions(),
                'scope': role.scope,
                'is_active': role.is_active,
                'is_immutable': role.is_immutable
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/roles/<int:role_id>', methods=['DELETE'])
@login_required
def api_delete_role(role_id):
    """Delete a role"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        role = Role.query.get_or_404(role_id)
        
        # Check if role is immutable
        if role.is_immutable:
            return jsonify({'error': 'Cannot delete immutable role'}), 400
        
        # Check if role is assigned to any users
        if role.user_roles:
            return jsonify({'error': 'Cannot delete role that is assigned to users'}), 400
        
        audit_reason = request.json.get('audit_reason', 'Deleting role') if request.json else 'Deleting role'
        
        # Log the action before deletion
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action='role.delete',
                resource_type='role',
                resource_id=role.id,
                details={
                    'role_slug': role.slug,
                    'role_name': role.name
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                request_id=request.headers.get('X-Request-ID', ''),
                reason=audit_reason
            )
            db.session.add(audit_log)
        except Exception as e:
            print(f"Audit logging failed: {e}")
        
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({'message': 'Role deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== USER ROLE MANAGEMENT API ROUTES ====================

@app.route('/api/v1/users/<int:user_id>/roles', methods=['GET'])
@login_required
def api_get_user_roles(user_id):
    """Get roles assigned to a user"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        roles = [
            {
                'role_slug': ur.role.slug,
                'role_name': ur.role.name,
                'scope': ur.scope,
                'is_active': ur.is_active,
                'assigned_at': ur.assigned_at.isoformat() if ur.assigned_at else None,
            }
            for ur in user.user_roles
        ]
        return jsonify({'user_id': user.id, 'roles': roles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/users/<int:user_id>/roles', methods=['POST'])
@login_required
def api_assign_role(user_id):
    """Assign a role to a user"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        payload = request.get_json() or {}
        role_slug = payload.get('role_slug')
        scope = payload.get('scope', 'site')
        audit_reason = payload.get('audit_reason', 'Assign role')

        if not role_slug:
            return jsonify({'error': 'role_slug is required'}), 400

        user = User.query.get_or_404(user_id)
        role = Role.query.filter_by(slug=role_slug).first()
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        user.assign_role(role=role, assigned_by=current_user.id, scope=scope)
        db.session.commit()

        # Audit log
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action='role.assign',
                resource_type='user_role',
                resource_id=user.id,
                details={
                    'assigned_to_user_id': user.id,
                    'role_slug': role.slug,
                    'scope': scope
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                request_id=request.headers.get('X-Request-ID', ''),
                reason=audit_reason
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception:
            pass

        return jsonify({'message': 'Role assigned successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/users/<int:user_id>/roles/<role_slug>', methods=['DELETE'])
@login_required
def api_revoke_role(user_id, role_slug):
    """Revoke a role from a user"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        payload = request.get_json() or {}
        scope = payload.get('scope', 'site')
        audit_reason = payload.get('audit_reason', 'Revoke role')

        user = User.query.get_or_404(user_id)
        user.revoke_role(role_slug=role_slug, scope=scope)
        db.session.commit()

        # Audit log
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action='role.revoke',
                resource_type='user_role',
                resource_id=user.id,
                details={
                    'revoked_from_user_id': user.id,
                    'role_slug': role_slug,
                    'scope': scope
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                request_id=request.headers.get('X-Request-ID', ''),
                reason=audit_reason
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception:
            pass

        return jsonify({'message': 'Role revoked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

# ==================== INVOICE MANAGEMENT ROUTES ====================

@app.route('/admin/invoices/<int:invoice_id>/approve', methods=['POST'])
@login_required
def admin_approve_invoice_with_notification(invoice_id):
    """تایید فاکتور با ارسال اطلاع‌رسانی"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        if invoice.approval_status != 'pending':
            flash('فاکتور در وضعیت قابل تایید نیست', 'error')
            return redirect(url_for('admin_invoice_management'))
        
        # Get form data
        admin_notes = request.form.get('admin_notes', '')
        send_notification = request.form.get('send_notification') == 'on'
        
        # Update invoice
        invoice.approval_status = 'approved'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        invoice.admin_notes = admin_notes
        
        # Send notification if requested
        if send_notification:
            from invoice_notification_service import InvoiceNotificationService
            InvoiceNotificationService.send_approval_notification(invoice_id, admin_notes)
        
        models.db.session.commit()
        flash('فاکتور با موفقیت تایید شد', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در تایید فاکتور', 'error')
        print(f"Error approving invoice: {str(e)}")
    
    return redirect(url_for('admin_invoice_management'))

@app.route('/admin/invoices/<int:invoice_id>/reject', methods=['POST'])
@login_required
def admin_reject_invoice_with_notification(invoice_id):
    """رد فاکتور با ارسال اطلاع‌رسانی"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        if invoice.approval_status != 'pending':
            flash('فاکتور در وضعیت قابل رد نیست', 'error')
            return redirect(url_for('admin_invoice_management'))
        
        # Get form data
        rejection_reason = request.form.get('rejection_reason', '')
        admin_notes = request.form.get('admin_notes', '')
        send_notification = request.form.get('send_notification') == 'on'
        
        if not rejection_reason:
            flash('دلیل رد فاکتور الزامی است', 'error')
            return redirect(url_for('admin_invoice_management'))
        
        # Update invoice
        invoice.approval_status = 'rejected'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        invoice.rejection_reason = rejection_reason
        invoice.admin_notes = admin_notes
        
        # Send notification if requested
        if send_notification:
            from invoice_notification_service import InvoiceNotificationService
            InvoiceNotificationService.send_rejection_notification(invoice_id, rejection_reason, admin_notes)
        
        models.db.session.commit()
        flash('فاکتور با موفقیت رد شد', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در رد فاکتور', 'error')
        print(f"Error rejecting invoice: {str(e)}")
    
    return redirect(url_for('admin_invoice_management'))

@app.route('/admin/invoices/<int:invoice_id>/set-review', methods=['POST'])
@login_required
def admin_set_invoice_review(invoice_id):
    """تنظیم فاکتور به حالت بررسی"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        if invoice.approval_status != 'pending':
            flash('فاکتور در وضعیت قابل بررسی نیست', 'error')
            return redirect(url_for('admin_invoice_management'))
        
        # Get form data
        admin_notes = request.form.get('admin_notes', '')
        
        # Update invoice
        invoice.approval_status = 'under_review'
        invoice.approval_date = datetime.utcnow()
        invoice.approved_by = current_user.id
        invoice.admin_review_notes = admin_notes
        
        # Send notification
        from invoice_notification_service import InvoiceNotificationService
        InvoiceNotificationService.send_review_notification(invoice_id, admin_notes)
        
        models.db.session.commit()
        flash('فاکتور به حالت بررسی تنظیم شد', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در تنظیم فاکتور به حالت بررسی', 'error')
        print(f"Error setting invoice review: {str(e)}")
    
    return redirect(url_for('admin_invoice_management'))

@app.route('/admin/invoices/<int:invoice_id>/documents')
@login_required
def admin_view_invoice_documents(invoice_id):
    """مشاهده مستندات فاکتور"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('admin/invoice_documents_viewer.html', invoice=invoice)

@app.route('/admin/invoices/<int:invoice_id>/documents/<int:document_id>/approve', methods=['POST'])
@login_required
def admin_approve_invoice_document(invoice_id, document_id):
    """تایید مستند فاکتور"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    try:
        document = InvoiceDocument.query.get_or_404(document_id)
        
        if document.invoice_id != invoice_id:
            flash('مستند متعلق به این فاکتور نیست', 'error')
            return redirect(url_for('admin_invoice_management'))
        
        # Update document
        document.is_approved = True
        document.approval_date = datetime.utcnow()
        document.approved_by = current_user.id
        
        models.db.session.commit()
        flash('مستند با موفقیت تایید شد', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در تایید مستند', 'error')
        print(f"Error approving document: {str(e)}")
    
    return redirect(url_for('admin_view_invoice_documents', invoice_id=invoice_id))

@app.route('/admin/invoices/<int:invoice_id>/documents/<int:document_id>/reject', methods=['POST'])
@login_required
def admin_reject_invoice_document(invoice_id, document_id):
    """رد مستند فاکتور"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        abort(403)
    
    try:
        document = InvoiceDocument.query.get_or_404(document_id)
        
        if document.invoice_id != invoice_id:
            flash('مستند متعلق به این فاکتور نیست', 'error')
            return redirect(url_for('admin_invoice_management'))
        
        # Get form data
        rejection_reason = request.form.get('rejection_reason', '')
        
        if not rejection_reason:
            flash('دلیل رد مستند الزامی است', 'error')
            return redirect(url_for('admin_view_invoice_documents', invoice_id=invoice_id))
        
        # Update document
        document.is_approved = False
        document.rejection_reason = rejection_reason
        document.approved_by = current_user.id
        
        models.db.session.commit()
        flash('مستند رد شد', 'success')
        
    except Exception as e:
        models.db.session.rollback()
        flash('خطا در رد مستند', 'error')
        print(f"Error rejecting document: {str(e)}")
    
    return redirect(url_for('admin_view_invoice_documents', invoice_id=invoice_id))

@app.route('/api/admin/invoices/statistics')
@login_required
def api_invoice_statistics():
    """دریافت آمار فاکتورها به صورت JSON"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        all_invoices = Invoice.query.all()
        
        stats = {
            'total_invoices': len(all_invoices),
            'pending_approval': len([i for i in all_invoices if i.approval_status == 'pending']),
            'approved': len([i for i in all_invoices if i.approval_status == 'approved']),
            'rejected': len([i for i in all_invoices if i.approval_status == 'rejected']),
            'under_review': len([i for i in all_invoices if i.approval_status == 'under_review']),
            'total_amount': sum(i.total_amount for i in all_invoices) / 1000000,  # Convert to millions
            'cash_invoices': len([i for i in all_invoices if i.payment_type == 'cash']),
            'check_invoices': len([i for i in all_invoices if i.payment_type == 'check'])
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/invoices/search')
@login_required
def api_invoice_search():
    """جستجوی پیشرفته فاکتورها"""
    if not (current_user.is_admin or current_user.has_role('مدیر_سفارشات', scope='site')):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get search parameters
        approval_status = request.args.get('approval_status', '')
        payment_type = request.args.get('payment_type', '')
        user_search = request.args.get('user_search', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        amount_min = request.args.get('amount_min', type=float)
        amount_max = request.args.get('amount_max', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Invoice.query.join(User, Invoice.user_id == User.id)
        
        if approval_status:
            query = query.filter_by(approval_status=approval_status)
        
        if payment_type:
            query = query.filter_by(payment_type=payment_type)
        
        if user_search:
            query = query.filter(
                models.db.or_(
                    User.username.contains(user_search),
                    User.full_name.contains(user_search),
                    User.company_name.contains(user_search)
                )
            )
        
        if date_from:
            query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        
        if date_to:
            query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        if amount_min:
            query = query.filter(Invoice.total_amount >= amount_min * 1000)
        
        if amount_max:
            query = query.filter(Invoice.total_amount <= amount_max * 1000)
        
        # Paginate results
        invoices = query.order_by(Invoice.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Convert to JSON
        invoices_data = []
        for invoice in invoices.items:
            invoice_data = {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer_name': invoice.user.full_name,
                'customer_company': invoice.user.company_name,
                'total_amount': invoice.total_amount,
                'payment_type': invoice.payment_type,
                'approval_status': invoice.approval_status,
                'created_at': invoice.created_at.isoformat(),
                'approval_date': invoice.approval_date.isoformat() if invoice.approval_date else None
            }
            invoices_data.append(invoice_data)
        
        return jsonify({
            'invoices': invoices_data,
            'total': invoices.total,
            'pages': invoices.pages,
            'current_page': invoices.page,
            'has_next': invoices.has_next,
            'has_prev': invoices.has_prev
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# ========================================
# Health Check Endpoint
# ========================================

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Check Redis connection (if available)
    redis_status = 'not_configured'
    try:
        import redis
        r = redis.Redis(host='redis', port=6379, db=0, socket_connect_timeout=5)
        r.ping()
        redis_status = 'healthy'
    except Exception as e:
        redis_status = f'unhealthy: {str(e)}'
    
    # System metrics
    system_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': time.time(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }
    
    # Overall health status
    overall_status = 'healthy'
    if db_status != 'healthy':
        overall_status = 'unhealthy'
    
    health_data = {
        'status': overall_status,
        'version': '1.0.0',
        'services': {
            'database': db_status,
            'redis': redis_status
        },
        'system': system_info
    }
    
    # Return appropriate HTTP status code
    status_code = 200 if overall_status == 'healthy' else 503
    
    return jsonify(health_data), status_code

@app.route('/health/ready')
def readiness_check():
    """Readiness check for Kubernetes/Docker health checks"""
    try:
        # Check if database is accessible
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ready'}), 200
    except Exception:
        return jsonify({'status': 'not_ready'}), 503

@app.route('/health/live')
def liveness_check():
    """Liveness check for Kubernetes/Docker health checks"""
    return jsonify({'status': 'alive'}), 200
