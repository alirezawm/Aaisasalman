"""
تست سیستم تشخیص خودکار
Test Detection System
"""

from app import app
from brand_vehicle_detector import get_detector
from detection_service import get_detection_service


def test_basic_detection():
    """تست تشخیص پایه"""
    print("\n" + "="*60)
    print("تست تشخیص پایه")
    print("="*60)
    
    with app.app_context():
        detector = get_detector()
        
        test_cases = [
            "لنت ترمز تویوتا کمری سدان",
            "روغن موتور هیوندای SUV",
            "فیلتر هوای بنز sedan",
            "شمع BMW کوپه",
        ]
        
        for text in test_cases:
            result = detector.detect_brand_and_vehicle_types(text)
            
            if result['status'] == 'success':
                data = result['data']
                brand = data['detected_brand']['name'] if data['detected_brand'] else 'نامشخص'
                types = [vt['name'] for vt in data['detected_vehicle_types']] if data['detected_vehicle_types'] else []
                types_str = ', '.join(types) if types else 'نامشخص'
                
                print(f"✓ {text[:40]:40} -> برند: {brand:10} | نوع: {types_str}")
            else:
                print(f"✗ {text[:40]:40} -> خطا: {result.get('message', 'نامشخص')}")


def test_detection_service():
    """تست سرویس تشخیص"""
    print("\n" + "="*60)
    print("تست سرویس تشخیص")
    print("="*60)
    
    with app.app_context():
        service = get_detection_service()
        
        # تست تشخیص تکی
        result = service.detect_single("لنت ترمز تویوتا کمری")
        
        if result['status'] == 'success':
            print("✓ سرویس تشخیص تکی کار می‌کند")
        else:
            print("✗ خطا در سرویس تشخیص تکی")
        
        # تست تشخیص دسته‌ای
        texts = [
            "روغن موتور بنز",
            "فیلتر هوای کیا"
        ]
        result = service.detect_batch(texts)
        
        if result['status'] == 'success':
            print(f"✓ سرویس تشخیص دسته‌ای کار می‌کند ({result['data']['successful']}/{result['data']['total']})")
        else:
            print("✗ خطا در سرویس تشخیص دسته‌ای")


def test_database():
    """تست دیتابیس"""
    print("\n" + "="*60)
    print("تست دیتابیس")
    print("="*60)
    
    with app.app_context():
        from detection_models import BrandAlias, VehicleTypeAlias
        from models import Brand, VehicleType
        
        # بررسی برندها
        brands = Brand.query.count()
        print(f"تعداد برندها: {brands}")
        
        # بررسی انواع خودرو
        types = VehicleType.query.count()
        print(f"تعداد انواع خودرو: {types}")
        
        # بررسی نام‌های مستعار برند
        brand_aliases = BrandAlias.query.count()
        print(f"تعداد نام‌های مستعار برند: {brand_aliases}")
        
        # بررسی نام‌های مستعار نوع
        type_aliases = VehicleTypeAlias.query.count()
        print(f"تعداد نام‌های مستعار نوع: {type_aliases}")
        
        if types > 0 and type_aliases > 0:
            print("✓ دیتابیس به درستی راه‌اندازی شده است")
        else:
            print("✗ مشکل در دیتابیس")


def test_stats():
    """تست آمار"""
    print("\n" + "="*60)
    print("آمار سیستم")
    print("="*60)
    
    with app.app_context():
        detector = get_detector()
        stats = detector.get_detection_stats()
        
        print(f"کل محصولات: {stats.get('total_products', 0)}")
        print(f"محصولات با برند: {stats.get('products_with_brand', 0)}")
        print(f"محصولات با نوع: {stats.get('products_with_vehicle_types', 0)}")
        print(f"پوشش برند: {stats.get('brand_coverage', 0):.1f}%")
        print(f"پوشش نوع: {stats.get('vehicle_type_coverage', 0):.1f}%")


def main():
    """اجرای همه تست‌ها"""
    print("\n" + "="*60)
    print("شروع تست سیستم تشخیص خودکار")
    print("="*60)
    
    try:
        test_database()
        test_basic_detection()
        test_detection_service()
        test_stats()
        
        print("\n" + "="*60)
        print("✓ همه تست‌ها موفق بودند!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ خطا در تست: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

