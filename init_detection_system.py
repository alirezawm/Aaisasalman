"""
اسکریپت مقداردهی اولیه سیستم تشخیص خودکار
Initialize Detection System
"""

from app import app
from models import db, Brand, VehicleType
from detection_models import BrandAlias, VehicleTypeAlias
import json


def init_detection_tables():
    """ایجاد جداول سیستم تشخیص"""
    print("در حال ایجاد جداول دیتابیس...")
    
    with app.app_context():
        # Import models to ensure they're registered
        import detection_models
        
        # Create all tables
        db.create_all()
        
        print("جداول ایجاد شدند")


def load_initial_data():
    """بارگذاری داده‌های اولیه"""
    print("\nدر حال بارگذاری داده‌های اولیه...")
    
    with app.app_context():
        # Load data from megaprompt
        try:
            with open('brand_vehicle_detection_complete_rebuild_megaprompt.json', 'r', encoding='utf-8') as f:
                megaprompt = json.load(f)
        except FileNotFoundError:
            print("فایل مگاپرامپت یافت نشد. از داده‌های پیش‌فرض استفاده می‌شود.")
            megaprompt = {'initial_data': {}}
        
        initial_data = megaprompt.get('initial_data', {})
        
        # Create brand aliases
        brand_aliases = initial_data.get('brand_aliases', {
            'Toyota': ['تویوتا', 'TOYOTA', 'toyota', 'تويوتا'],
            'Hyundai': ['هیوندای', 'هیوندا', 'HYUNDAI', 'hyundai', 'هيونداي'],
            'Benz': ['بنز', 'مرسدس', 'Mercedes', 'BENZ', 'بنز'],
            'BMW': ['بی‌ام‌و', 'بی ام و', 'BMW', 'bmw'],
            'Peugeot': ['پژو', 'پژو', 'PEUGEOT', 'peugeot'],
            'Pride': ['پراید', 'PRIDE', 'pride'],
            'Kia': ['کیا', 'KIA', 'kia'],
            'Nissan': ['نیسان', 'NISSAN', 'nissan'],
            'Mazda': ['مزدا', 'MAZDA', 'mazda'],
            'Honda': ['هوندا', 'HONDA', 'honda']
        })
        
        brands_added = 0
        aliases_added = 0
        
        for brand_name, aliases in brand_aliases.items():
            brand = Brand.query.filter_by(name=brand_name).first()
            
            if brand:
                for alias in aliases:
                    # Check if alias already exists
                    existing = BrandAlias.query.filter_by(
                        brand_id=brand.id,
                        alias=alias
                    ).first()
                    
                    if not existing:
                        lang = 'fa' if any('\u0600' <= c <= '\u06FF' for c in alias) else 'en'
                        ba = BrandAlias(
                            brand_id=brand.id,
                            alias=alias,
                            language=lang
                        )
                        db.session.add(ba)
                        aliases_added += 1
                
                brands_added += 1
                print(f"  + {brand_name}: {len(aliases)} نام مستعار")
        
        # Create vehicle type aliases
        type_aliases = initial_data.get('vehicle_type_aliases', {
            'sedan': ['سدان', 'سدان', 'SEDAN', 'Sedan'],
            'SUV': ['شاسی‌بلند', 'شاسی بلند', 'شاسیبلند', 'suv', 'SUV'],
            'hatchback': ['هاچ‌بک', 'هاچ بک', 'هاچبک', 'HATCHBACK', 'Hatchback'],
            'coupe': ['کوپه', 'کوپه', 'COUPE', 'Coupe'],
            'pickup': ['پیکاپ', 'پیکاپ', 'PICKUP', 'Pickup'],
            'van': ['ون', 'ون', 'VAN', 'Van']
        })
        
        types_added = 0
        type_aliases_added = 0
        
        for type_name, aliases in type_aliases.items():
            vtype = VehicleType.query.filter_by(name=type_name).first()
            
            if not vtype:
                # Create vehicle type if it doesn't exist
                vtype = VehicleType(name=type_name)
                db.session.add(vtype)
                db.session.flush()  # To get the ID
            
            for alias in aliases:
                # Check if alias already exists
                existing = VehicleTypeAlias.query.filter_by(
                    vehicle_type_id=vtype.id,
                    alias=alias
                ).first()
                
                if not existing:
                    lang = 'fa' if any('\u0600' <= c <= '\u06FF' for c in alias) else 'en'
                    vta = VehicleTypeAlias(
                        vehicle_type_id=vtype.id,
                        alias=alias,
                        language=lang
                    )
                    db.session.add(vta)
                    type_aliases_added += 1
            
            types_added += 1
            print(f"  + {type_name}: {len(aliases)} نام مستعار")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\nداده‌های اولیه بارگذاری شدند:")
        print(f"   - {brands_added} برند")
        print(f"   - {aliases_added} نام مستعار برند")
        print(f"   - {types_added} نوع خودرو")
        print(f"   - {type_aliases_added} نام مستعار نوع")


def test_detection():
    """تست سیستم تشخیص"""
    print("\nتست سیستم تشخیص...")
    
    with app.app_context():
        from brand_vehicle_detector import get_detector
        
        detector = get_detector()
        
        # Test cases
        test_cases = [
            "لنت ترمز تویوتا کمری سدان",
            "روغن موتور هیوندای سوناتا",
            "فیلتر هوای بنز E کلاس",
            "شمع BMW سری 3 SUV",
        ]
        
        print("\n  نتایج تست:")
        for text in test_cases:
            result = detector.detect_brand_and_vehicle_types(text)
            
            if result['status'] == 'success':
                data = result['data']
                brand = data['detected_brand']['name'] if data['detected_brand'] else 'نامشخص'
                types = [vt['name'] for vt in data['detected_vehicle_types']] if data['detected_vehicle_types'] else []
                types_str = ', '.join(types) if types else 'نامشخص'
                
                print(f"  + {text[:35]:35} -> برند: {brand:10} | نوع: {types_str}")
            else:
                print(f"  x {text[:35]:35} -> خطا")
        
        # Show stats
        stats = detector.get_detection_stats()
        print(f"\nآمار:")
        print(f"   - کل محصولات: {stats.get('total_products', 0)}")
        print(f"   - با برند: {stats.get('products_with_brand', 0)}")
        print(f"   - پوشش برند: {stats.get('brand_coverage', 0):.1f}%")


def main():
    """تابع اصلی"""
    print("=" * 60)
    print("راه‌اندازی سیستم تشخیص خودکار برند و نوع خودرو")
    print("=" * 60)
    
    try:
        # Step 1: Create tables
        init_detection_tables()
        
        # Step 2: Load initial data
        load_initial_data()
        
        # Step 3: Test detection
        test_detection()
        
        print("\n" + "=" * 60)
        print("راه‌اندازی با موفقیت انجام شد!")
        print("=" * 60)
        print("\nگام‌های بعدی:")
        print("   1. python app.py  # راه‌اندازی سرور")
        print("   2. دسترسی به: http://localhost:5000/admin/detection")
        print("   3. API: http://localhost:5000/api/detection/stats")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\nخطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    main()

