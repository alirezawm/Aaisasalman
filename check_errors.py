"""
بررسی خطاهای سیستم
Check System Errors
"""

import sys
import traceback

def check_imports():
    """بررسی import ها"""
    print("\n" + "="*60)
    print("بررسی Import ها")
    print("="*60)
    
    modules_to_check = [
        ('app', 'Flask app'),
        ('models', 'Models'),
        ('detection_models', 'Detection Models'),
        ('detection_service', 'Detection Service'),
        ('detection_api', 'Detection API'),
        ('brand_vehicle_detector', 'Brand Vehicle Detector'),
    ]
    
    errors = []
    
    for module_name, description in modules_to_check:
        try:
            __import__(module_name)
            print(f"✓ {description:30} - OK")
        except Exception as e:
            print(f"✗ {description:30} - خطا: {str(e)}")
            errors.append((module_name, str(e)))
    
    return errors


def check_app_context():
    """بررسی app context"""
    print("\n" + "="*60)
    print("بررسی App Context")
    print("="*60)
    
    try:
        from app import app
        with app.app_context():
            print("✓ App context کار می‌کند")
            return True
    except Exception as e:
        print(f"✗ App context خطا: {str(e)}")
        traceback.print_exc()
        return False


def check_database():
    """بررسی دیتابیس"""
    print("\n" + "="*60)
    print("بررسی دیتابیس")
    print("="*60)
    
    try:
        from app import app
        from models import db, Brand, VehicleType, Product
        from detection_models import BrandAlias, VehicleTypeAlias
        
        with app.app_context():
            # بررسی اتصال
            db.session.execute(db.text('SELECT 1'))
            print("✓ اتصال دیتابیس OK")
            
            # بررسی جداول
            brands_count = Brand.query.count()
            print(f"✓ جدول Brand: {brands_count} رکورد")
            
            types_count = VehicleType.query.count()
            print(f"✓ جدول VehicleType: {types_count} رکورد")
            
            products_count = Product.query.count()
            print(f"✓ جدول Product: {products_count} رکورد")
            
            aliases_count = BrandAlias.query.count()
            print(f"✓ جدول BrandAlias: {aliases_count} رکورد")
            
            type_aliases_count = VehicleTypeAlias.query.count()
            print(f"✓ جدول VehicleTypeAlias: {type_aliases_count} رکورد")
            
            return True
            
    except Exception as e:
        print(f"✗ خطا در دیتابیس: {str(e)}")
        traceback.print_exc()
        return False


def check_detector():
    """بررسی detector"""
    print("\n" + "="*60)
    print("بررسی Detector")
    print("="*60)
    
    try:
        from app import app
        from brand_vehicle_detector import get_detector
        
        with app.app_context():
            detector = get_detector()
            print("✓ Detector ایجاد شد")
            
            # تست تشخیص
            result = detector.detect_brand_and_vehicle_types("تست تویوتا")
            
            if result['status'] == 'success':
                print("✓ تشخیص کار می‌کند")
                return True
            else:
                print(f"✗ خطا در تشخیص: {result.get('message', 'نامشخص')}")
                return False
                
    except Exception as e:
        print(f"✗ خطا در Detector: {str(e)}")
        traceback.print_exc()
        return False


def check_api():
    """بررسی API"""
    print("\n" + "="*60)
    print("بررسی API")
    print("="*60)
    
    try:
        from app import app
        from detection_api import detection_bp
        
        # بررسی blueprint
        if detection_bp in app.blueprints.values():
            print("✓ Detection API Blueprint ثبت شده")
        else:
            print("✗ Detection API Blueprint ثبت نشده")
            return False
        
        # بررسی routes
        routes = [rule.rule for rule in app.url_map.iter_rules() if 'detection' in rule.rule]
        
        print(f"✓ تعداد route های detection: {len(routes)}")
        for route in routes:
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"✗ خطا در API: {str(e)}")
        traceback.print_exc()
        return False


def check_service():
    """بررسی Service"""
    print("\n" + "="*60)
    print("بررسی Service")
    print("="*60)
    
    try:
        from app import app
        from detection_service import get_detection_service
        
        with app.app_context():
            service = get_detection_service()
            print("✓ Service ایجاد شد")
            
            # تست سرویس
            result = service.detect_single("تست هیوندای")
            
            if result['status'] == 'success':
                print("✓ Service کار می‌کند")
                return True
            else:
                print(f"✗ خطا در Service: {result.get('message', 'نامشخص')}")
                return False
                
    except Exception as e:
        print(f"✗ خطا در Service: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """اجرای همه بررسی‌ها"""
    print("\n" + "="*60)
    print("بررسی کامل سیستم تشخیص خودکار")
    print("="*60)
    
    results = {
        'imports': False,
        'app_context': False,
        'database': False,
        'detector': False,
        'api': False,
        'service': False,
    }
    
    # اجرای بررسی‌ها
    import_errors = check_imports()
    results['imports'] = len(import_errors) == 0
    
    if results['imports']:
        results['app_context'] = check_app_context()
        
        if results['app_context']:
            results['database'] = check_database()
            results['detector'] = check_detector()
            results['api'] = check_api()
            results['service'] = check_service()
    
    # نمایش نتایج
    print("\n" + "="*60)
    print("نتیجه نهایی")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✓ OK" if passed else "✗ خطا"
        print(f"{check_name:20} : {status}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✓✓✓ همه چیز OK است! سیستم آماده است ✓✓✓")
    else:
        print("✗✗✗ خطاهایی وجود دارد! ✗✗✗")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

