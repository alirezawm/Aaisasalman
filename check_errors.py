"""
بررسی خطاهای سیستم
Check System Errors
"""

import sys
import traceback

def check_imports():
    """بررسی import ها"""
    print("\n" + "="*60)
    print("Checking Imports")
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
            print(f"OK {description:30} - OK")
        except Exception as e:
            print(f"X {description:30} - Error: {str(e)}")
            errors.append((module_name, str(e)))
    
    return errors


def check_app_context():
    """بررسی app context"""
    print("\n" + "="*60)
    print("Checking App Context")
    print("="*60)
    
    try:
        from app import app
        with app.app_context():
            print("OK App context is working")
            return True
    except Exception as e:
        print(f"X App context error: {str(e)}")
        traceback.print_exc()
        return False


def check_database():
    """بررسی دیتابیس"""
    print("\n" + "="*60)
    print("Checking Database")
    print("="*60)
    
    try:
        from app import app
        from models import db, Brand, VehicleType, Product
        from detection_models import BrandAlias, VehicleTypeAlias
        
        with app.app_context():
            # بررسی اتصال
            db.session.execute(db.text('SELECT 1'))
            print("OK Database connection OK")
            
            # بررسی جداول
            brands_count = Brand.query.count()
            print(f"OK Brand table: {brands_count} records")
            
            types_count = VehicleType.query.count()
            print(f"OK VehicleType table: {types_count} records")
            
            products_count = Product.query.count()
            print(f"OK Product table: {products_count} records")
            
            aliases_count = BrandAlias.query.count()
            print(f"OK BrandAlias table: {aliases_count} records")
            
            type_aliases_count = VehicleTypeAlias.query.count()
            print(f"OK VehicleTypeAlias table: {type_aliases_count} records")
            
            return True
            
    except Exception as e:
        print(f"X Database error: {str(e)}")
        traceback.print_exc()
        return False


def check_detector():
    """بررسی detector"""
    print("\n" + "="*60)
    print("Checking Detector")
    print("="*60)
    
    try:
        from app import app
        from brand_vehicle_detector import get_detector
        
        with app.app_context():
            detector = get_detector()
            print("OK Detector created")
            
            # تست تشخیص
            result = detector.detect_brand_and_vehicle_types("تست تویوتا")
            
            if result['status'] == 'success':
                print("OK Detection is working")
                return True
            else:
                print(f"X Detection error: {result.get('message', 'Unknown')}")
                return False
                
    except Exception as e:
        print(f"X Detector error: {str(e)}")
        traceback.print_exc()
        return False


def check_api():
    """بررسی API"""
    print("\n" + "="*60)
    print("Checking API")
    print("="*60)
    
    try:
        from app import app
        from detection_api import detection_bp
        
        # بررسی blueprint
        if detection_bp in app.blueprints.values():
            print("OK Detection API Blueprint registered")
        else:
            print("X Detection API Blueprint not registered")
            return False
        
        # بررسی routes
        routes = [rule.rule for rule in app.url_map.iter_rules() if 'detection' in rule.rule]
        
        print(f"OK Number of detection routes: {len(routes)}")
        for route in routes:
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"X API error: {str(e)}")
        traceback.print_exc()
        return False


def check_service():
    """بررسی Service"""
    print("\n" + "="*60)
    print("Checking Service")
    print("="*60)
    
    try:
        from app import app
        from detection_service import get_detection_service
        
        with app.app_context():
            service = get_detection_service()
            print("OK Service created")
            
            # تست سرویس
            result = service.detect_single("تست هیوندای")
            
            if result['status'] == 'success':
                print("OK Service is working")
                return True
            else:
                print(f"X Service error: {result.get('message', 'Unknown')}")
                return False
                
    except Exception as e:
        print(f"X Service error: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """اجرای همه بررسی‌ها"""
    print("\n" + "="*60)
    print("System Error Check - Complete Detection System")
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
    print("Final Results")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "OK" if passed else "X ERROR"
        print(f"{check_name:20} : {status}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("OK OK OK All systems OK! System is ready OK OK OK")
    else:
        print("XXX Errors found! XXX")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

