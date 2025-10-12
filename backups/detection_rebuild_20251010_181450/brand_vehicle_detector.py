"""
سیستم تشخیص خودکار برند و نوع خودرو
Brand and Vehicle Type Detection System
"""

import re
import json
import time
from typing import Dict, List, Optional, Tuple
from models import Brand, VehicleModel, VehicleType, Product, db


class BrandVehicleDetector:
    """کلاس تشخیص خودکار برند و نوع خودرو"""
    
    def __init__(self):
        self.brands_cache = {}
        self.vehicle_types_cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """بارگذاری کش برندها و انواع خودرو"""
        try:
            # بارگذاری برندها
            brands = Brand.query.filter_by(is_active=True).all()
            for brand in brands:
                # نام انگلیسی
                self.brands_cache[brand.name.lower()] = {
                    'id': brand.id,
                    'name': brand.name,
                    'name_fa': brand.name_fa,
                    'confidence': 'high'
                }
                # نام فارسی
                self.brands_cache[brand.name_fa] = {
                    'id': brand.id,
                    'name': brand.name,
                    'name_fa': brand.name_fa,
                    'confidence': 'high'
                }
            
            # بارگذاری انواع خودرو
            vehicle_types = VehicleType.query.all()
            for vt in vehicle_types:
                self.vehicle_types_cache[vt.name.lower()] = {
                    'id': vt.id,
                    'name': vt.name,
                    'confidence': 'high'
                }
                
                # اضافه کردن نام‌های فارسی رایج
                persian_mappings = {
                    'sedan': ['سدان', 'سدان'],
                    'SUV': ['شاسی‌بلند', 'شاسی بلند', 'شاسیبلند'],
                    'hatchback': ['هاچ‌بک', 'هاچ بک', 'هاچبک'],
                    'coupe': ['کوپه', 'کوپه'],
                    'convertible': ['کابریولت', 'کابریولت'],
                    'wagon': ['واگن', 'واگن'],
                    'pickup': ['پیکاپ', 'پیکاپ'],
                    'van': ['ون', 'ون'],
                    'truck': ['کامیون', 'کامیون'],
                    'bus': ['اتوبوس', 'اتوبوس']
                }
                
                if vt.name.lower() in persian_mappings:
                    for persian_name in persian_mappings[vt.name.lower()]:
                        self.vehicle_types_cache[persian_name] = {
                            'id': vt.id,
                            'name': vt.name,
                            'confidence': 'high'
                        }
                        
        except Exception as e:
            print(f"خطا در بارگذاری کش: {e}")
    
    def normalize_text(self, text: str) -> str:
        """نرمال‌سازی متن"""
        if not text:
            return ""
        
        # حذف فاصله‌های اضافی و تبدیل به حروف کوچک
        text = re.sub(r'\s+', ' ', text.strip().lower())
        
        # حذف کاراکترهای خاص
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        
        return text
    
    def detect_brand(self, product_name: str) -> Optional[Dict]:
        """تشخیص برند از نام محصول"""
        if not product_name:
            return None
        
        normalized_name = self.normalize_text(product_name)
        
        # جستجو برای برندها
        detected_brands = []
        
        for brand_key, brand_info in self.brands_cache.items():
            if brand_key in normalized_name:
                # محاسبه طول تطبیق برای اولویت‌بندی
                match_length = len(brand_key)
                detected_brands.append({
                    'brand_info': brand_info,
                    'match_length': match_length,
                    'position': normalized_name.find(brand_key)
                })
        
        if not detected_brands:
            return None
        
        # انتخاب برند با بیشترین طول تطبیق
        best_match = max(detected_brands, key=lambda x: x['match_length'])
        
        return best_match['brand_info']
    
    def detect_vehicle_types(self, product_name: str) -> List[Dict]:
        """تشخیص انواع خودرو از نام محصول"""
        if not product_name:
            return []
        
        normalized_name = self.normalize_text(product_name)
        detected_types = []
        
        for type_key, type_info in self.vehicle_types_cache.items():
            if type_key in normalized_name:
                detected_types.append(type_info)
        
        # حذف تکراری‌ها
        unique_types = []
        seen_ids = set()
        for vt in detected_types:
            if vt['id'] not in seen_ids:
                unique_types.append(vt)
                seen_ids.add(vt['id'])
        
        return unique_types
    
    def detect_brand_and_vehicle_types(self, product_name: str) -> Dict:
        """تشخیص برند و انواع خودرو از نام محصول"""
        start_time = time.time()
        
        try:
            # تشخیص برند
            detected_brand = self.detect_brand(product_name)
            
            # تشخیص انواع خودرو
            detected_vehicle_types = self.detect_vehicle_types(product_name)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'status': 'success',
                'data': {
                    'product_name': product_name,
                    'detected_brand': detected_brand,
                    'detected_vehicle_types': detected_vehicle_types,
                    'processing_time': processing_time,
                    'timestamp': time.time()
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error_code': 'DETECTION_ERROR',
                'message': f'خطا در تشخیص: {str(e)}',
                'details': str(e)
            }
    
    def batch_detect_products(self, product_ids: List[int] = None) -> Dict:
        """تشخیص دسته‌ای محصولات"""
        try:
            if product_ids:
                products = Product.query.filter(Product.id.in_(product_ids)).all()
            else:
                products = Product.query.filter_by(is_active=True).all()
            
            results = []
            updated_count = 0
            
            for product in products:
                detection_result = self.detect_brand_and_vehicle_types(product.name)
                
                if detection_result['status'] == 'success':
                    data = detection_result['data']
                    
                    # به‌روزرسانی برند محصول
                    if data['detected_brand']:
                        product.brand_id = data['detected_brand']['id']
                        updated_count += 1
                    
                    # به‌روزرسانی انواع خودرو
                    if data['detected_vehicle_types']:
                        vehicle_type_ids = [vt['id'] for vt in data['detected_vehicle_types']]
                        # حذف روابط قبلی
                        product.vehicle_types.clear()
                        # اضافه کردن روابط جدید
                        for vt_id in vehicle_type_ids:
                            vt = VehicleType.query.get(vt_id)
                            if vt:
                                product.vehicle_types.append(vt)
                    
                    results.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'detected_brand': data['detected_brand'],
                        'detected_vehicle_types': data['detected_vehicle_types']
                    })
            
            # ذخیره تغییرات
            db.session.commit()
            
            return {
                'status': 'success',
                'data': {
                    'total_processed': len(products),
                    'updated_count': updated_count,
                    'results': results
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'error_code': 'BATCH_DETECTION_ERROR',
                'message': f'خطا در تشخیص دسته‌ای: {str(e)}',
                'details': str(e)
            }
    
    def refresh_cache(self):
        """به‌روزرسانی کش"""
        self.brands_cache.clear()
        self.vehicle_types_cache.clear()
        self._load_cache()
    
    def get_detection_stats(self) -> Dict:
        """آمار تشخیص"""
        try:
            total_products = Product.query.count()
            products_with_brand = Product.query.filter(Product.brand_id.isnot(None)).count()
            products_with_vehicle_types = Product.query.join(Product.vehicle_types).count()
            
            return {
                'total_products': total_products,
                'products_with_brand': products_with_brand,
                'products_with_vehicle_types': products_with_vehicle_types,
                'brand_coverage': round((products_with_brand / total_products * 100) if total_products > 0 else 0, 2),
                'vehicle_type_coverage': round((products_with_vehicle_types / total_products * 100) if total_products > 0 else 0, 2)
            }
        except Exception as e:
            return {
                'error': f'خطا در دریافت آمار: {str(e)}'
            }


# نمونه سراسری - باید در application context ایجاد شود
detector = None

def get_detector():
    """دریافت نمونه detector در application context"""
    global detector
    if detector is None:
        detector = BrandVehicleDetector()
    return detector
