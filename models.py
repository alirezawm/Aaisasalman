from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import event, text
from datetime import datetime, timedelta
import json

# Create SQLAlchemy instance
db = SQLAlchemy()

def init_db(database):
    global db
    db = database

# Define models at module level
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(100))
    
    # Profile completion fields
    national_id = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.Text, nullable=True)
    landline_phone = db.Column(db.String(20), nullable=True)
    secondary_phone = db.Column(db.String(20), nullable=True)
    profile_completion_percentage = db.Column(db.Integer, default=0)
    profile_completed_at = db.Column(db.DateTime, nullable=True)
    notification_preferences = db.Column(db.Text, default='{}')
    
    # Enhanced user type and permissions
    user_type = db.Column(db.String(20), default='regular')  # admin, staff, bulk_buyer, regular
    is_bulk_buyer = db.Column(db.Boolean, default=False)
    bulk_buyer_approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    bulk_buyer_approved_at = db.Column(db.DateTime, nullable=True)
    bulk_buyer_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # User preferences
    preferred_brands = db.Column(db.Text)  # JSON string of brand IDs
    preferred_language = db.Column(db.String(5), default='fa')
    search_preferences = db.Column(db.Text)  # JSON string
    
    # Financial
    credit_limit = db.Column(db.Float, default=0)
    current_debt = db.Column(db.Float, default=0)
    current_credit = db.Column(db.Float, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    invoices = db.relationship('Invoice', foreign_keys='Invoice.user_id', backref='user', lazy=True)
    documents = db.relationship('UserDocument', backref='user', lazy=True)
    search_history = db.relationship('UserSearchHistory', backref='user', lazy=True)
    bulk_buyer_approver = db.relationship('User', foreign_keys=[bulk_buyer_approved_by], backref='approved_bulk_buyers', remote_side='User.id')
    
    def get_preferred_brands(self):
        """Get preferred brands as list"""
        if self.preferred_brands:
            return json.loads(self.preferred_brands)
        return []
    
    def set_preferred_brands(self, brand_ids):
        """Set preferred brands"""
        self.preferred_brands = json.dumps(brand_ids)
    
    def get_search_preferences(self):
        """Get search preferences as dict"""
        if self.search_preferences:
            return json.loads(self.search_preferences)
        return {}
    
    def set_search_preferences(self, preferences):
        """Set search preferences"""
        self.search_preferences = json.dumps(preferences)
    
    def get_roles(self, scope='site'):
        """Get user's roles for a specific scope"""
        return [ur.role for ur in self.user_roles if ur.is_active and ur.scope == scope]
    
    def has_role(self, role_slug, scope='site'):
        """Check if user has a specific role"""
        return any(ur.role.slug == role_slug and ur.is_active and ur.scope == scope for ur in self.user_roles)
    
    def has_permission(self, permission, scope='site'):
        """Check if user has a specific permission"""
        # Check role-based permissions
        for user_role in self.user_roles:
            if user_role.is_active and user_role.scope == scope:
                if user_role.role.has_permission(permission):
                    return True
        
        # For admin users, check if they have site.* permission
        if self.is_admin:
            # Check if any role has site.* permission
            for user_role in self.user_roles:
                if user_role.is_active and user_role.scope == scope:
                    if user_role.role.has_permission('site.*'):
                        return True
            # If no roles found but user is admin, allow access
            return True
        
        return False
    
    def assign_role(self, role, assigned_by, scope='site'):
        """Assign a role to user"""
        # Check if role already assigned
        existing = UserRole.query.filter_by(
            user_id=self.id, 
            role_id=role.id, 
            scope=scope
        ).first()
        
        if existing:
            existing.is_active = True
            existing.assigned_by = assigned_by
            existing.assigned_at = datetime.utcnow()
        else:
            user_role = UserRole(
                user_id=self.id,
                role_id=role.id,
                scope=scope,
                assigned_by=assigned_by
            )
            db.session.add(user_role)
    
    def revoke_role(self, role_slug, scope='site'):
        """Revoke a role from user"""
        user_role = UserRole.query.join(Role).filter(
            UserRole.user_id == self.id,
            Role.slug == role_slug,
            UserRole.scope == scope,
            UserRole.is_active == True
        ).first()
        
        if user_role:
            user_role.is_active = False
    
    def get_role_change_notification(self, role_name, action, changed_by):
        """Generate notification message for role changes"""
        if action == 'assigned':
            return f"نقش '{role_name}' به شما تخصیص داده شد توسط {changed_by}"
        elif action == 'revoked':
            return f"نقش '{role_name}' از شما گرفته شد توسط {changed_by}"
        return f"تغییر در نقش '{role_name}' توسط {changed_by}"
    
    def calculate_profile_completion(self):
        """محاسبه درصد تکمیل پروفایل"""
        total_fields = 7  # Reduced from 8 since email is now optional
        completed_fields = 0
        
        # فیلدهای اجباری
        if self.full_name:
            completed_fields += 1
        if self.phone:
            completed_fields += 1
        if self.username:
            completed_fields += 1
        
        # فیلدهای اختیاری
        if self.email:
            completed_fields += 1
        if self.national_id:
            completed_fields += 1
        if self.birth_date:
            completed_fields += 1
        if self.address:
            completed_fields += 1
        if self.landline_phone or self.secondary_phone:
            completed_fields += 1
        
        percentage = int((completed_fields / total_fields) * 100)
        self.profile_completion_percentage = percentage
        
        # اگر پروفایل کامل شد
        if percentage == 100 and not self.profile_completed_at:
            self.profile_completed_at = datetime.utcnow()
        
        return percentage
    
    def get_notification_preferences(self):
        """Get notification preferences as dict"""
        if self.notification_preferences:
            return json.loads(self.notification_preferences)
        return {}
    
    def set_notification_preferences(self, preferences):
        """Set notification preferences"""
        self.notification_preferences = json.dumps(preferences)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    name_fa = db.Column(db.String(100), unique=True, nullable=False)  # Persian name
    logo_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    country_of_origin = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='brand', lazy=True)
    vehicle_models = db.relationship('VehicleModel', backref='brand', lazy=True)
    
    def __repr__(self):
        return f'<Brand {self.name}>'

class VehicleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    model_name_fa = db.Column(db.String(100), nullable=False)  # Persian name
    year_from = db.Column(db.Integer)
    year_to = db.Column(db.Integer)
    body_type = db.Column(db.String(50))  # sedan, SUV, hatchback, etc.
    engine_type = db.Column(db.String(50))  # petrol, diesel, hybrid, electric
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', secondary='product_vehicle_models', backref='vehicle_models', lazy=True)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('brand_id', 'model_name', 'year_from', name='unique_brand_model_year'),)
    
    def __repr__(self):
        return f'<VehicleModel {self.brand.name} {self.model_name} {self.year_from}>'

class PartCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('part_category.id'))
    category_name = db.Column(db.String(100), nullable=False)
    category_name_fa = db.Column(db.String(100), nullable=False)  # Persian name
    description = db.Column(db.Text)
    icon_class = db.Column(db.String(50))  # FontAwesome class
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for hierarchical structure
    children = db.relationship('PartCategory', backref=db.backref('parent', remote_side=[id]))
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<PartCategory {self.category_name}>'

class PartSubcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('part_category.id'), nullable=False)
    subcategory_name = db.Column(db.String(100), nullable=False)
    subcategory_name_fa = db.Column(db.String(100), nullable=False)  # Persian name
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='subcategory', lazy=True)
    
    def __repr__(self):
        return f'<PartSubcategory {self.subcategory_name}>'

