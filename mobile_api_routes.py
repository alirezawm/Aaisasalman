"""
Mobile API Routes for Android Application
All endpoints are prefixed with /api/mobile/v1
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_, and_, func
from datetime import datetime
from models import *
from app import app
import models
import json

# Import helper functions from routes
from routes import normalize_fa_text, advanced_product_search

# Helper function to get current user from JWT
def get_current_user():
    """Get current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(user_id)
    except:
        pass
    return None

# Helper function to serialize product for mobile API
def serialize_product_for_mobile(product, user=None):
    """Serialize product data for mobile API response"""
    from app import can_see_bulk_prices, format_price
    
    # Calculate prices (convert from thousands to full Rials)
    price_cash = int(product.retail_price_cash * 1000) if product.retail_price_cash else 0
    price_check = int(product.retail_price_check * 1000) if product.retail_price_check else 0
    
    # Bulk prices if user can see them
    price_cash_bulk = None
    price_check_bulk = None
    if user and can_see_bulk_prices(user):
        price_cash_bulk = int(product.bulk_price_cash * 1000) if product.bulk_price_cash else None
        price_check_bulk = int(product.bulk_price_check * 1000) if product.bulk_price_check else None
    
    # Check for active discounts
    discount_percentage = None
    discounted_price_cash = None
    discounted_price_check = None
    
    if product.discounts:
        for discount in product.discounts:
            if discount.is_valid():
                discount_percentage = discount.discount_percentage
                discounted_price_cash = int(price_cash * (1 - discount_percentage / 100))
                discounted_price_check = int(price_check * (1 - discount_percentage / 100))
                break  # Use first valid discount
    
    # Parse images
    images = []
    if product.images:
        try:
            images = json.loads(product.images)
        except:
            pass
    if product.primary_image:
        if product.primary_image not in images:
            images.insert(0, product.primary_image)
    
    return {
        'id': product.id,
        'name': product.name,
        'name_fa': product.name_fa,
        'sku': product.sku,
        'oem_code': product.oem_code or '',
        'description': product.description or '',
        'description_fa': product.description_fa or '',
        'image_url': product.primary_image or '',
        'images': images,
        'price_cash': price_cash,
        'price_check': price_check,
        'price_cash_bulk': price_cash_bulk,
        'price_check_bulk': price_check_bulk,
        'discount_percentage': discount_percentage,
        'discounted_price_cash': discounted_price_cash,
        'discounted_price_check': discounted_price_check,
        'stock_quantity': product.stock_quantity,
        'is_active': product.is_active,
        'brand': {
            'id': product.brand.id if product.brand else None,
            'name': product.brand.name if product.brand else '',
            'name_fa': product.brand.name_fa if product.brand else '',
            'logo_url': product.brand.logo_url if product.brand else ''
        } if product.brand else None,
        'category': {
            'id': product.category.id if product.category else None,
            'name': product.category.category_name if product.category else '',
            'name_fa': product.category.category_name_fa if product.category else ''
        } if product.category else None,
        'vehicle_type': {
            'id': product.vehicle_types[0].id if product.vehicle_types else None,
            'name': product.vehicle_types[0].name if product.vehicle_types else '',
            'name_fa': product.vehicle_types[0].name if product.vehicle_types else ''
        } if product.vehicle_types else None,
        'product_type': None  # Can be added if needed
    }

# ==================== PRODUCTS API ====================

