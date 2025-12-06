"""
API موبایل برای نرم‌افزار اندروید
Mobile API for Android Application
"""

from flask import Blueprint, request, jsonify, url_for
from flask_login import login_user, current_user, login_required
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func, desc
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import json
import logging
import uuid
from functools import wraps

from models import *
from app import app, can_see_bulk_prices, can_see_isaco_products
import models

# Import normalization functions and ISACO helpers from routes
from routes import normalize_fa_text, normalize_sql_expr, is_isaco_feature_enabled, isaco_allowed_plans, get_isaco_unit_price

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
mobile_api_bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile/v1')

# Helper functions
def clean_phone(phone):
    """Clean and validate phone number"""
    clean = ''.join(filter(str.isdigit, phone))
    if not clean.startswith('09'):
        if clean.startswith('9'):
            clean = '0' + clean
    return clean if len(clean) == 11 and clean.startswith('09') else None

def mobile_auth_required(f):
    """Decorator for mobile API authentication"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'کاربر غیرفعال است',
                    'code': 'USER_INACTIVE'
                }), 401
            return f(user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'خطا در احراز هویت',
                'code': 'AUTH_ERROR'
            }), 401
    return decorated

def format_product_for_mobile(product, user=None):
    """Format product data for mobile API"""
    can_see_bulk = can_see_bulk_prices(user) if user else False
    can_see_isaco = can_see_isaco_products(user) if user else False
    
    # Get prices based on user permissions
    if can_see_bulk:
        cash_price = product.bulk_price_cash if product.bulk_price_cash else product.retail_price_cash
        check_price = product.bulk_price_check if product.bulk_price_check else product.retail_price_check
    else:
        cash_price = product.retail_price_cash
        check_price = product.retail_price_check
    
    # Get images
    images = []
    if product.primary_image:
        images.append(product.primary_image)
    if product.images:
        try:
            img_list = json.loads(product.images) if isinstance(product.images, str) else product.images
            images.extend([img for img in img_list if img and img not in images])
        except:
            pass
    
    result = {
        'id': product.id,
        'sku': product.sku,
        'name': product.name_fa or product.name,
        'name_en': product.name,
        'description': product.description_fa or product.description or '',
        'brand_id': product.brand_id,
        'brand_name': product.brand.name_fa if product.brand else None,
        'category_id': product.category_id,
        'category_name': product.category.category_name if product.category else None,
        'prices': {
            'cash': float(cash_price) if cash_price else 0,
            'check': float(check_price) if check_price else 0,
            'bulk_available': can_see_bulk
        },
        'stock_quantity': product.stock_quantity or 0,
        'in_stock': (product.stock_quantity or 0) > 0,
        'images': images,
        'primary_image': product.primary_image,
        'is_featured': product.is_featured,
        'is_active': product.is_active,
        'oem_code': product.oem_code,
        'min_order_quantity': product.min_order_quantity or 1,
        'max_order_quantity': product.max_order_quantity,
        'weight_kg': float(product.weight_kg) if product.weight_kg else None,
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None
    }
    
    # Add ISACO prices if applicable
    if can_see_isaco and product.is_isaco_wh15:
        result['isaco_prices'] = {
            'cash': float(product.isaco_cash * 1.10) if product.isaco_cash else None,
            '1m': float(product.isaco_1m * 1.10) if product.isaco_1m else None,
            '2m': float(product.isaco_2m * 1.10) if product.isaco_2m else None,
            '3m': float(product.isaco_3m * 1.10) if product.isaco_3m else None
        }
    
    return result

# ==================== AUTHENTICATION ENDPOINTS ====================

@mobile_api_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    """ارسال کد تایید OTP"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({
                'success': False,
                'message': 'شماره تلفن الزامی است',
                'code': 'PHONE_REQUIRED'
            }), 400
        
        clean_phone_num = clean_phone(phone)
        if not clean_phone_num:
            return jsonify({
                'success': False,
                'message': 'شماره تلفن معتبر نیست. باید با 09 شروع شود',
                'code': 'INVALID_PHONE'
            }), 400
        
        # Send OTP using SMS service
        from sms_service import sms_service
        result = sms_service.send_otp(clean_phone_num)
        
        if result['success']:
            # Delete any existing OTP for this phone
            OTPVerification.query.filter_by(phone=clean_phone_num, verified=False).delete()
            
            # Store verification data in database
            expires_at = sms_service.get_expiration_time()
            otp_record = OTPVerification(
                phone=clean_phone_num,
                code=result['code'],
                source='mobile',
                expires_at=expires_at
            )
            db.session.add(otp_record)
            db.session.commit()
            
            logger.info(f"OTP sent to mobile: {clean_phone_num}")
            
            return jsonify({
                'success': True,
                'message': 'کد تایید ارسال شد',
                'phone': clean_phone_num,
                'expires_in': 120  # seconds
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'خطا در ارسال کد تایید'),
                'code': 'SMS_ERROR'
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در ارسال کد تایید',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    """تایید کد OTP و ورود/ثبت‌نام کاربر"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        otp_code = data.get('otp_code')
        device_id = data.get('device_id')  # Optional: for device tracking
        
        if not phone or not otp_code:
            return jsonify({
                'success': False,
                'message': 'شماره تلفن و کد تایید الزامی است',
                'code': 'MISSING_PARAMS'
            }), 400
        
        clean_phone_num = clean_phone(phone)
        if not clean_phone_num:
            return jsonify({
                'success': False,
                'message': 'شماره تلفن معتبر نیست',
                'code': 'INVALID_PHONE'
            }), 400
        
        # Clean up expired OTPs
        OTPVerification.query.filter(
            OTPVerification.expires_at <= datetime.utcnow(),
            OTPVerification.verified == False
        ).delete()
        db.session.commit()
        
        # Verify OTP
        otp_record = OTPVerification.query.filter_by(
            phone=clean_phone_num,
            verified=False,
            source='mobile'
        ).filter(OTPVerification.expires_at > datetime.utcnow()).first()
        
        if not otp_record:
            return jsonify({
                'success': False,
                'message': 'کد تایید یافت نشد یا منقضی شده است',
                'code': 'OTP_NOT_FOUND'
            }), 404
        
        if otp_record.code != str(otp_code):
            return jsonify({
                'success': False,
                'message': 'کد تایید اشتباه است',
                'code': 'INVALID_OTP'
            }), 400
        
        # OTP verified successfully
        otp_record.verified = True
        otp_record.verified_at = datetime.utcnow()
        
        # Check if user exists
        user = User.query.filter_by(phone=clean_phone_num).first()
        
        is_new_user = False
        if not user:
            # Create new user
            is_new_user = True
            username = f"user_{clean_phone_num}"
            user = User(
                username=username,
                phone=clean_phone_num,
                full_name='',
                password_hash=generate_password_hash(str(uuid.uuid4())),  # Random password
                phone_verified=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()
            
            # Create wallet for user
            wallet = Wallet(user_id=user.id, balance=0)
            db.session.add(wallet)
        
        # Update user
        user.phone_verified = True
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Login user
        login_user(user)
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        # Return user data
        user_data = {
            'id': user.id,
            'phone': user.phone,
            'full_name': user.full_name or '',
            'email': user.email or '',
            'is_bulk_buyer': user.is_bulk_buyer,
            'bulk_buyer_status': user.bulk_buyer_approval_status,
            'profile_completed': user.profile_completion_percentage >= 100
        }
        
        logger.info(f"User authenticated via mobile: {clean_phone_num}, new_user: {is_new_user}")
        
        return jsonify({
            'success': True,
            'message': 'ورود موفقیت‌آمیز بود',
            'data': {
                'user': user_data,
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': 604800  # 7 days in seconds
                },
                'is_new_user': is_new_user
            }
        })
        
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در تایید کد',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/auth/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """تازه‌سازی توکن دسترسی"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'message': 'کاربر غیرفعال است',
                'code': 'USER_INACTIVE'
            }), 401
        
        # Create new access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token,
                'expires_in': 604800
            }
        })
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در تازه‌سازی توکن',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/auth/logout', methods=['POST'])
@mobile_auth_required
def logout(user):
    """خروج از حساب کاربری"""
    try:
        # In a JWT system, logout is typically handled client-side by removing the token
        # But we can log the logout event
        logger.info(f"User logged out: {user.phone}")
        
        return jsonify({
            'success': True,
            'message': 'خروج موفقیت‌آمیز بود'
        })
        
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در خروج',
            'code': 'SERVER_ERROR'
        }), 500