class VehicleType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', secondary='product_vehicle_types', backref='vehicle_types')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    oem_code = db.Column(db.String(50))  # Original Equipment Manufacturer code
    name = db.Column(db.String(200), nullable=False)
    name_fa = db.Column(db.String(200), nullable=False)  # Persian name
    description = db.Column(db.Text)
    description_fa = db.Column(db.Text)  # Persian description
    
    # Hierarchical relationships
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('part_category.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('part_subcategory.id'))
    
    # Compatibility - JSON field for multiple vehicle models
    compatible_models = db.Column(db.Text)  # JSON string of vehicle_model_ids
    
    # Pricing (in thousands of Rials)
    bulk_price_cash = db.Column(db.Float, nullable=False)
    retail_price_cash = db.Column(db.Float, nullable=False)
    bulk_price_check = db.Column(db.Float, nullable=False)
    retail_price_check = db.Column(db.Float, nullable=False)

    # ISACO warehouse 15 special pricing (thousands of Rials)
    isaco_cash = db.Column(db.Float, nullable=True)
    isaco_1m = db.Column(db.Float, nullable=True)
    isaco_2m = db.Column(db.Float, nullable=True)
    isaco_3m = db.Column(db.Float, nullable=True)

    # Visibility/control flags
    is_isaco_wh15 = db.Column(db.Boolean, default=False)
    
    # Inventory
    stock_quantity = db.Column(db.Integer, default=0)
    min_order_quantity = db.Column(db.Integer, default=1)
    max_order_quantity = db.Column(db.Integer)
    
    # Additional attributes
    weight_kg = db.Column(db.Float)
    dimensions = db.Column(db.Text)  # JSON string {length, width, height}
    material = db.Column(db.String(100))
    color = db.Column(db.String(50))
    
    # Images and media
    primary_image = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON string of image URLs
    technical_specs = db.Column(db.Text)  # JSON string
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text)  # JSON string of search tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Legacy fields for backward compatibility
    code = db.Column(db.String(50))  # Keep for backward compatibility
    image = db.Column(db.String(200))  # Keep for backward compatibility
    
    # Additional pricing fields
    settlement_period = db.Column(db.Integer, default=0)  # Days
    credit_amount = db.Column(db.Float, default=0)  # Credit amount for this product
    cash_discount_percentage = db.Column(db.Float, default=0)  # Discount percentage for cash payment
    
    def get_compatible_models(self):
        """Get compatible models as list"""
        if self.compatible_models:
            return json.loads(self.compatible_models)
        return []
    
    def set_compatible_models(self, model_ids):
        """Set compatible models"""
        self.compatible_models = json.dumps(model_ids)
    
    def get_dimensions(self):
        """Get dimensions as dict"""
        if self.dimensions:
            return json.loads(self.dimensions)
        return {}
    
    def set_dimensions(self, dimensions):
        """Set dimensions"""
        self.dimensions = json.dumps(dimensions)
    
    def get_images(self):
        """Get images as list"""
        if self.images:
            return json.loads(self.images)
        return []
    
    def set_images(self, image_urls):
        """Set images"""
        self.images = json.dumps(image_urls)
    
    def get_technical_specs(self):
        """Get technical specs as dict"""
        if self.technical_specs:
            return json.loads(self.technical_specs)
        return {}
    
    def set_technical_specs(self, specs):
        """Set technical specs"""
        self.technical_specs = json.dumps(specs)
    
    def get_tags(self):
        """Get tags as list"""
        if self.tags:
            return json.loads(self.tags)
        return []
    
    def set_tags(self, tag_list):
        """Set tags"""
        self.tags = json.dumps(tag_list)
    
    def __repr__(self):
        return f'<Product {self.sku} - {self.name}>'

class UserSearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_query = db.Column(db.String(255))
    search_filters = db.Column(db.Text)  # JSON string
    results_count = db.Column(db.Integer)
    clicked_product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='search_clicks')
    
    def get_search_filters(self):
        """Get search filters as dict"""
        if self.search_filters:
            return json.loads(self.search_filters)
        return {}
    
    def set_search_filters(self, filters):
        """Set search filters"""
        self.search_filters = json.dumps(filters)
    
    def __repr__(self):
        return f'<UserSearchHistory {self.user.username} - {self.search_query}>'

class ProductSearchIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    search_keywords = db.Column(db.Text)  # JSON string of searchable keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='search_index')
    
    def get_search_keywords(self):
        """Get search keywords as list"""
        if self.search_keywords:
            return json.loads(self.search_keywords)
        return []
    
    def set_search_keywords(self, keywords):
        """Set search keywords"""
        self.search_keywords = json.dumps(keywords)
    
    def __repr__(self):
        return f'<ProductSearchIndex {self.product.sku}>'

class ProductVehicleType(db.Model):
    __tablename__ = 'product_vehicle_types'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_type.id'), primary_key=True)

class ProductVehicleModel(db.Model):
    __tablename__ = 'product_vehicle_models'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    vehicle_model_id = db.Column(db.Integer, db.ForeignKey('vehicle_model.id'), primary_key=True)

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_type = db.Column(db.String(10), nullable=False)  # 'cash' or 'check'
    # ISACO specific price plan for warehouse 15 items
    price_plan = db.Column(db.String(20), nullable=True)  # isaco_cash, isaco_1m, isaco_2m, isaco_3m
    unit_price = db.Column(db.Float, nullable=False)  # Store the actual unit price
    discount_amount = db.Column(db.Float, default=0)
    discount_type = db.Column(db.String(20), default='fixed')  # 'percentage' or 'fixed'
    session_id = db.Column(db.String(100), db.ForeignKey('cart_session.id'), nullable=True)  # For guest users
    is_saved_for_later = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    # Relationships
    product = db.relationship('Product', backref='cart_items')
    user = db.relationship('User', backref='cart_items')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_cart_user_product_price', 'user_id', 'product_id', 'price_type'),
        db.Index('idx_cart_session', 'session_id'),
        db.Index('idx_cart_expires', 'expires_at'),
    )
    
    def get_total_price(self):
        """Calculate total price with discount applied"""
        base_price = self.quantity * self.unit_price
        if self.discount_type == 'percentage':
            discount = base_price * (self.discount_amount / 100)
        else:
            discount = self.discount_amount
        return max(0, base_price - discount)
    
    def is_expired(self):
        """Check if cart item has expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'price_type': self.price_type,
            'unit_price': self.unit_price,
            'total_price': self.get_total_price(),
            'discount_amount': self.discount_amount,
            'discount_type': self.discount_type,
            'is_saved_for_later': self.is_saved_for_later,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CartSession(db.Model):
    __tablename__ = 'cart_session'
    
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for guests
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='cart_sessions')
    cart_items = db.relationship('Cart', backref='cart_session', lazy=True)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def is_expired(self, hours=24):
        """Check if session has expired"""
        return datetime.utcnow() > (self.last_activity + timedelta(hours=hours))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_active': self.is_active
        }

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product', backref='wishlist_items')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),
    )
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_price': self.product.retail_price_cash if self.product else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CartNotification(db.Model):
    __tablename__ = 'cart_notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'price_drop', 'stock_alert', 'abandoned_cart', etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=True)  # JSON data
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='cart_notifications')
    
    def get_data(self):
        """Get parsed JSON data"""
        if self.data:
            try:
                return json.loads(self.data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_data(self, data_dict):
        """Set JSON data"""
        self.data = json.dumps(data_dict)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.get_data(),
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(10), nullable=False)  # 'cash' or 'check'
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Approval tracking fields
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, under_review
    approval_date = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # admin who approved
    rejection_reason = db.Column(db.Text)  # reason for rejection
    admin_notes = db.Column(db.Text)  # admin notes about the invoice
    
    # Enhanced notification tracking
    admin_review_notes = db.Column(db.Text)  # admin notes during review process
    notification_sent = db.Column(db.Boolean, default=False)  # whether notification was sent to customer
    notification_sent_at = db.Column(db.DateTime)  # when last notification was sent
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('InvoiceDocument', backref='invoice', lazy=True, cascade='all, delete-orphan')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_invoices')

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    price_type = db.Column(db.String(10), nullable=False)  # 'cash' or 'check'
    price_plan = db.Column(db.String(20), nullable=True)  # ISACO plan if applicable
    
    # Relationships
    product = db.relationship('Product', backref='invoice_items')

class InvoiceDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)  # 'check' or 'receipt'
    file_path = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Document approval tracking
    is_approved = db.Column(db.Boolean, default=False)
    approval_date = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    rejection_reason = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    # Relationships
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_documents')

class UserDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # 'identity', 'credit', etc.
    file_path = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Festival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    discount_percentage = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CompanyInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    bulk_purchase_conditions = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON string of permissions
    scope = db.Column(db.String(20), default='site')  # site, tenant, store
    is_active = db.Column(db.Boolean, default=True)
    is_immutable = db.Column(db.Boolean, default=False)  # Core roles that cannot be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_roles = db.relationship('UserRole', backref='role', lazy=True, cascade='all, delete-orphan')
    
    def get_permissions(self):
        """Get permissions as list"""
        if self.permissions:
            return json.loads(self.permissions)
        return []
    
    def set_permissions(self, permissions_list):
        """Set permissions"""
        self.permissions = json.dumps(permissions_list)
    
    def has_permission(self, permission):
        """Check if role has specific permission"""
        role_permissions = self.get_permissions()
        return permission in role_permissions or any(p.startswith(permission.split('.')[0] + '.*') for p in role_permissions)
    
    def __repr__(self):
        return f'<Role {self.slug}>'

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    scope = db.Column(db.String(20), default='site')
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='user_roles')
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='assigned_roles')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', 'scope', name='unique_user_role_scope'),)
    
    def __repr__(self):
        return f'<UserRole {self.user.username} - {self.role.slug}>'

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # assign_role, create_role, delete_role, revoke_role
    target_type = db.Column(db.String(20), nullable=False)  # user, role
    target_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text)  # JSON string with additional details
    request_id = db.Column(db.String(100))  # For request tracking
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    actor = db.relationship('User', backref='audit_logs')
    
    def get_details(self):
        """Get details as dict"""
        if self.details:
            return json.loads(self.details)
        return {}
    
    def set_details(self, details_dict):
        """Set details"""
        self.details = json.dumps(details_dict)
    
    def __repr__(self):
        return f'<AuditLog {self.actor.username} - {self.action}>'

class UserNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # role_change, system, invoice_approved, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Invoice-related notification fields
    related_invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    notification_action = db.Column(db.String(50), nullable=True)  # approve, reject, review
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    related_invoice = db.relationship('Invoice', backref='notifications')
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<UserNotification {self.user.username} - {self.title}>'

class ColorScheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Color values
    background_color = db.Column(db.String(7), nullable=False)  # Hex color
    primary_text_color = db.Column(db.String(7), nullable=False)
    secondary_text_color = db.Column(db.String(7), nullable=False)
    accent_text_color = db.Column(db.String(7), nullable=False)
    
    # Contrast ratios
    primary_contrast_ratio = db.Column(db.Float, nullable=False)
    secondary_contrast_ratio = db.Column(db.Float, nullable=False)
    accent_contrast_ratio = db.Column(db.Float, nullable=False)
    
    # Accessibility levels
    primary_accessibility_level = db.Column(db.String(10), nullable=False)  # AA, AAA, Fail
    secondary_accessibility_level = db.Column(db.String(10), nullable=False)
    accent_accessibility_level = db.Column(db.String(10), nullable=False)
    
    # Scheme properties
    is_light_background = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Usage tracking
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_color_schemes')
    
    def get_colors_dict(self):
        """Get colors as dictionary"""
        return {
            'background': self.background_color,
            'primary': self.primary_text_color,
            'secondary': self.secondary_text_color,
            'accent': self.accent_text_color
        }
    
    def get_contrast_ratios_dict(self):
        """Get contrast ratios as dictionary"""
        return {
            'primary': self.primary_contrast_ratio,
            'secondary': self.secondary_contrast_ratio,
            'accent': self.accent_contrast_ratio
        }
    
    def get_accessibility_levels_dict(self):
        """Get accessibility levels as dictionary"""
        return {
            'primary': self.primary_accessibility_level,
            'secondary': self.secondary_accessibility_level,
            'accent': self.accent_accessibility_level
        }
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    def is_accessible(self, level='AA'):
        """Check if scheme meets accessibility requirements"""
        if level == 'AAA':
            return (self.primary_accessibility_level == 'AAA' and 
                    self.secondary_accessibility_level == 'AAA' and 
                    self.accent_accessibility_level == 'AAA')
        else:  # AA
            return (self.primary_accessibility_level in ['AA', 'AAA'] and 
                    self.secondary_accessibility_level in ['AA', 'AAA'] and 
                    self.accent_accessibility_level in ['AA', 'AAA'])
    
    def generate_css(self):
        """Generate CSS for this color scheme"""
        return f""":root {{
    --bg-color: {self.background_color};
    --text-primary: {self.primary_text_color};
    --text-secondary: {self.secondary_text_color};
    --text-accent: {self.accent_text_color};
}}