@app.route('/api/mobile/v1/products', methods=['GET'])
def mobile_products_list():
    """Mobile API: Get products list"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        brand_id = request.args.get('brand_id', type=int)
        category_id = request.args.get('category_id', type=int)
        vehicle_type_id = request.args.get('vehicle_type_id', type=int)
        product_type_id = request.args.get('product_type_id', type=int)
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        in_stock = request.args.get('in_stock', type=bool)
        has_discount = request.args.get('has_discount', type=bool)
        search = request.args.get('search', '').strip()
        
        # Get current user (optional)
        user = get_current_user()
        
        # Build query
        query = Product.query.filter_by(is_active=True)
        
        # Apply filters
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if vehicle_type_id:
            query = query.join(ProductVehicleType).filter(
                ProductVehicleType.vehicle_type_id == vehicle_type_id
            )
        if min_price:
            # Convert from full Rials to thousands
            min_price_thousands = min_price / 1000
            query = query.filter(Product.retail_price_cash >= min_price_thousands)
        if max_price:
            max_price_thousands = max_price / 1000
            query = query.filter(Product.retail_price_cash <= max_price_thousands)
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        if has_discount:
            query = query.join(ProductDiscountProduct).join(ProductDiscount).filter(
                ProductDiscount.is_active == True
            )
        if search:
            search_normalized = normalize_fa_text(search)
            query = query.filter(
                or_(
                    Product.name.contains(search_normalized),
                    Product.name_fa.contains(search_normalized),
                    Product.sku.contains(search),
                    Product.oem_code.contains(search)
                )
            )
        
        # Order by
        query = query.order_by(Product.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Serialize products
        products_data = [serialize_product_for_mobile(p, user) for p in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_products_list: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت لیست محصولات'
        }), 500

@app.route('/api/mobile/v1/products/<int:product_id>', methods=['GET'])
def mobile_product_detail(product_id):
    """Mobile API: Get product detail"""
    try:
        user = get_current_user()
        
        product = Product.query.get_or_404(product_id)
        
        if not product.is_active:
            return jsonify({
                'success': False,
                'message': 'محصول یافت نشد'
            }), 404
        
        product_data = serialize_product_for_mobile(product, user)
        
        # Add related products
        related_products = Product.query.filter(
            Product.brand_id == product.brand_id,
            Product.id != product.id,
            Product.is_active == True,
            Product.stock_quantity > 0
        ).limit(10).all()
        
        product_data['related_products'] = [serialize_product_for_mobile(p, user) for p in related_products]
        
        return jsonify({
            'success': True,
            'data': {
                'product': product_data
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_product_detail: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت جزئیات محصول'
        }), 500

@app.route('/api/mobile/v1/products/search', methods=['GET'])
def mobile_products_search():
    """Mobile API: Search products"""
    try:
        search_query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not search_query:
            return jsonify({
                'success': False,
                'message': 'عبارت جستجو الزامی است'
            }), 400
        
        user = get_current_user()
        
        # Use advanced search
        query = Product.query.filter_by(is_active=True)
        query = advanced_product_search(query, search_query)
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Serialize products
        products_data = [serialize_product_for_mobile(p, user) for p in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_products_search: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در جستجو'
        }), 500

@app.route('/api/mobile/v1/products/filters', methods=['GET'])
def mobile_products_filters():
    """Mobile API: Get product filters"""
    try:
        # Get all active brands
        brands = Brand.query.filter_by(is_active=True).all()
        brands_data = [{
            'id': b.id,
            'name': b.name,
            'name_fa': b.name_fa,
            'logo_url': b.logo_url or ''
        } for b in brands]
        
        # Get all active categories
        categories = PartCategory.query.filter_by(is_active=True).all()
        categories_data = [{
            'id': c.id,
            'name': c.category_name,
            'name_fa': c.category_name_fa
        } for c in categories]
        
        # Get all active vehicle types
        vehicle_types = VehicleType.query.filter_by(is_active=True).all()
        vehicle_types_data = [{
            'id': vt.id,
            'name': vt.name,
            'name_fa': vt.name
        } for vt in vehicle_types]
        
        # Get price range
        min_price_result = models.db.session.query(func.min(Product.retail_price_cash)).filter(
            Product.is_active == True
        ).scalar()
        max_price_result = models.db.session.query(func.max(Product.retail_price_cash)).filter(
            Product.is_active == True
        ).scalar()
        
        price_range = {
            'min': int(min_price_result * 1000) if min_price_result else 0,
            'max': int(max_price_result * 1000) if max_price_result else 0
        }
        
        return jsonify({
            'success': True,
            'data': {
                'brands': brands_data,
                'categories': categories_data,
                'vehicle_types': vehicle_types_data,
                'product_types': [],  # Can be added if needed
                'price_range': price_range
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_products_filters: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت فیلترها'
        }), 500

# ==================== CATEGORIES API ====================

@app.route('/api/mobile/v1/categories', methods=['GET'])
def mobile_categories_list():
    """Mobile API: Get categories list"""
    try:
        categories = PartCategory.query.filter_by(is_active=True).all()
        categories_data = [{
            'id': c.id,
            'name': c.category_name,
            'name_fa': c.category_name_fa,
            'description': c.description or '',
            'description_fa': c.description_fa or ''
        } for c in categories]
        
        return jsonify({
            'success': True,
            'data': {
                'categories': categories_data
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_categories_list: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت دسته‌بندی‌ها'
        }), 500

@app.route('/api/mobile/v1/categories/vehicle-based', methods=['GET'])
def mobile_categories_vehicle_based():
    """Mobile API: Get categories grouped by vehicle type"""
    try:
        vehicle_types = VehicleType.query.filter_by(is_active=True).all()
        user = get_current_user()
        
        result = []
        for vt in vehicle_types:
            # Get products for this vehicle type
            products = Product.query.join(ProductVehicleType).filter(
                ProductVehicleType.vehicle_type_id == vt.id,
                Product.is_active == True,
                Product.stock_quantity > 0
            ).all()
            
            # Get unique categories from products
            category_ids = set()
            for p in products:
                if p.category_id:
                    category_ids.add(p.category_id)
            
            categories = PartCategory.query.filter(
                PartCategory.id.in_(category_ids),
                PartCategory.is_active == True
            ).all()
            
            result.append({
                'id': vt.id,
                'name': vt.name,
                'name_fa': vt.name,
                'icon_url': vt.image or '',
                'categories': [{
                    'id': c.id,
                    'name': c.category_name,
                    'name_fa': c.category_name_fa
                } for c in categories]
            })
        
        return jsonify({
            'success': True,
            'data': {
                'vehicle_types': result
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_categories_vehicle_based: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت دسته‌بندی‌ها'
        }), 500

@app.route('/api/mobile/v1/categories/brand-based', methods=['GET'])
def mobile_categories_brand_based():
    """Mobile API: Get categories grouped by brand"""
    try:
        brands = Brand.query.filter_by(is_active=True).all()
        user = get_current_user()
        
        result = []
        for brand in brands:
            # Get products for this brand
            products = Product.query.filter(
                Product.brand_id == brand.id,
                Product.is_active == True,
                Product.stock_quantity > 0
            ).all()
            
            # Get unique categories from products
            category_ids = set()
            for p in products:
                if p.category_id:
                    category_ids.add(p.category_id)
            
            categories = PartCategory.query.filter(
                PartCategory.id.in_(category_ids),
                PartCategory.is_active == True
            ).all()
            
            result.append({
                'id': brand.id,
                'name': brand.name,
                'name_fa': brand.name_fa,
                'logo_url': brand.logo_url or '',
                'categories': [{
                    'id': c.id,
                    'name': c.category_name,
                    'name_fa': c.category_name_fa
                } for c in categories]
            })
        
        return jsonify({
            'success': True,
            'data': {
                'brands': result
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_categories_brand_based: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت دسته‌بندی‌ها'
        }), 500

@app.route('/api/mobile/v1/categories/<int:category_id>/products', methods=['GET'])
def mobile_category_products(category_id):
    """Mobile API: Get products in a category"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        category = PartCategory.query.get_or_404(category_id)
        user = get_current_user()
        
        query = Product.query.filter_by(
            category_id=category_id,
            is_active=True
        ).order_by(Product.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        products_data = [serialize_product_for_mobile(p, user) for p in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_category_products: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت محصولات'
        }), 500