# ==================== PRODUCT ENDPOINTS ====================

@mobile_api_bp.route('/products', methods=['GET'])
@jwt_required(optional=True)
def get_products():
    """لیست محصولات با pagination و فیلتر"""
    try:
        # Get user if authenticated
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            pass
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Max 100 items per page
        
        brand_id = request.args.get('brand_id', type=int)
        category_id = request.args.get('category_id', type=int)
        vehicle_type_id = request.args.get('vehicle_type_id', type=int)
        search_query = request.args.get('search', '')
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        in_stock_only = request.args.get('in_stock', 'false').lower() == 'true'
        
        # Build query
        query = Product.query.filter_by(is_active=True)
        
        # Filter out Isaco products if user doesn't have permission
        if not can_see_isaco_products(user):
            isaco_brand_id = app.config.get('ISACO_BRAND_ID')
            if isaco_brand_id:
                query = query.filter(Product.brand_id != isaco_brand_id)
        
        # Apply filters
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if vehicle_type_id:
            query = query.join(ProductVehicleType).filter(
                ProductVehicleType.vehicle_type_id == vehicle_type_id
            )
        
        if search_query:
            try:
                norm_q = normalize_fa_text(search_query)
                name_norm = normalize_sql_expr(Product.name)
                name_fa_norm = normalize_sql_expr(Product.name_fa)
                
                query = query.filter(
                    or_(
                        name_norm.contains(norm_q),
                        name_fa_norm.contains(norm_q),
                        Product.sku.contains(norm_q),
                        Product.oem_code.contains(norm_q)
                    )
                )
            except Exception as e:
                logger.error(f"Search normalization failed: {e}")
                query = query.filter(
                    or_(
                        Product.name.contains(search_query),
                        Product.name_fa.contains(search_query),
                        Product.sku.contains(search_query),
                        Product.oem_code.contains(search_query)
                    )
                )
        
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        if in_stock_only:
            query = query.filter(Product.stock_quantity > 0)
        
        # Paginate
        products = query.order_by(desc(Product.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format products
        products_list = [format_product_for_mobile(p, user) for p in products.items]
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': products.total,
                    'pages': products.pages,
                    'has_next': products.has_next,
                    'has_prev': products.has_prev
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت محصولات',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required(optional=True)
def get_product_detail(product_id):
    """جزئیات یک محصول"""
    try:
        # Get user if authenticated
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            pass
        
        product = Product.query.get_or_404(product_id)
        
        if not product.is_active:
            return jsonify({
                'success': False,
                'message': 'محصول یافت نشد',
                'code': 'PRODUCT_NOT_FOUND'
            }), 404
        
        # Check ISACO permission
        if product.is_isaco_wh15 and not can_see_isaco_products(user):
            return jsonify({
                'success': False,
                'message': 'دسترسی به این محصول ندارید',
                'code': 'ACCESS_DENIED'
            }), 403
        
        # Format product
        product_data = format_product_for_mobile(product, user)
        
        # Add detailed information
        product_data['description_full'] = product.description_fa or product.description or ''
        product_data['technical_specs'] = product.get_technical_specs()
        product_data['dimensions'] = product.get_dimensions()
        product_data['compatible_models'] = product.get_compatible_models()
        product_data['tags'] = product.get_tags()
        
        return jsonify({
            'success': True,
            'data': product_data
        })
        
    except Exception as e:
        logger.error(f"Error getting product detail: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت جزئیات محصول',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/products/search', methods=['GET'])
@jwt_required(optional=True)
def search_products():
    """جستجوی پیشرفته محصولات"""
    try:
        # Get user if authenticated
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            pass
        
        search_query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)
        
        if not search_query:
            return jsonify({
                'success': True,
                'data': {
                    'products': [],
                    'count': 0
                }
            })
        
        # Build search query
        query = Product.query.filter_by(is_active=True)
        
        # Filter out Isaco products if needed
        if not can_see_isaco_products(user):
            isaco_brand_id = app.config.get('ISACO_BRAND_ID')
            if isaco_brand_id:
                query = query.filter(Product.brand_id != isaco_brand_id)
        
        # Search
        try:
            norm_q = normalize_fa_text(search_query)
            name_norm = normalize_sql_expr(Product.name)
            name_fa_norm = normalize_sql_expr(Product.name_fa)
            
            products = query.filter(
                or_(
                    name_norm.contains(norm_q),
                    name_fa_norm.contains(norm_q),
                    Product.sku.contains(norm_q),
                    Product.oem_code.contains(norm_q)
                )
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Search normalization failed: {e}")
            products = query.filter(
                or_(
                    Product.name.contains(search_query),
                    Product.name_fa.contains(search_query),
                    Product.sku.contains(search_query),
                    Product.oem_code.contains(search_query)
                )
            ).limit(limit).all()
        
        # Format products
        products_list = [format_product_for_mobile(p, user) for p in products]
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_list,
                'count': len(products_list)
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در جستجو',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/products/filters', methods=['GET'])
def get_product_filters():
    """دریافت فیلترهای موجود"""
    try:
        brands = Brand.query.filter_by(is_active=True).all()
        categories = PartCategory.query.filter_by(is_active=True).all()
        vehicle_types = VehicleType.query.all()
        
        return jsonify({
            'success': True,
            'data': {
                'brands': [{'id': b.id, 'name': b.name_fa, 'name_en': b.name} for b in brands],
                'categories': [{'id': c.id, 'name': c.category_name_fa or c.category_name} for c in categories],
                'vehicle_types': [{'id': vt.id, 'name': vt.type_name_fa or vt.type_name} for vt in vehicle_types]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting filters: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت فیلترها',
            'code': 'SERVER_ERROR'
        }), 500

# ==================== CATEGORY ENDPOINTS ====================

@mobile_api_bp.route('/categories', methods=['GET'])
def get_categories():
    """لیست تمام دسته‌بندی‌ها"""
    try:
        categories = PartCategory.query.filter_by(is_active=True).order_by(PartCategory.sort_order).all()
        
        categories_list = []
        for cat in categories:
            # Count products in category
            product_count = Product.query.filter_by(
                category_id=cat.id,
                is_active=True
            ).count()
            
            categories_list.append({
                'id': cat.id,
                'name': cat.category_name_fa or cat.category_name,
                'name_en': cat.category_name,
                'description': cat.description or '',
                'icon_class': cat.icon_class,
                'product_count': product_count,
                'parent_id': cat.parent_id
            })
        
        return jsonify({
            'success': True,
            'data': {
                'categories': categories_list
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت دسته‌بندی‌ها',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/categories/vehicle-based', methods=['GET'])
@jwt_required(optional=True)
def get_vehicle_based_categories():
    """دسته‌بندی بر اساس نوع خودرو"""
    try:
        # Get user if authenticated
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            pass
        
        # Get all vehicle types
        vehicle_types = VehicleType.query.all()
        
        result = []
        for vt in vehicle_types:
            # Get categories that have products for this vehicle type
            categories = models.db.session.query(PartCategory).join(Product).join(
                ProductVehicleType
            ).filter(
                ProductVehicleType.vehicle_type_id == vt.id,
                Product.is_active == True,
                PartCategory.is_active == True
            ).distinct().all()
            
            # Count products for this vehicle type
            product_count = models.db.session.query(func.count(Product.id)).join(
                ProductVehicleType
            ).filter(
                ProductVehicleType.vehicle_type_id == vt.id,
                Product.is_active == True
            ).scalar() or 0
            
            # Filter out Isaco products if needed
            if not can_see_isaco_products(user):
                isaco_brand_id = app.config.get('ISACO_BRAND_ID')
                if isaco_brand_id:
                    product_count = models.db.session.query(func.count(Product.id)).join(
                        ProductVehicleType
                    ).filter(
                        ProductVehicleType.vehicle_type_id == vt.id,
                        Product.is_active == True,
                        Product.brand_id != isaco_brand_id
                    ).scalar() or 0
            
            category_list = []
            for cat in categories:
                # Count products in this category for this vehicle type
                cat_count = models.db.session.query(func.count(Product.id)).join(
                    ProductVehicleType
                ).filter(
                    ProductVehicleType.vehicle_type_id == vt.id,
                    Product.category_id == cat.id,
                    Product.is_active == True
                ).scalar() or 0
                
                category_list.append({
                    'id': cat.id,
                    'name': cat.category_name_fa or cat.category_name,
                    'name_en': cat.category_name,
                    'product_count': cat_count
                })
            
            result.append({
                'vehicle_type': {
                    'id': vt.id,
                    'name': vt.type_name_fa or vt.type_name,
                    'name_en': vt.type_name
                },
                'categories': category_list,
                'total_products': product_count
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle-based categories: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت دسته‌بندی‌ها',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/categories/brand-based', methods=['GET'])
def get_brand_based_categories():
    """دسته‌بندی بر اساس برند کالا"""
    try:
        # Get all active brands
        brands = Brand.query.filter_by(is_active=True).all()
        
        result = []
        for brand in brands:
            # Get categories that have products for this brand
            categories = models.db.session.query(PartCategory).join(Product).filter(
                Product.brand_id == brand.id,
                Product.is_active == True,
                PartCategory.is_active == True
            ).distinct().all()
            
            # Count products for this brand
            product_count = Product.query.filter_by(
                brand_id=brand.id,
                is_active=True
            ).count()
            
            category_list = []
            for cat in categories:
                # Count products in this category for this brand
                cat_count = Product.query.filter_by(
                    brand_id=brand.id,
                    category_id=cat.id,
                    is_active=True
                ).count()
                
                category_list.append({
                    'id': cat.id,
                    'name': cat.category_name_fa or cat.category_name,
                    'name_en': cat.category_name,
                    'product_count': cat_count
                })
            
            result.append({
                'brand': {
                    'id': brand.id,
                    'name': brand.name_fa,
                    'name_en': brand.name,
                    'logo': brand.logo_url
                },
                'categories': category_list,
                'total_products': product_count
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error getting brand-based categories: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت دسته‌بندی‌ها',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/categories/<int:category_id>/products', methods=['GET'])
@jwt_required(optional=True)
def get_category_products(category_id):
    """محصولات یک دسته‌بندی"""
    try:
        # Get user if authenticated
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            pass
        
        category = PartCategory.query.get_or_404(category_id)
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        # Build query
        query = Product.query.filter_by(
            category_id=category_id,
            is_active=True
        )
        
        # Filter out Isaco products if needed
        if not can_see_isaco_products(user):
            isaco_brand_id = app.config.get('ISACO_BRAND_ID')
            if isaco_brand_id:
                query = query.filter(Product.brand_id != isaco_brand_id)
        
        # Paginate
        products = query.order_by(desc(Product.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format products
        products_list = [format_product_for_mobile(p, user) for p in products.items]
        
        return jsonify({
            'success': True,
            'data': {
                'category': {
                    'id': category.id,
                    'name': category.category_name_fa or category.category_name,
                    'name_en': category.category_name
                },
                'products': products_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': products.total,
                    'pages': products.pages,
                    'has_next': products.has_next,
                    'has_prev': products.has_prev
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting category products: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت محصولات',
            'code': 'SERVER_ERROR'
        }), 500

# ==================== CART ENDPOINTS ====================

def format_cart_item_for_mobile(cart_item, user=None):
    """Format cart item data for mobile API"""
    product = cart_item.product
    product_data = format_product_for_mobile(product, user) if product else None
    
    return {
        'id': cart_item.id,
        'product': product_data,
        'quantity': cart_item.quantity,
        'price_type': cart_item.price_type,
        'unit_price': float(cart_item.unit_price) if cart_item.unit_price else 0,
        'total_price': float(cart_item.get_total_price()),
        'price_plan': cart_item.price_plan,
        'is_saved_for_later': cart_item.is_saved_for_later,
        'notes': cart_item.notes,
        'created_at': cart_item.created_at.isoformat() if cart_item.created_at else None,
        'updated_at': cart_item.updated_at.isoformat() if cart_item.updated_at else None
    }

@mobile_api_bp.route('/cart', methods=['GET'])
@mobile_auth_required
def get_cart(user):
    """دریافت سبد خرید (تمام موارد)"""
    try:
        price_type = request.args.get('price_type')  # Optional: 'cash' or 'check'
        
        # Build query
        query = Cart.query.filter_by(
            user_id=user.id,
            is_saved_for_later=False
        )
        
        if price_type:
            query = query.filter_by(price_type=price_type)
        
        cart_items = query.all()
        
        # Separate cash and check items
        cash_items = [item for item in cart_items if item.price_type == 'cash']
        check_items = [item for item in cart_items if item.price_type == 'check']
        
        # Calculate totals
        cash_total = sum(item.get_total_price() for item in cash_items)
        check_total = sum(item.get_total_price() for item in check_items)
        
        return jsonify({
            'success': True,
            'data': {
                'cash_cart': {
                    'items': [format_cart_item_for_mobile(item, user) for item in cash_items],
                    'total': float(cash_total),
                    'item_count': len(cash_items)
                },
                'check_cart': {
                    'items': [format_cart_item_for_mobile(item, user) for item in check_items],
                    'total': float(check_total),
                    'item_count': len(check_items)
                },
                'grand_total': float(cash_total + check_total),
                'total_items': len(cart_items)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت سبد خرید',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/cart/cash', methods=['GET'])
@mobile_auth_required
def get_cash_cart(user):
    """دریافت سبد خرید نقدی"""
    try:
        cart_items = Cart.query.filter_by(
            user_id=user.id,
            price_type='cash',
            is_saved_for_later=False
        ).all()
        
        total = sum(item.get_total_price() for item in cart_items)
        
        return jsonify({
            'success': True,
            'data': {
                'items': [format_cart_item_for_mobile(item, user) for item in cart_items],
                'total': float(total),
                'item_count': len(cart_items)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting cash cart: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت سبد خرید',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/cart/check', methods=['GET'])
@mobile_auth_required
def get_check_cart(user):
    """دریافت سبد خرید چکی"""
    try:
        cart_items = Cart.query.filter_by(
            user_id=user.id,
            price_type='check',
            is_saved_for_later=False
        ).all()
        
        total = sum(item.get_total_price() for item in cart_items)
        
        return jsonify({
            'success': True,
            'data': {
                'items': [format_cart_item_for_mobile(item, user) for item in cart_items],
                'total': float(total),
                'item_count': len(cart_items)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting check cart: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت سبد خرید',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/cart', methods=['POST'])
@mobile_auth_required
def add_to_cart(user):
    """افزودن محصول به سبد خرید"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        price_type = data.get('price_type', 'cash')  # 'cash' or 'check'
        price_plan = data.get('price_plan')  # For ISACO products
        
        if not product_id:
            return jsonify({
                'success': False,
                'message': 'شناسه محصول الزامی است',
                'code': 'PRODUCT_ID_REQUIRED'
            }), 400
        
        if price_type not in ['cash', 'check']:
            return jsonify({
                'success': False,
                'message': 'نوع قیمت باید cash یا check باشد',
                'code': 'INVALID_PRICE_TYPE'
            }), 400
        
        product = Product.query.get_or_404(product_id)
        
        if not product.is_active:
            return jsonify({
                'success': False,
                'message': 'محصول غیرفعال است',
                'code': 'PRODUCT_INACTIVE'
            }), 400
        
        # Check stock
        if product.stock_quantity and product.stock_quantity < quantity:
            return jsonify({
                'success': False,
                'message': f'موجودی کافی نیست. موجودی: {product.stock_quantity}',
                'code': 'INSUFFICIENT_STOCK'
            }), 400
        
        # Determine unit price based on user permissions
        can_see_bulk = can_see_bulk_prices(user)
        can_see_isaco = can_see_isaco_products(user)
        
        # ISACO pricing
        if is_isaco_feature_enabled() and product.is_isaco_wh15 and can_see_isaco:
            if price_plan and price_plan in isaco_allowed_plans():
                unit_price = get_isaco_unit_price(product, price_plan)
                if not unit_price or unit_price <= 0:
                    return jsonify({
                        'success': False,
                        'message': 'قیمت انتخاب‌شده معتبر نیست',
                        'code': 'INVALID_PRICE'
                    }), 400
            else:
                # Use regular pricing for ISACO if plan not specified
                if can_see_bulk:
                    unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
                else:
                    unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
        else:
            # Regular pricing
            if can_see_bulk:
                unit_price = product.bulk_price_cash if price_type == 'cash' else product.bulk_price_check
            else:
                unit_price = product.retail_price_cash if price_type == 'cash' else product.retail_price_check
        
        if not unit_price or unit_price <= 0:
            return jsonify({
                'success': False,
                'message': 'قیمت محصول معتبر نیست',
                'code': 'INVALID_PRICE'
            }), 400
        
        # Check if item already exists in cart
        existing_item = Cart.query.filter_by(
            user_id=user.id,
            product_id=product_id,
            price_type=price_type,
            price_plan=price_plan
        ).first()
        
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            # Check stock again
            if product.stock_quantity and product.stock_quantity < new_quantity:
                return jsonify({
                    'success': False,
                    'message': f'موجودی کافی نیست',
                    'code': 'INSUFFICIENT_STOCK'
                }), 400
            existing_item.quantity = new_quantity
            existing_item.unit_price = unit_price  # Update price in case it changed
            db.session.commit()
        else:
            cart_item = Cart(
                user_id=user.id,
                product_id=product_id,
                quantity=quantity,
                price_type=price_type,
                price_plan=price_plan,
                unit_price=unit_price
            )
            db.session.add(cart_item)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'محصول به سبد خرید اضافه شد',
            'data': {
                'cart_item': format_cart_item_for_mobile(existing_item if existing_item else cart_item, user)
            }
        })
        
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در افزودن به سبد خرید',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/cart/<int:cart_item_id>', methods=['PUT'])
@mobile_auth_required
def update_cart_item(user, cart_item_id):
    """تغییر تعداد محصول در سبد خرید"""
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None:
            return jsonify({
                'success': False,
                'message': 'تعداد الزامی است',
                'code': 'QUANTITY_REQUIRED'
            }), 400
        
        if quantity < 0:
            return jsonify({
                'success': False,
                'message': 'تعداد نمی‌تواند منفی باشد',
                'code': 'INVALID_QUANTITY'
            }), 400
        
        cart_item = Cart.query.filter_by(
            id=cart_item_id,
            user_id=user.id
        ).first_or_404()
        
        product = cart_item.product
        
        if quantity == 0:
            # Remove item
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'محصول از سبد خرید حذف شد'
            })
        
        # Check stock
        if product.stock_quantity and product.stock_quantity < quantity:
            return jsonify({
                'success': False,
                'message': f'موجودی کافی نیست. موجودی: {product.stock_quantity}',
                'code': 'INSUFFICIENT_STOCK'
            }), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تعداد محصول به‌روزرسانی شد',
            'data': {
                'cart_item': format_cart_item_for_mobile(cart_item, user)
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در به‌روزرسانی سبد خرید',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/cart/<int:cart_item_id>', methods=['DELETE'])
@mobile_auth_required
def remove_from_cart(user, cart_item_id):
    """حذف محصول از سبد خرید"""
    try:
        cart_item = Cart.query.filter_by(
            id=cart_item_id,
            user_id=user.id
        ).first_or_404()
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'محصول از سبد خرید حذف شد'
        })
        
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در حذف از سبد خرید',
            'code': 'SERVER_ERROR'
        }), 500

# ==================== ORDER/INVOICE ENDPOINTS ====================

def format_invoice_for_mobile(invoice, user=None):
    """Format invoice data for mobile API"""
    items = []
    for item in invoice.items:
        product = item.product
        items.append({
            'id': item.id,
            'product': {
                'id': product.id if product else None,
                'name': product.name_fa if product else 'محصول حذف شده',
                'sku': product.sku if product else '',
                'image': product.primary_image if product else None
            },
            'quantity': item.quantity,
            'unit_price': float(item.unit_price) if item.unit_price else 0,
            'total_price': float(item.total_price) if item.total_price else 0,
            'price_type': item.price_type,
            'price_plan': item.price_plan
        })
    
    return {
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'total_amount': float(invoice.total_amount) if invoice.total_amount else 0,
        'payment_type': invoice.payment_type,
        'status': invoice.status,
        'approval_status': invoice.approval_status,
        'items': items,
        'items_count': len(items),
        'created_at': invoice.created_at.isoformat() if invoice.created_at else None,
        'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
        'customer_notes': invoice.customer_notes
    }

@mobile_api_bp.route('/orders', methods=['GET'])
@mobile_auth_required
def get_orders(user):
    """لیست سفارشات (فاکتورها) کاربر"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        per_page = min(per_page, 50)
        
        status = request.args.get('status')  # Optional filter
        
        # Build query
        query = Invoice.query.filter_by(user_id=user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Paginate
        invoices = query.order_by(desc(Invoice.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format invoices
        orders_list = [format_invoice_for_mobile(inv, user) for inv in invoices.items]
        
        return jsonify({
            'success': True,
            'data': {
                'orders': orders_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': invoices.total,
                    'pages': invoices.pages,
                    'has_next': invoices.has_next,
                    'has_prev': invoices.has_prev
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت سفارشات',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/orders/<int:order_id>', methods=['GET'])
@mobile_auth_required
def get_order_detail(user, order_id):
    """جزئیات یک سفارش (فاکتور)"""
    try:
        invoice = Invoice.query.filter_by(
            id=order_id,
            user_id=user.id
        ).first_or_404()
        
        return jsonify({
            'success': True,
            'data': {
                'order': format_invoice_for_mobile(invoice, user)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting order detail: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت جزئیات سفارش',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/orders', methods=['POST'])
@mobile_auth_required
def create_order(user):
    """ایجاد سفارش جدید از سبد خرید"""
    try:
        data = request.get_json()
        payment_type = data.get('payment_type', 'cash')
        customer_notes = data.get('customer_notes', '')
        
        if payment_type not in ['cash', 'check']:
            return jsonify({
                'success': False,
                'message': 'نوع پرداخت باید cash یا check باشد',
                'code': 'INVALID_PAYMENT_TYPE'
            }), 400
        
        # Get cart items for this payment type
        cart_items = Cart.query.filter_by(
            user_id=user.id,
            price_type=payment_type,
            is_saved_for_later=False
        ).all()
        
        if not cart_items:
            return jsonify({
                'success': False,
                'message': 'سبد خرید خالی است',
                'code': 'EMPTY_CART'
            }), 400
        
        # Validate stock for all items
        for item in cart_items:
            product = item.product
            if not product:
                continue
            if product.stock_quantity is not None and product.stock_quantity < item.quantity:
                return jsonify({
                    'success': False,
                    'message': f'موجودی کالای {product.name_fa} کافی نیست',
                    'code': 'INSUFFICIENT_STOCK',
                    'product_id': product.id
                }), 400
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total amount
        total_amount = sum(item.get_total_price() for item in cart_items)
        
        if total_amount <= 0:
            return jsonify({
                'success': False,
                'message': 'مبلغ سفارش باید بیشتر از صفر باشد',
                'code': 'INVALID_AMOUNT'
            }), 400
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            user_id=user.id,
            total_amount=total_amount,
            payment_type=payment_type,
            status='pending',
            customer_notes=customer_notes,
            customer_type=user.customer_type if hasattr(user, 'customer_type') else 'individual'
        )
        
        db.session.add(invoice)
        db.session.flush()  # Get the invoice ID
        
        # Create invoice items
        for cart_item in cart_items:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.get_total_price(),
                price_type=cart_item.price_type,
                price_plan=cart_item.price_plan
            )
            db.session.add(invoice_item)
        
        # Clear cart items (only for this payment type)
        Cart.query.filter_by(
            user_id=user.id,
            price_type=payment_type,
            is_saved_for_later=False
        ).delete()
        
        db.session.commit()
        
        # Award points if service exists
        try:
            from points_service import PointsService
            points_service = PointsService()
            points_service.award_points_for_invoice(invoice.id)
        except:
            pass  # Points service is optional
        
        return jsonify({
            'success': True,
            'message': 'سفارش با موفقیت ایجاد شد',
            'data': {
                'order': format_invoice_for_mobile(invoice, user)
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در ایجاد سفارش',
            'code': 'SERVER_ERROR'
        }), 500

# ==================== USER PROFILE ENDPOINTS ====================

def format_user_profile_for_mobile(user):
    """Format user profile data for mobile API"""
    profile_data = {
        'id': user.id,
        'full_name': user.full_name,
        'phone': user.phone,
        'email': user.email,
        'company_name': user.company_name,
        'address': user.address,
        'landline_phone': user.landline_phone,
        'secondary_phone': user.secondary_phone,
        'national_id': user.national_id,
        'profile_completion_percentage': user.profile_completion_percentage or 0,
        'is_bulk_buyer': user.is_bulk_buyer or False,
        'bulk_buyer_approval_status': user.bulk_buyer_approval_status or 'pending',
        'customer_type': user.customer_type if hasattr(user, 'customer_type') else 'individual',
        'bulk_customer_level': user.bulk_customer_level if hasattr(user, 'bulk_customer_level') else None,
        'total_purchase_amount': float(user.total_purchase_amount) if hasattr(user, 'total_purchase_amount') and user.total_purchase_amount else 0,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }
    
    # Add wallet balance if exists
    try:
        if hasattr(user, 'wallet') and user.wallet:
            profile_data['wallet_balance'] = float(user.wallet.balance)
        else:
            profile_data['wallet_balance'] = 0.0
    except:
        profile_data['wallet_balance'] = 0.0
    
    return profile_data

@mobile_api_bp.route('/user/profile', methods=['GET'])
@mobile_auth_required
def get_user_profile(user):
    """دریافت پروفایل کاربر"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'profile': format_user_profile_for_mobile(user)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت پروفایل',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/user/profile', methods=['PUT'])
@mobile_auth_required
def update_user_profile(user):
    """به‌روزرسانی پروفایل کاربر"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'email' in data:
            email = data['email'].strip()
            if email:
                # Check if email is already taken by another user
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({
                        'success': False,
                        'message': 'این ایمیل قبلاً استفاده شده است',
                        'code': 'EMAIL_ALREADY_EXISTS'
                    }), 400
                user.email = email
        
        if 'company_name' in data:
            user.company_name = data['company_name'].strip() if data['company_name'] else None
        
        if 'address' in data:
            user.address = data['address'].strip() if data['address'] else None
        
        if 'landline_phone' in data:
            user.landline_phone = data['landline_phone'].strip() if data['landline_phone'] else None
        
        if 'secondary_phone' in data:
            user.secondary_phone = data['secondary_phone'].strip() if data['secondary_phone'] else None
        
        if 'national_id' in data:
            user.national_id = data['national_id'].strip() if data['national_id'] else None
        
        # Calculate profile completion
        fields = ['full_name', 'phone', 'email', 'address', 'national_id']
        completed = sum([
            1 if getattr(user, field) else 0
            for field in fields
        ])
        user.profile_completion_percentage = int((completed / len(fields)) * 100)
        
        if user.profile_completion_percentage == 100 and not user.profile_completed_at:
            user.profile_completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'پروفایل با موفقیت به‌روزرسانی شد',
            'data': {
                'profile': format_user_profile_for_mobile(user)
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در به‌روزرسانی پروفایل',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/user/bulk-buyer-request', methods=['POST'])
@mobile_auth_required
def submit_bulk_buyer_request(user):
    """ارسال درخواست خریدار عمده"""
    try:
        data = request.get_json()
        
        # Check if user already has a pending request
        if user.is_bulk_buyer and user.bulk_buyer_approval_status == 'pending':
            return jsonify({
                'success': False,
                'message': 'شما قبلاً درخواست خریدار عمده ارسال کرده‌اید که در حال بررسی است',
                'code': 'REQUEST_PENDING'
            }), 400
        
        # Check if user is already approved
        if user.is_bulk_buyer and user.bulk_buyer_approval_status == 'approved':
            return jsonify({
                'success': False,
                'message': 'شما قبلاً به عنوان خریدار عمده تایید شده‌اید',
                'code': 'ALREADY_APPROVED'
            }), 400
        
        # Update user fields for bulk buyer request
        user.is_bulk_buyer = True
        user.bulk_buyer_approval_status = 'pending'
        user.user_type = 'bulk_buyer'
        
        # Update company information if provided
        if 'company_name' in data:
            user.company_name = data['company_name'].strip()
        
        if 'national_id' in data:
            user.national_id = data['national_id'].strip()
        
        if 'address' in data:
            user.address = data['address'].strip()
        
        if 'landline_phone' in data:
            user.landline_phone = data['landline_phone'].strip()
        
        if 'sales_expert_name' in data:
            # This could be stored in a custom field or UserDocument
            pass
        
        # Send notification to admin
        try:
            from models import UserNotification
            admin_users = User.query.filter_by(is_admin=True, is_active=True).all()
            for admin in admin_users:
                notification = UserNotification(
                    user_id=admin.id,
                    notification_type='bulk_buyer_request',
                    title='درخواست خریدار عمده جدید',
                    message=f'کاربر {user.full_name} ({user.phone}) درخواست خریدار عمده ارسال کرده است.'
                )
                db.session.add(notification)
        except Exception as e:
            logger.error(f"Error sending admin notification: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'درخواست شما با موفقیت ارسال شد. در حال بررسی است.',
            'data': {
                'profile': format_user_profile_for_mobile(user)
            }
        })
        
    except Exception as e:
        logger.error(f"Error submitting bulk buyer request: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'خطا در ارسال درخواست',
            'code': 'SERVER_ERROR'
        }), 500

# ==================== CONFIG ENDPOINTS ====================

@mobile_api_bp.route('/config', methods=['GET'])
def get_app_config():
    """دریافت تنظیمات کلی اپلیکیشن"""
    try:
        config = {
            'app_version': '1.0.0',
            'api_version': '1.0',
            'min_supported_version': '1.0.0',
            'features': {
                'isaco_enabled': is_isaco_feature_enabled(),
                'points_enabled': True,
                'bulk_buyer_enabled': True
            }
        }
        
        return jsonify({
            'success': True,
            'data': config
        })
        
    except Exception as e:
        logger.error(f"Error getting app config: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت تنظیمات',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/config/banners', methods=['GET'])
def get_banners():
    """دریافت بنرها و اطلاعیه‌ها"""
    try:
        banners = []
        
        # Get active announcements
        announcements = Announcement.query.filter_by(is_active=True).order_by(
            desc(Announcement.created_at)
        ).limit(10).all()
        
        for ann in announcements:
            banners.append({
                'id': ann.id,
                'type': 'announcement',
                'title': ann.title,
                'content': ann.content,
                'created_at': ann.created_at.isoformat() if ann.created_at else None
            })
        
        # Get active festivals/special offers
        festivals = Festival.query.filter_by(is_active=True).filter(
            or_(
                Festival.start_date.is_(None),
                Festival.start_date <= datetime.utcnow()
            ),
            or_(
                Festival.end_date.is_(None),
                Festival.end_date >= datetime.utcnow()
            )
        ).order_by(desc(Festival.created_at)).limit(10).all()
        
        for fest in festivals:
            banners.append({
                'id': fest.id,
                'type': 'festival',
                'title': fest.title,
                'description': fest.description,
                'discount_percentage': float(fest.discount_percentage) if fest.discount_percentage else 0,
                'start_date': fest.start_date.isoformat() if fest.start_date else None,
                'end_date': fest.end_date.isoformat() if fest.end_date else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'banners': banners,
                'count': len(banners)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting banners: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت بنرها',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/config/company-info', methods=['GET'])
def get_company_info():
    """دریافت اطلاعات شرکت"""
    try:
        company_info = CompanyInfo.query.first()
        
        if not company_info:
            # Return default structure if no company info exists
            return jsonify({
                'success': True,
                'data': {
                    'company_name': 'شرکت آسیا سلمان',
                    'description': '',
                    'address': '',
                    'phone': '',
                    'email': '',
                    'logo': None,
                    'bulk_purchase_conditions': ''
                }
            })
        
        # Build logo URL if exists
        logo_url = None
        if company_info.logo:
            if company_info.logo.startswith('http'):
                logo_url = company_info.logo
            else:
                logo_url = url_for('static', filename=f'uploads/{company_info.logo}', _external=True)
        
        return jsonify({
            'success': True,
            'data': {
                'company_name': company_info.company_name,
                'description': company_info.description or '',
                'address': company_info.address or '',
                'phone': company_info.phone or '',
                'email': company_info.email or '',
                'logo': logo_url,
                'bulk_purchase_conditions': company_info.bulk_purchase_conditions or ''
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting company info: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت اطلاعات شرکت',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/config/splash', methods=['GET'])
def get_splash_config():
    """دریافت تنظیمات صفحه ابتدایی (Splash Screen)"""
    try:
        company_info = CompanyInfo.query.first()
        
        # Build splash screen config
        splash_config = {
            'logo': None,
            'welcome_text': 'خوش آمدید',
            'background_color': '#FFFFFF',
            'text_color': '#000000',
            'duration_seconds': 2,
            'animation_enabled': True
        }
        
        # Get logo if exists
        if company_info and company_info.logo:
            if company_info.logo.startswith('http'):
                splash_config['logo'] = company_info.logo
            else:
                splash_config['logo'] = url_for('static', filename=f'uploads/{company_info.logo}', _external=True)
        
        if company_info and company_info.company_name:
            splash_config['welcome_text'] = f'به {company_info.company_name} خوش آمدید'
        
        return jsonify({
            'success': True,
            'data': splash_config
        })
        
    except Exception as e:
        logger.error(f"Error getting splash config: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت تنظیمات صفحه ابتدایی',
            'code': 'SERVER_ERROR'
        }), 500

@mobile_api_bp.route('/rewards', methods=['GET'])
@jwt_required(optional=True)
def get_rewards():
    """دریافت لیست جوایز"""
    try:
        # Get user if authenticated
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            pass
        
        # Get active rewards
        rewards = Reward.query.filter_by(is_active=True).filter(
            or_(
                Reward.valid_from.is_(None),
                Reward.valid_from <= datetime.utcnow()
            ),
            or_(
                Reward.valid_until.is_(None),
                Reward.valid_until >= datetime.utcnow()
            )
        ).order_by(Reward.points_required).all()
        
        # Get user's wallet balance if authenticated
        user_points = 0
        if user:
            try:
                if hasattr(user, 'wallet') and user.wallet:
                    user_points = float(user.wallet.balance)
            except:
                pass
        
        rewards_list = []
        for reward in rewards:
            if reward.is_valid():
                rewards_list.append({
                    'id': reward.id,
                    'name': reward.name_fa or reward.name,
                    'description': reward.description_fa or reward.description or '',
                    'points_required': float(reward.points_required) if reward.points_required else 0,
                    'reward_type': reward.reward_type,
                    'discount_percentage': float(reward.discount_percentage) if reward.discount_percentage else None,
                    'discount_amount': float(reward.discount_amount) if reward.discount_amount else None,
                    'is_available': user_points >= (reward.points_required or 0) if user else False,
                    'user_points': user_points if user else 0
                })
        
        return jsonify({
            'success': True,
            'data': {
                'rewards': rewards_list,
                'user_points': user_points if user else None,
                'count': len(rewards_list)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting rewards: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطا در دریافت جوایز',
            'code': 'SERVER_ERROR'
        }), 500