.text-primary-optimized {{ color: var(--text-primary); }}
.text-secondary-optimized {{ color: var(--text-secondary); }}
.text-accent-optimized {{ color: var(--text-accent); }}
.bg-optimized {{ background-color: var(--bg-color); }}"""
    
    def generate_html_example(self):
        """Generate HTML example for this color scheme"""
        return f"""<div class="bg-optimized text-primary-optimized">
    <h1 class="text-primary-optimized">عنوان اصلی</h1>
    <p class="text-secondary-optimized">متن ثانویه</p>
    <a href="#" class="text-accent-optimized">لینک تأکیدی</a>
</div>"""
    
    def __repr__(self):
        return f'<ColorScheme {self.name} - {self.background_color}>'

# ==================== TADBIR ACCOUNTING SYSTEM MODELS ====================

class TadbirSyncLog(db.Model):
    """جدول لاگ همگام‌سازی تدبیر"""
    __tablename__ = 'tadbir_sync_log'
    
    id = db.Column(db.Integer, primary_key=True)
    sync_type = db.Column(db.String(50), nullable=False)  # products, inventory, prices, full
    status = db.Column(db.String(20), nullable=False)  # started, completed, failed, cancelled
    records_processed = db.Column(db.Integer, default=0)
    records_successful = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<TadbirSyncLog {self.sync_type} - {self.status}>'

class TadbirProductCache(db.Model):
    """کش کالاهای تدبیر"""
    __tablename__ = 'tadbir_product_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(500))
    alias = db.Column(db.String(4000))
    unit = db.Column(db.String(20))
    techspec = db.Column(db.String(50))
    barcode = db.Column(db.String(20))
    is_item = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    tadbir_guid = db.Column(db.String(36))
    last_update = db.Column(db.DateTime)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TadbirProductCache {self.item_code}>'

class TadbirPriceCache(db.Model):
    """کش قیمت‌های تدبیر"""
    __tablename__ = 'tadbir_price_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), nullable=False)
    price_list_key = db.Column(db.Integer, nullable=False)
    price_type = db.Column(db.String(20), nullable=False)  # retail_check, bulk_check, bulk_cash
    base_price = db.Column(db.Numeric(18, 2))
    final_price = db.Column(db.Numeric(18, 2))
    discount_percentage = db.Column(db.Numeric(5, 2))
    discount_amount = db.Column(db.Numeric(18, 2))
    min_order = db.Column(db.Numeric(18, 5))
    tadbir_guid = db.Column(db.String(36))
    last_update = db.Column(db.DateTime)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for efficient queries
    __table_args__ = (
        db.Index('idx_tadbir_price_item_type', 'item_code', 'price_type'),
        db.Index('idx_tadbir_price_list_key', 'price_list_key'),
    )
    
    def __repr__(self):
        return f'<TadbirPriceCache {self.item_code} - {self.price_type}>'

class TadbirInventoryCache(db.Model):
    """کش موجودی تدبیر"""
    __tablename__ = 'tadbir_inventory_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), nullable=False)
    stock_code = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Numeric(18, 5))
    reserved_quantity = db.Column(db.Numeric(18, 5))
    available_quantity = db.Column(db.Numeric(18, 5))
    last_update = db.Column(db.DateTime)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for efficient queries
    __table_args__ = (
        db.Index('idx_tadbir_inventory_item_stock', 'item_code', 'stock_code'),
        db.UniqueConstraint('item_code', 'stock_code', name='unique_item_stock'),
    )
    
    def __repr__(self):
        return f'<TadbirInventoryCache {self.item_code} - {self.stock_code}>'

class TadbirSyncSettings(db.Model):
    """تنظیمات همگام‌سازی تدبیر"""
    __tablename__ = 'tadbir_sync_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    updater = db.relationship('User', backref='tadbir_settings_updates')
    
    def __repr__(self):
        return f'<TadbirSyncSettings {self.setting_key}>'

# ==================== POINTS SYSTEM MODELS ====================

class UserPoints(db.Model):
    """جدول امتیازات کاربران"""
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    current_points = db.Column(db.Integer, default=0)
    total_earned_points = db.Column(db.Integer, default=0)
    total_spent_points = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='points')
    
    def __repr__(self):
        return f'<UserPoints {self.user.username} - {self.current_points}>'

class PointsTransaction(db.Model):
    """جدول تراکنش‌های امتیازی"""
    __tablename__ = 'points_transaction'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_amount = db.Column(db.Integer, nullable=False)  # مثبت برای کسب، منفی برای خرج
    transaction_type = db.Column(db.String(20), nullable=False)  # earn, spend, expire, bonus
    source_type = db.Column(db.String(30), nullable=False)  # purchase, bonus, admin_adjustment, reward_redemption
    source_id = db.Column(db.Integer)  # شناسه منبع (invoice_id, reward_id, etc.)
    description = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)  # تاریخ انقضا امتیاز
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='points_transactions')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_points_transaction_user_id', 'user_id'),
        db.Index('idx_points_transaction_type', 'transaction_type'),
        db.Index('idx_points_transaction_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f'<PointsTransaction {self.user.username} - {self.points_amount}>'

class Reward(db.Model):
    """جدول جوایز"""
    __tablename__ = 'reward'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_fa = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    description_fa = db.Column(db.Text)
    points_required = db.Column(db.Float, nullable=False)  # Changed to Float to support decimal points
    discount_percentage = db.Column(db.Float)  # درصد تخفیف
    discount_amount = db.Column(db.Float)  # مقدار تخفیف ثابت
    reward_type = db.Column(db.String(30), nullable=False)  # discount_percentage, discount_amount, free_shipping, product
    is_active = db.Column(db.Boolean, default=True)
    max_redemptions = db.Column(db.Integer)  # حداکثر تعداد استفاده
    current_redemptions = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    redemptions = db.relationship('RewardRedemption', backref='reward', lazy=True)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_reward_active', 'is_active'),
        db.Index('idx_reward_points', 'points_required'),
    )
    
    def is_valid(self):
        """بررسی اعتبار جایزه"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_redemptions and self.current_redemptions >= self.max_redemptions:
            return False
        return True
    
    def __repr__(self):
        return f'<Reward {self.name_fa} - {self.points_required} points>'

