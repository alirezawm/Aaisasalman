"""
مدل‌های دیتابیس برای سیستم تشخیص خودکار
Database Models for Auto-Detection System
"""

from models import db
from datetime import datetime

class DetectionPattern(db.Model):
    """الگوهای تشخیص"""
    __tablename__ = 'detection_pattern'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(20), nullable=False)  # brand, vehicle_type, model
    pattern = db.Column(db.String(200), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.String(20), nullable=False)
    confidence_weight = db.Column(db.Float, default=1.0)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DetectionLog(db.Model):
    """لاگ تشخیص‌ها"""
    __tablename__ = 'detection_log'
    
    id = db.Column(db.Integer, primary_key=True)
    input_text = db.Column(db.String(500), nullable=False)
    detected_brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    detected_vehicle_types = db.Column(db.Text)  # JSON
    confidence_scores = db.Column(db.Text)  # JSON
    algorithm_used = db.Column(db.String(50))
    processing_time_ms = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    verification_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DetectionFeedback(db.Model):
    """بازخورد تشخیص"""
    __tablename__ = 'detection_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    detection_log_id = db.Column(db.Integer, db.ForeignKey('detection_log.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_correct = db.Column(db.Boolean, nullable=False)
    correct_brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    correct_vehicle_types = db.Column(db.Text)  # JSON
    feedback_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BrandAlias(db.Model):
    """نام‌های مستعار برند"""
    __tablename__ = 'brand_alias'
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    alias = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(5), nullable=False)  # fa, en
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('brand_id', 'alias', name='unique_brand_alias'),)

class VehicleTypeAlias(db.Model):
    """نام‌های مستعار نوع خودرو"""
    __tablename__ = 'vehicle_type_alias'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_type.id'), nullable=False)
    alias = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(5), nullable=False)  # fa, en
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('vehicle_type_id', 'alias', name='unique_vtype_alias'),)

class DetectionStatistics(db.Model):
    """آمار تشخیص"""
    __tablename__ = 'detection_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_detections = db.Column(db.Integer, default=0)
    successful_detections = db.Column(db.Integer, default=0)
    failed_detections = db.Column(db.Integer, default=0)
    average_confidence = db.Column(db.Float, default=0.0)
    average_processing_time = db.Column(db.Float, default=0.0)
    brands_detected = db.Column(db.Text)  # JSON
    vehicle_types_detected = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