# ==================== DISCOUNTS API ====================

@app.route('/api/mobile/v1/discounts/daily-products', methods=['GET'])
def mobile_discounts_daily_products():
    """Mobile API: Get daily discount products"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        user = get_current_user()
        
        # Get active daily discounts
        now = datetime.utcnow()
        discounts = ProductDiscount.query.filter(
            ProductDiscount.discount_type == 'daily',
            ProductDiscount.is_active == True,
            or_(
                ProductDiscount.start_date.is_(None),
                ProductDiscount.start_date <= now
            ),
            or_(
                ProductDiscount.end_date.is_(None),
                ProductDiscount.end_date >= now
            )
        ).order_by(ProductDiscount.priority.desc(), ProductDiscount.created_at.desc()).all()
        
        # Collect all products from active discounts
        products_dict = {}
        for discount in discounts:
            for product in discount.products:
                if product.is_active and product.stock_quantity > 0:
                    if product.id not in products_dict:
                        products_dict[product.id] = product
        
        # Convert to list and apply limit/offset
        products_list = list(products_dict.values())[offset:offset+limit]
        products_data = [serialize_product_for_mobile(p, user) for p in products_list]
        
        discount_info = None
        if discounts:
            discount_info = {
                'name': discounts[0].name,
                'name_fa': discounts[0].name_fa,
                'discount_percentage': discounts[0].discount_percentage
            }
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_data,
                'discount_info': discount_info
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_discounts_daily_products: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت محصولات تخفیف‌دار'
        }), 500

@app.route('/api/mobile/v1/discounts/monthly-products', methods=['GET'])
def mobile_discounts_monthly_products():
    """Mobile API: Get monthly discount products"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        user = get_current_user()
        
        # Get active monthly discounts
        now = datetime.utcnow()
        discounts = ProductDiscount.query.filter(
            ProductDiscount.discount_type == 'monthly',
            ProductDiscount.is_active == True,
            or_(
                ProductDiscount.start_date.is_(None),
                ProductDiscount.start_date <= now
            ),
            or_(
                ProductDiscount.end_date.is_(None),
                ProductDiscount.end_date >= now
            )
        ).order_by(ProductDiscount.priority.desc(), ProductDiscount.created_at.desc()).all()
        
        # Collect all products from active discounts
        products_dict = {}
        for discount in discounts:
            for product in discount.products:
                if product.is_active and product.stock_quantity > 0:
                    if product.id not in products_dict:
                        products_dict[product.id] = product
        
        # Convert to list and apply limit/offset
        products_list = list(products_dict.values())[offset:offset+limit]
        products_data = [serialize_product_for_mobile(p, user) for p in products_list]
        
        discount_info = None
        if discounts:
            discount_info = {
                'name': discounts[0].name,
                'name_fa': discounts[0].name_fa,
                'discount_percentage': discounts[0].discount_percentage
            }
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_data,
                'discount_info': discount_info
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_discounts_monthly_products: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت محصولات تخفیف‌دار'
        }), 500

