from flask import Flask
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asia_salman.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# SQLite-specific settings for better concurrency handling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'timeout': 30,  # 30 seconds timeout for database locks
        'check_same_thread': False  # Allow SQLite to be accessed from multiple threads
    },
    'pool_pre_ping': True,  # Verify connections before using them
    'pool_recycle': 3600,  # Recycle connections after 1 hour
}

# Create upload directories
os.makedirs('uploads/products', exist_ok=True)
os.makedirs('uploads/logos', exist_ok=True)
os.makedirs('uploads/documents', exist_ok=True)
os.makedirs('uploads/receipts', exist_ok=True)

# Import models first to get the db instance
import models

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the database with the Flask app
models.db.init_app(app)

# Set up user loader
@login_manager.user_loader
def load_user(user_id):
    from sqlalchemy.orm import joinedload
    # Load user with notifications to avoid lazy loading issues
    return models.User.query.options(
        joinedload(models.User.notifications)
    ).get(int(user_id))

# Import routes after models are defined
from routes import *

# Register Detection API Blueprint
from detection_api import detection_bp
if 'detection_api' not in app.blueprints:
    app.register_blueprint(detection_bp)

# Define format_price function here to avoid circular import
def format_price(price):
    """Format price for display - prices are stored in thousands Rials, display as full Rials"""
    if price is None or price == 0:
        return "0 ريال"
    # Convert from thousands Rials to full Rials
    full_price = price * 1000
    # Format with 0 decimal places for full Rials
    price_formatted = f"{full_price:,.0f}"
    return f"{price_formatted} ريال"

# Import Persian date utilities
from persian_date_utils import (
    persian_date_filter, 
    persian_datetime_filter, 
    persian_date_pretty_filter, 
    persian_datetime_pretty_filter
)

# CSRF Token function
def csrf_token():
    """Generate CSRF token for forms"""
    import secrets
    return secrets.token_hex(16)

# Define helper function here to avoid circular import
def can_see_bulk_prices(user):
    """Check if user can see bulk prices (must be bulk buyer AND approved)"""
    return user and user.is_authenticated and user.is_bulk_buyer and user.bulk_buyer_approval_status == 'approved'

# Make functions available in templates
app.jinja_env.globals.update(format_price=format_price, csrf_token=csrf_token, can_see_bulk_prices=can_see_bulk_prices)

# Register Persian date filters
app.jinja_env.filters['persian_date'] = persian_date_filter
app.jinja_env.filters['persian_datetime'] = persian_datetime_filter
app.jinja_env.filters['persian_date_pretty'] = persian_date_pretty_filter
app.jinja_env.filters['persian_datetime_pretty'] = persian_datetime_pretty_filter

# Context processor to provide unread notifications count
@app.context_processor
def inject_unread_notifications_count():
    """Make unread notifications count available in all templates"""
    from flask_login import current_user
    if current_user.is_authenticated:
        try:
            # Query directly instead of using lazy-loaded relationship
            unread_count = models.UserNotification.query.filter_by(
                user_id=current_user.id, 
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
        except Exception:
            return {'unread_notifications_count': 0}
    return {'unread_notifications_count': 0}

if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
        
        # Enable WAL mode for SQLite to improve concurrent access
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine
            
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                if 'sqlite' in str(dbapi_conn):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA busy_timeout=30000")  # 30 seconds
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.close()
            
            print("SQLite WAL mode and optimizations enabled")
        except Exception as e:
            print(f"Failed to enable SQLite optimizations: {e}")
        
        # Initialize Tadbir scheduler
        try:
            from tadbir_scheduler_service import get_scheduler
            scheduler = get_scheduler()
            scheduler.start_scheduler()
            print("Tadbir scheduler started successfully")
        except Exception as e:
            print(f"Failed to start Tadbir scheduler: {e}")
    
    # Ensure proper cleanup on shutdown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        models.db.session.remove()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
