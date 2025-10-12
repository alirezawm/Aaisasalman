"""
افزودن نام‌های مستعار برای برندهای موجود
Add Aliases for Existing Brands
"""

from app import app
from models import db, Brand
from detection_models import BrandAlias


# نقشه نام‌های مستعار برندها
BRAND_ALIASES = {
    'Toyota': ['تویوتا', 'TOYOTA', 'toyota', 'تويوتا'],
    'Hyundai': ['هیوندای', 'هیوندا', 'HYUNDAI', 'hyundai', 'هيونداي', 'هیوندایی'],
    'Benz': ['بنز', 'مرسدس', 'مرسدس بنز', 'Mercedes', 'BENZ', 'mercedes'],
    'BMW': ['بی‌ام‌و', 'بی ام و', 'BMW', 'bmw', 'بیامو'],
    'Peugeot': ['پژو', 'پژو', 'PEUGEOT', 'peugeot'],
    'Pride': ['پراید', 'PRIDE', 'pride'],
    'Kia': ['کیا', 'KIA', 'kia', 'کیا'],
    'Nissan': ['نیسان', 'NISSAN', 'nissan', 'نیسان'],
    'Mazda': ['مزدا', 'MAZDA', 'mazda', 'مزدا'],
    'Honda': ['هوندا', 'HONDA', 'honda', 'هوندا'],
    'Ford': ['فورد', 'FORD', 'ford'],
    'Chevrolet': ['شورولت', 'شورلت', 'CHEVROLET', 'chevrolet'],
    'Volkswagen': ['فولکس', 'فولکس واگن', 'VOLKSWAGEN', 'volkswagen'],
    'Audi': ['آئودی', 'اودی', 'AUDI', 'audi'],
    'Lexus': ['لکسوس', 'LEXUS', 'lexus'],
    'Volvo': ['ولوو', 'VOLVO', 'volvo'],
    'Renault': ['رنو', 'RENAULT', 'renault'],
    'Fiat': ['فیات', 'FIAT', 'fiat'],
    'Jeep': ['جیپ', 'JEEP', 'jeep'],
    'Land Rover': ['لندرور', 'لند رور', 'LAND ROVER', 'landrover'],
    'Porsche': ['پورشه', 'PORSCHE', 'porsche'],
    'Mitsubishi': ['میتسوبیشی', 'متسوبیشی', 'MITSUBISHI', 'mitsubishi'],
    'Subaru': ['سوبارو', 'SUBARU', 'subaru'],
    'Suzuki': ['سوزوکی', 'SUZUKI', 'suzuki'],
    'Chrysler': ['کرایسلر', 'CHRYSLER', 'chrysler'],
    'Dodge': ['دوج', 'DODGE', 'dodge'],
    'Cadillac': ['کادیلاک', 'CADILLAC', 'cadillac'],
    'Buick': ['بیوک', 'BUICK', 'buick'],
    'GMC': ['جی ام سی', 'GMC', 'gmc'],
    'Lincoln': ['لینکلن', 'LINCOLN', 'lincoln'],
    'Acura': ['اکیورا', 'ACURA', 'acura'],
    'Infiniti': ['اینفینیتی', 'INFINITI', 'infiniti'],
    'Genesis': ['جنسیس', 'GENESIS', 'genesis'],
    'Ram': ['رم', 'RAM', 'ram'],
    'Tesla': ['تسلا', 'TESLA', 'tesla'],
    'Jaguar': ['جگوار', 'JAGUAR', 'jaguar'],
    'Alfa Romeo': ['آلفا رومئو', 'ALFA ROMEO', 'alfa romeo'],
    'Maserati': ['مازراتی', 'MASERATI', 'maserati'],
    'Ferrari': ['فراری', 'FERRARI', 'ferrari'],
    'Lamborghini': ['لامبورگینی', 'LAMBORGHINI', 'lamborghini'],
    'Bentley': ['بنتلی', 'BENTLEY', 'bentley'],
    'Rolls-Royce': ['رولزرویس', 'ROLLS-ROYCE', 'rolls royce'],
    'Aston Martin': ['استون مارتین', 'ASTON MARTIN', 'aston martin'],
    'McLaren': ['مک‌لارن', 'MCLAREN', 'mclaren'],
    'Bugatti': ['بوگاتی', 'BUGATTI', 'bugatti'],
}


def add_aliases():
    """افزودن نام‌های مستعار"""
    print("\n" + "="*60)
    print("افزودن نام‌های مستعار برندها")
    print("="*60 + "\n")
    
    with app.app_context():
        brands_found = 0
        aliases_added = 0
        brands_not_found = []
        
        for brand_name, aliases in BRAND_ALIASES.items():
            # جستجوی برند (با توجه به حروف بزرگ/کوچک)
            brand = Brand.query.filter(
                db.func.lower(Brand.name) == brand_name.lower()
            ).first()
            
            if brand:
                brands_found += 1
                print(f"پیدا شد: {brand.name} (ID: {brand.id})")
                
                for alias in aliases:
                    # بررسی وجود نام مستعار
                    existing = BrandAlias.query.filter_by(
                        brand_id=brand.id,
                        alias=alias
                    ).first()
                    
                    if not existing:
                        # تشخیص زبان
                        lang = 'fa' if any('\u0600' <= c <= '\u06FF' for c in alias) else 'en'
                        
                        # ایجاد نام مستعار
                        ba = BrandAlias(
                            brand_id=brand.id,
                            alias=alias,
                            language=lang
                        )
                        db.session.add(ba)
                        aliases_added += 1
                
                print(f"  + {len(aliases)} نام مستعار\n")
            else:
                brands_not_found.append(brand_name)
        
        # ذخیره تغییرات
        db.session.commit()
        
        print("="*60)
        print("نتایج:")
        print("="*60)
        print(f"برندهای پیدا شده: {brands_found}")
        print(f"نام‌های مستعار افزوده شده: {aliases_added}")
        
        if brands_not_found:
            print(f"\nبرندهای پیدا نشده ({len(brands_not_found)}):")
            for brand in brands_not_found:
                print(f"  - {brand}")
        
        print("\n" + "="*60)
        print("✓ عملیات با موفقیت انجام شد!")
        print("="*60 + "\n")
        
        # نمایش برندهای موجود در دیتابیس
        print("برندهای موجود در دیتابیس:")
        all_brands = Brand.query.all()
        for brand in all_brands[:10]:  # فقط 10 تا اول
            print(f"  - {brand.name} ({brand.name_fa})")
        
        if len(all_brands) > 10:
            print(f"  ... و {len(all_brands) - 10} برند دیگر")


if __name__ == '__main__':
    add_aliases()