# ==================== CART API ====================

@app.route('/api/mobile/v1/cart', methods=['GET'])
@jwt_required()
def mobile_cart_get():
    """Mobile API: Get cart items"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        price_type_filter = request.args.get('price_type')  # Optional filter
        
        # Get all cart items
        query = Cart.query.filter_by(user_id=user.id, is_saved_for_later=False)
        if price_type_filter:
            query = query.filter_by(price_type=price_type_filter)
        
        cart_items = query.all()
        
        # Separate cash and check items
        cash_items = []
        check_items = []
        cash_total = 0
        check_total = 0
        
        for item in cart_items:
            product_data = serialize_product_for_mobile(item.product, user)
            # Convert unit_price from thousands to full Rials
            unit_price_full = int(item.unit_price * 1000) if item.unit_price else 0
            total_price = unit_price_full * item.quantity
            
            item_data = {
                'id': item.id,
                'product': product_data,
                'quantity': item.quantity,
                'unit_price_cash': unit_price_full if item.price_type == 'cash' else None,
                'unit_price_check': unit_price_full if item.price_type == 'check' else None,
                'total_price_cash': total_price if item.price_type == 'cash' else 0,
                'total_price_check': total_price if item.price_type == 'check' else 0,
                'price_type': item.price_type,
                'price_plan': item.price_plan
            }
            
            if item.price_type == 'cash':
                cash_items.append(item_data)
                cash_total += total_price
            else:
                check_items.append(item_data)
                check_total += total_price
        
        return jsonify({
            'success': True,
            'data': {
                'cash_cart': {
                    'items': cash_items,
                    'total': cash_total,
                    'item_count': len(cash_items)
                },
                'check_cart': {
                    'items': check_items,
                    'total': check_total,
                    'item_count': len(check_items)
                },
                'grand_total': cash_total + check_total,
                'total_items': len(cart_items)
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_cart_get: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت سبد خرید'
        }), 500

@app.route('/api/mobile/v1/cart', methods=['POST'])
@jwt_required()
def mobile_cart_add():
    """Mobile API: Add item to cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        price_type = data.get('price_type', 'cash')
        price_plan = data.get('price_plan')
        
        if not product_id:
            return jsonify({
                'success': False,
                'message': 'شناسه محصول الزامی است'
            }), 400
        
        if quantity < 1:
            return jsonify({
                'success': False,
                'message': 'تعداد باید بیشتر از صفر باشد'
            }), 400
        
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return jsonify({
                'success': False,
                'message': 'محصول یافت نشد'
            }), 404
        
        # Check stock
        if product.stock_quantity < quantity:
            return jsonify({
                'success': False,
                'message': f'موجودی کافی نیست. موجودی: {product.stock_quantity}'
            }), 400
        
        # Calculate unit price
        from app import can_see_bulk_prices, can_see_isaco_products
        from routes import is_isaco_feature_enabled, get_isaco_unit_price, isaco_allowed_plans
        
        unit_price = None
        
        # ISACO pricing logic
        if is_isaco_feature_enabled() and getattr(product, 'is_isaco_wh15', False):
            if can_see_isaco_products(user):
                if not price_plan or price_plan not in isaco_allowed_plans():
                    return jsonify({
                        'success': False,
                        'message': 'لطفاً یکی از گزینه‌های ایساکو را انتخاب کنید'
                    }), 400
                unit_price = get_isaco_unit_price(product, price_plan)
        
        # Regular pricing
        if not unit_price or unit_price <= 0:
            if can_see_bulk_prices(user):
                unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
            else:
                unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
        
        # Check if item already exists
        existing_item = Cart.query.filter_by(
            user_id=user.id,
            product_id=product_id,
            price_type=price_type,
            price_plan=price_plan
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            cart_item = existing_item
        else:
            cart_item = Cart(
                user_id=user.id,
                product_id=product_id,
                quantity=quantity,
                price_type=price_type,
                price_plan=price_plan,
                unit_price=unit_price
            )
            models.db.session.add(cart_item)
        
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'محصول به سبد خرید اضافه شد',
            'data': {
                'cart_item': {
                    'id': cart_item.id,
                    'product_id': product_id,
                    'quantity': cart_item.quantity,
                    'price_type': price_type
                }
            }
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_cart_add: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در افزودن به سبد خرید'
        }), 500