class RewardRedemption(db.Model):
    """جدول استفاده از جوایز"""
    __tablename__ = 'reward_redemption'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))  # فاکتور مرتبط
    used_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, used, expired, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='reward_redemptions')
    invoice = db.relationship('Invoice', backref='reward_redemptions')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_reward_redemption_user_id', 'user_id'),
        db.Index('idx_reward_redemption_status', 'status'),
    )
    
    def __repr__(self):
        return f'<RewardRedemption {self.user.username} - {self.reward.name_fa}>'

class UserLevel(db.Model):
    """جدول سطح‌بندی کاربران"""
    __tablename__ = 'user_level'
    
    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(50), nullable=False)
    level_name_fa = db.Column(db.String(50), nullable=False)
    min_points = db.Column(db.Float, nullable=False)  # Changed to Float to support decimal points
    max_points = db.Column(db.Float)  # None برای سطح بالاترین (Changed to Float to support decimal points)
    discount_percentage = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_level_points', 'min_points', 'max_points'),
    )
    
    def __repr__(self):
        return f'<UserLevel {self.level_name_fa} - {self.min_points}+>'

class PointsRule(db.Model):
    """جدول قوانین امتیازدهی"""
    __tablename__ = 'points_rule'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    rule_name_fa = db.Column(db.String(100), nullable=False)
    points_per_100k_rials = db.Column(db.Float, default=0.5)  # امتیاز به ازای هر 100 هزار ریال (reduced by 3 digits)
    bonus_points_per_product = db.Column(db.Float, default=0.05)  # امتیاز اضافی به ازای هر محصول (reduced by 3 digits)
    max_bonus_points = db.Column(db.Float, default=1)  # حداکثر امتیاز اضافی (reduced by 3 digits)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_points_rule_active', 'is_active'),
    )
    
    def is_valid(self):
        """بررسی اعتبار قانون"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True
    
    def __repr__(self):
        return f'<PointsRule {self.rule_name_fa} - {self.points_per_100k_rials} points/100k>'

# ==================== DATA INTEGRITY EVENTS ====================

@event.listens_for(VehicleType, 'before_delete')
def move_products_to_misc_before_vehicle_type_delete(mapper, connection, target):
    """Automatically reassign all product links from the deleting VehicleType to the
    'misc' VehicleType, creating it if it doesn't exist, then remove old links.

    This ensures that deleting a VehicleType never fails due to existing product
    associations and that products remain categorized under a fallback type.
    """
    # Ensure 'misc' VehicleType exists and get its id
    misc_id_row = connection.execute(text(
        "SELECT id FROM vehicle_type WHERE name = :name LIMIT 1"
    ), {"name": "misc"}).fetchone()

    if misc_id_row is None:
        connection.execute(text(
            "INSERT INTO vehicle_type (name, created_at) VALUES (:name, CURRENT_TIMESTAMP)"
        ), {"name": "misc"})
        misc_id_row = connection.execute(text(
            "SELECT id FROM vehicle_type WHERE name = :name LIMIT 1"
        ), {"name": "misc"}).fetchone()

    misc_id = misc_id_row[0]

    # Move links from the deleting type to 'misc' (avoid duplicates)
    # SQLite supports INSERT OR IGNORE to skip duplicates on the composite PK
    connection.execute(text(
        """
        INSERT OR IGNORE INTO product_vehicle_types (product_id, vehicle_type_id)
        SELECT product_id, :misc_id
        FROM product_vehicle_types
        WHERE vehicle_type_id = :old_id
        """
    ), {"misc_id": misc_id, "old_id": target.id})

    # Remove old links to the deleting type
    connection.execute(text(
        "DELETE FROM product_vehicle_types WHERE vehicle_type_id = :old_id"
    ), {"old_id": target.id})
