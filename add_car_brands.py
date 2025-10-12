"""
افزودن برندهای خودرو به دیتابیس
Add Car Brands to Database
"""

from app import app
from models import db, Brand
from detection_models import BrandAlias


# برندهای خودرو با نام فارسی
CAR_BRANDS = [
    ('Toyota', 'تویوتا', 'Japan'),
    ('Hyundai', 'هیوندای', 'South Korea'),
    ('Mercedes-Benz', 'مرسدس بنز', 'Germany'),
    ('BMW', 'بی‌ام‌و', 'Germany'),
    ('Peugeot', 'پژو', 'France'),
    ('Kia', 'کیا', 'South Korea'),
    ('Nissan', 'نیسان', 'Japan'),
    ('Mazda', 'مزدا', 'Japan'),
    ('Honda', 'هوندا', 'Japan'),
    ('Ford', 'فورد', 'USA'),
    ('Chevrolet', 'شورولت', 'USA'),
    ('Volkswagen', 'فولکس واگن', 'Germany'),
    ('Audi', 'آئودی', 'Germany'),
    ('Lexus', 'لکسوس', 'Japan'),
    ('Renault', 'رنو', 'France'),
    ('Suzuki', 'سوزوکی', 'Japan'),
    ('Mitsubishi', 'میتسوبیشی', 'Japan'),
    ('Jeep', 'جیپ', 'USA'),
    ('Land Rover', 'لندرور', 'UK'),
    ('Porsche', 'پورشه', 'Germany'),
    ('Volvo', 'ولوو', 'Sweden'),
    ('Subaru', 'سوبارو', 'Japan'),
    ('Tesla', 'تسلا', 'USA'),
    ('SAIPA', 'سایپا', 'Iran'),
    ('Iran Khodro', 'ایران خودرو', 'Iran'),
    ('Brilliance', 'بریلیانس', 'China'),
    ('Changan', 'چانگان', 'China'),
    ('Chery', 'چری', 'China'),
    ('Geely', 'جیلی', 'China'),
    ('Great Wall', 'گریت وال', 'China'),
    ('MVM', 'ام‌وی‌ام', 'Iran'),
]

# نام‌های مستعار
ALIASES = {
    'Toyota': ['تویوتا', 'TOYOTA', 'toyota', 'تويوتا'],
    'Hyundai': ['هیوندای', 'هیوندا', 'HYUNDAI', 'hyundai', 'هيونداي'],
    'Mercedes-Benz': ['بنز', 'مرسدس', 'مرسدس بنز', 'Mercedes', 'BENZ'],
    'BMW': ['بی‌ام‌و', 'بی ام و', 'BMW', 'bmw', 'بیامو'],
    'Peugeot': ['پژو', 'PEUGEOT', 'peugeot'],
    'Kia': ['کیا', 'KIA', 'kia'],
    'Nissan': ['نیسان', 'NISSAN', 'nissan'],
    'Mazda': ['مزدا', 'MAZDA', 'mazda'],
    'Honda': ['هوندا', 'HONDA', 'honda'],
    'Ford': ['فورد', 'FORD', 'ford'],
    'Chevrolet': ['شورولت', 'شورلت', 'CHEVROLET', 'chevrolet'],
    'Volkswagen': ['فولکس', 'فولکس واگن', 'VW', 'VOLKSWAGEN'],
    'Audi': ['آئودی', 'اودی', 'AUDI', 'audi'],
    'Lexus': ['لکسوس', 'LEXUS', 'lexus'],
    'Renault': ['رنو', 'RENAULT', 'renault'],
    'Suzuki': ['سوزوکی', 'SUZUKI', 'suzuki'],
    'Mitsubishi': ['میتسوبیشی', 'متسوبیشی', 'MITSUBISHI'],
    'Jeep': ['جیپ', 'JEEP', 'jeep'],
    'Land Rover': ['لندرور', 'لند رور', 'LAND ROVER'],
    'Porsche': ['پورشه', 'PORSCHE', 'porsche'],
    'Volvo': ['ولوو', 'VOLVO', 'volvo'],
    'Subaru': ['سوبارو', 'SUBARU', 'subaru'],
    'Tesla': ['تسلا', 'TESLA', 'tesla'],
    'SAIPA': ['سایپا', 'SAIPA', 'saipa'],
    'Iran Khodro': ['ایران خودرو', 'ایرانخودرو', 'IKCO'],
    'Brilliance': ['بریلیانس', 'BRILLIANCE'],
    'Changan': ['چانگان', 'CHANGAN'],
    'Chery': ['چری', 'CHERY', 'chery'],
    'Geely': ['جیلی', 'GEELY', 'geely'],
    'Great Wall': ['گریت وال', 'گریت‌وال', 'GREAT WALL'],
    'MVM': ['ام‌وی‌ام', 'ام وی ام', 'MVM', 'mvm'],
}


def add_car_brands():
    """افزودن برندهای خودرو"""
    print("\n" + "="*60)
    print("افزودن برندهای خودرو به دیتابیس")
    print("="*60 + "\n")
    
    with app.app_context():
        brands_added = 0
        brands_existing = 0
        aliases_added = 0
        
        for brand_name, brand_name_fa, country in CAR_BRANDS:
            # بررسی وجود برند
            existing_brand = Brand.query.filter(
                db.func.lower(Brand.name) == brand_name.lower()
            ).first()
            
            if existing_brand:
                print(f"وجود دارد: {brand_name}")
                brand = existing_brand
                brands_existing += 1
            else:
                # ایجاد برند جدید
                brand = Brand(
                    name=brand_name,
                    name_fa=brand_name_fa,
                    country_of_origin=country,
                    is_active=True
                )
                db.session.add(brand)
                db.session.flush()  # برای دریافت ID
                brands_added += 1
                print(f"✓ افزوده شد: {brand_name} ({brand_name_fa})")
            
            # افزودن نام‌های مستعار
            if brand_name in ALIASES:
                for alias in ALIASES[brand_name]:
                    existing_alias = BrandAlias.query.filter_by(
                        brand_id=brand.id,
                        alias=alias
                    ).first()
                    
                    if not existing_alias:
                        lang = 'fa' if any('\u0600' <= c <= '\u06FF' for c in alias) else 'en'
                        ba = BrandAlias(
                            brand_id=brand.id,
                            alias=alias,
                            language=lang
                        )
                        db.session.add(ba)
                        aliases_added += 1
                
                print(f"  + {len(ALIASES[brand_name])} نام مستعار")
        
        # ذخیره تغییرات
        db.session.commit()
        
        print("\n" + "="*60)
        print("نتایج:")
        print("="*60)
        print(f"برندهای جدید افزوده شده: {brands_added}")
        print(f"برندهای موجود: {brands_existing}")
        print(f"نام‌های مستعار افزوده شده: {aliases_added}")
        print("\n" + "="*60)
        print("✓ عملیات با موفقیت انجام شد!")
        print("="*60 + "\n")
        
        # نمایش تعداد کل
        total_brands = Brand.query.count()
        total_aliases = BrandAlias.query.count()
        print(f"تعداد کل برندها: {total_brands}")
        print(f"تعداد کل نام‌های مستعار: {total_aliases}\n")


if __name__ == '__main__':
    add_car_brands()