@app.route('/api/mobile/v1/cart/<int:cart_item_id>', methods=['PUT'])
@jwt_required()
def mobile_cart_update(cart_item_id):
    """Mobile API: Update cart item quantity"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        data = request.get_json()
        quantity = data.get('quantity')
        
        if not quantity or quantity < 1:
            return jsonify({
                'success': False,
                'message': 'تعداد باید بیشتر از صفر باشد'
            }), 400
        
        cart_item = Cart.query.filter_by(id=cart_item_id, user_id=user.id).first_or_404()
        
        # Check stock
        if cart_item.product.stock_quantity < quantity:
            return jsonify({
                'success': False,
                'message': f'موجودی کافی نیست. موجودی: {cart_item.product.stock_quantity}'
            }), 400
        
        cart_item.quantity = quantity
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تعداد به‌روزرسانی شد'
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_cart_update: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در به‌روزرسانی سبد خرید'
        }), 500

@app.route('/api/mobile/v1/cart/<int:cart_item_id>', methods=['DELETE'])
@jwt_required()
def mobile_cart_remove(cart_item_id):
    """Mobile API: Remove item from cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        cart_item = Cart.query.filter_by(id=cart_item_id, user_id=user.id).first_or_404()
        models.db.session.delete(cart_item)
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'محصول از سبد خرید حذف شد'
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_cart_remove: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در حذف از سبد خرید'
        }), 500

@app.route('/api/mobile/v1/cart/clear', methods=['DELETE'])
@jwt_required()
def mobile_cart_clear():
    """Mobile API: Clear cart"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        price_type = request.args.get('price_type')  # Optional
        
        query = Cart.query.filter_by(user_id=user.id, is_saved_for_later=False)
        if price_type:
            query = query.filter_by(price_type=price_type)
        
        query.delete()
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'سبد خرید پاک شد'
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_cart_clear: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در پاک کردن سبد خرید'
        }), 500

# Continuation of mobile_api_routes.py
# Add these endpoints to the end of mobile_api_routes.py

# ==================== USER API ====================

@app.route('/api/mobile/v1/user/profile', methods=['GET'])
@jwt_required()
def mobile_user_profile_get():
    """Mobile API: Get user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'phone': user.phone,
            'email': user.email or '',
            'company_name': user.company_name or '',
            'national_id': user.national_id or '',
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'address': user.address or '',
            'landline_phone': user.landline_phone or '',
            'secondary_phone': user.secondary_phone or '',
            'is_bulk_buyer': user.is_bulk_buyer,
            'bulk_buyer_approval_status': user.bulk_buyer_approval_status,
            'profile_completion_percentage': user.profile_completion_percentage if hasattr(user, 'profile_completion_percentage') else 0,
            'avatar_url': user.avatar_url if hasattr(user, 'avatar_url') else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify({
            'success': True,
            'data': {
                'user': user_data
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_user_profile_get: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت پروفایل'
        }), 500

@app.route('/api/mobile/v1/user/profile', methods=['PUT'])
@jwt_required()
def mobile_user_profile_update():
    """Mobile API: Update user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        if 'company_name' in data:
            user.company_name = data['company_name']
        if 'national_id' in data:
            user.national_id = data['national_id']
        if 'birth_date' in data:
            try:
                from datetime import datetime
                user.birth_date = datetime.fromisoformat(data['birth_date'].replace('Z', '+00:00')).date()
            except:
                pass
        if 'address' in data:
            user.address = data['address']
        if 'landline_phone' in data:
            user.landline_phone = data['landline_phone']
        if 'secondary_phone' in data:
            user.secondary_phone = data['secondary_phone']
        
        # Calculate profile completion
        if hasattr(user, 'calculate_profile_completion'):
            user.calculate_profile_completion()
        
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'پروفایل با موفقیت به‌روزرسانی شد',
            'data': {
                'user': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'profile_completion_percentage': user.profile_completion_percentage if hasattr(user, 'profile_completion_percentage') else 0
                }
            }
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_user_profile_update: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در به‌روزرسانی پروفایل'
        }), 500

@app.route('/api/mobile/v1/user/bulk-buyer-request', methods=['POST'])
@jwt_required()
def mobile_user_bulk_buyer_request():
    """Mobile API: Submit bulk buyer request"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        data = request.get_json()
        company_name = data.get('company_name')
        national_id = data.get('national_id')
        address = data.get('address')
        landline_phone = data.get('landline_phone')
        description = data.get('description', '')
        
        # Validation
        if not all([company_name, national_id, address, landline_phone]):
            return jsonify({
                'success': False,
                'message': 'تمام فیلدهای الزامی را پر کنید'
            }), 400
        
        # Update user info
        user.company_name = company_name
        user.national_id = national_id
        user.address = address
        user.landline_phone = landline_phone
        user.is_bulk_buyer = True
        user.bulk_buyer_approval_status = 'pending'
        
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'درخواست شما با موفقیت ارسال شد. پس از بررسی، نتیجه به شما اطلاع داده خواهد شد.',
            'data': {
                'request_status': 'pending'
            }
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_user_bulk_buyer_request: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در ارسال درخواست'
        }), 500

@app.route('/api/mobile/v1/user/notifications', methods=['GET'])
@jwt_required()
def mobile_user_notifications():
    """Mobile API: Get user notifications"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = UserNotification.query.filter_by(user_id=user.id)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        pagination = query.order_by(UserNotification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        notifications_data = [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat() if n.created_at else None,
            'action_url': n.action_url if hasattr(n, 'action_url') else None
        } for n in pagination.items]
        
        # Get unread count
        unread_count = UserNotification.query.filter_by(
            user_id=user.id,
            is_read=False
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': notifications_data,
                'unread_count': unread_count,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_user_notifications: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت اعلان‌ها'
        }), 500

@app.route('/api/mobile/v1/user/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mobile_user_notification_mark_read(notification_id):
    """Mobile API: Mark notification as read"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'کاربر یافت نشد'
            }), 401
        
        notification = UserNotification.query.filter_by(
            id=notification_id,
            user_id=user.id
        ).first_or_404()
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        models.db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'اعلان به عنوان خوانده شده علامت‌گذاری شد'
        })
    except Exception as e:
        models.db.session.rollback()
        current_app.logger.error(f"Error in mobile_user_notification_mark_read: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در به‌روزرسانی اعلان'
        }), 500

# ==================== COMPANY API ====================

@app.route('/api/mobile/v1/company/info', methods=['GET'])
def mobile_company_info():
    """Mobile API: Get company information"""
    try:
        company_info = CompanyInfo.query.first()
        
        if not company_info:
            return jsonify({
                'success': True,
                'data': {
                    'name': 'Asia Salman',
                    'name_fa': 'آسیا سلمان',
                    'logo_url': '',
                    'description': '',
                    'description_fa': '',
                    'phone': '',
                    'support_phone': '',
                    'email': '',
                    'address': '',
                    'about': '',
                    'about_fa': '',
                    'partner_brands': []
                }
            })
        
        # Get partner brands
        partner_brands = []
        if hasattr(company_info, 'partner_brand_ids') and company_info.partner_brand_ids:
            try:
                brand_ids = json.loads(company_info.partner_brand_ids)
                brands = Brand.query.filter(Brand.id.in_(brand_ids), Brand.is_active == True).all()
                partner_brands = [{
                    'id': b.id,
                    'name': b.name,
                    'name_fa': b.name_fa,
                    'logo_url': b.logo_url or ''
                } for b in brands]
            except:
                pass
        
        return jsonify({
            'success': True,
            'data': {
                'name': company_info.company_name or 'Asia Salman',
                'name_fa': company_info.company_name_fa or 'آسیا سلمان',
                'logo_url': company_info.logo_url or '',
                'description': company_info.description or '',
                'description_fa': company_info.description_fa or '',
                'phone': company_info.phone or '',
                'support_phone': company_info.support_phone or '',
                'email': company_info.email or '',
                'address': company_info.address or '',
                'about': company_info.about or '',
                'about_fa': company_info.about_fa or '',
                'partner_brands': partner_brands
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_company_info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت اطلاعات شرکت'
        }), 500

@app.route('/api/mobile/v1/company/banners', methods=['GET'])
def mobile_company_banners():
    """Mobile API: Get company banners"""
    try:
        position = request.args.get('position', 'homepage')
        
        banners = Banner.query.filter_by(
            position=position,
            is_active=True
        ).order_by(Banner.display_order.asc(), Banner.created_at.desc()).all()
        
        banners_data = [{
            'id': b.id,
            'title': b.title or '',
            'title_fa': b.title_fa or '',
            'image_url': b.image_url,
            'link_url': b.link_url or '',
            'position': b.position,
            'is_active': b.is_active
        } for b in banners]
        
        return jsonify({
            'success': True,
            'data': {
                'banners': banners_data
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_company_banners: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت بنرها'
        }), 500

# ==================== APP CONFIG API ====================

@app.route('/api/mobile/v1/app/config', methods=['GET'])
def mobile_app_config():
    """Mobile API: Get app configuration"""
    try:
        config = AndroidAppConfig.get_config()
        
        # Get company info if not cached
        company_info = CompanyInfo.query.first()
        if company_info:
            config.company_name = company_info.company_name or config.company_name
            config.company_name_fa = company_info.company_name_fa or config.company_name_fa
            config.company_logo_url = company_info.logo_url or config.company_logo_url
            config.company_phone = company_info.phone or config.company_phone
            config.company_support_phone = company_info.support_phone or config.company_support_phone
            config.company_email = company_info.email or config.company_email
            config.company_address = company_info.address or config.company_address
        
        # Get partner brands
        partner_brands = []
        brand_ids = config.get_partner_brand_ids()
        if brand_ids:
            brands = Brand.query.filter(Brand.id.in_(brand_ids), Brand.is_active == True).all()
            partner_brands = [{
                'id': b.id,
                'name': b.name,
                'name_fa': b.name_fa,
                'logo_url': b.logo_url or ''
            } for b in brands]
        
        # Get daily suggestions products
        daily_suggestions_products = []
        product_ids = config.get_daily_suggestions_product_ids()
        if product_ids:
            user = get_current_user()  # Optional
            products = Product.query.filter(
                Product.id.in_(product_ids),
                Product.is_active == True,
                Product.stock_quantity > 0
            ).limit(20).all()
            daily_suggestions_products = [serialize_product_for_mobile(p, user) for p in products]
        
        return jsonify({
            'success': True,
            'data': {
                'app_version': config.app_version,
                'min_app_version': config.min_app_version,
                'force_update': config.force_update,
                'maintenance_mode': config.maintenance_mode,
                'maintenance_message': config.maintenance_message or '',
                'features': {
                    'daily_suggestions_enabled': config.daily_suggestions_enabled,
                    'wholesale_requests_enabled': config.wholesale_requests_enabled,
                    'wallet_enabled': config.wallet_enabled,
                    'notifications_enabled': config.notifications_enabled
                },
                'settings': {
                    'default_price_type': config.default_price_type,
                    'show_bulk_prices': config.show_bulk_prices,
                    'enable_offline_mode': config.enable_offline_mode
                },
                'daily_suggestions': {
                    'enabled': config.daily_suggestions_enabled,
                    'title': config.daily_suggestions_title,
                    'title_fa': config.daily_suggestions_title_fa,
                    'products': daily_suggestions_products,
                    'updated_at': config.updated_at.isoformat() if config.updated_at else None
                },
                'company': {
                    'name': config.company_name or 'Asia Salman',
                    'name_fa': config.company_name_fa or 'آسیا سلمان',
                    'logo_url': config.company_logo_url or '',
                    'phone': config.company_phone or '',
                    'support_phone': config.company_support_phone or '',
                    'email': config.company_email or '',
                    'address': config.company_address or '',
                    'partner_brands': partner_brands
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in mobile_app_config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت تنظیمات اپلیکیشن'
        }), 500

