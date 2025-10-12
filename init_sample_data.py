"""
Database initialization script for Asia Salman Automotive Parts
Creates sample data for brands, models, categories, and products
"""

from app import app, db
import models
import json
from datetime import datetime

def init_sample_data():
    """Initialize sample data for the enhanced system"""
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Sample Brands
        brands_data = [
            {
                'name': 'Toyota',
                'name_fa': 'تویوتا',
                'description': 'برند ژاپنی معتبر خودرو',
                'country_of_origin': 'Japan',
                'logo_url': '/static/images/brands/toyota.png'
            },
            {
                'name': 'Hyundai',
                'name_fa': 'هیوندای',
                'description': 'برند کره‌ای خودرو',
                'country_of_origin': 'South Korea',
                'logo_url': '/static/images/brands/hyundai.png'
            },
            {
                'name': 'KIA',
                'name_fa': 'کیا',
                'description': 'برند کره‌ای خودرو',
                'country_of_origin': 'South Korea',
                'logo_url': '/static/images/brands/kia.png'
            },
            {
                'name': 'Nissan',
                'name_fa': 'نیسان',
                'description': 'برند ژاپنی خودرو',
                'country_of_origin': 'Japan',
                'logo_url': '/static/images/brands/nissan.png'
            }
        ]
        
        brands = {}
        for brand_data in brands_data:
            brand = models.Brand(**brand_data)
            db.session.add(brand)
            db.session.flush()  # Get the ID
            brands[brand_data['name']] = brand
        
        # Sample Vehicle Models
        models_data = [
            # Toyota Models
            {
                'brand_id': brands['Toyota'].id,
                'model_name': 'Corolla',
                'model_name_fa': 'کورولا',
                'year_from': 2019,
                'year_to': 2024,
                'body_type': 'sedan',
                'engine_type': 'petrol'
            },
            {
                'brand_id': brands['Toyota'].id,
                'model_name': 'Camry',
                'model_name_fa': 'کمری',
                'year_from': 2020,
                'year_to': 2024,
                'body_type': 'sedan',
                'engine_type': 'petrol'
            },
            {
                'brand_id': brands['Toyota'].id,
                'model_name': 'RAV4',
                'model_name_fa': 'راو4',
                'year_from': 2019,
                'year_to': 2024,
                'body_type': 'SUV',
                'engine_type': 'petrol'
            },
            # Hyundai Models
            {
                'brand_id': brands['Hyundai'].id,
                'model_name': 'Elantra',
                'model_name_fa': 'الانترا',
                'year_from': 2020,
                'year_to': 2024,
                'body_type': 'sedan',
                'engine_type': 'petrol'
            },
            {
                'brand_id': brands['Hyundai'].id,
                'model_name': 'Tucson',
                'model_name_fa': 'توسان',
                'year_from': 2019,
                'year_to': 2024,
                'body_type': 'SUV',
                'engine_type': 'petrol'
            },
            # KIA Models
            {
                'brand_id': brands['KIA'].id,
                'model_name': 'Sportage',
                'model_name_fa': 'اسپورتیج',
                'year_from': 2020,
                'year_to': 2024,
                'body_type': 'SUV',
                'engine_type': 'petrol'
            },
            {
                'brand_id': brands['KIA'].id,
                'model_name': 'Optima',
                'model_name_fa': 'اپتیما',
                'year_from': 2019,
                'year_to': 2023,
                'body_type': 'sedan',
                'engine_type': 'petrol'
            }
        ]
        
        vehicle_models = {}
        for model_data in models_data:
            model = models.VehicleModel(**model_data)
            db.session.add(model)
            db.session.flush()  # Get the ID
            vehicle_models[f"{model_data['brand_id']}_{model_data['model_name']}"] = model
        
        # Sample Part Categories
        categories_data = [
            {
                'category_name': 'Engine Parts',
                'category_name_fa': 'قطعات موتور',
                'description': 'قطعات مربوط به موتور خودرو',
                'icon_class': 'fas fa-cog',
                'sort_order': 1
            },
            {
                'category_name': 'Brake System',
                'category_name_fa': 'سیستم ترمز',
                'description': 'قطعات سیستم ترمز خودرو',
                'icon_class': 'fas fa-car-crash',
                'sort_order': 2
            },
            {
                'category_name': 'Electrical',
                'category_name_fa': 'قطعات برقی',
                'description': 'قطعات سیستم برق خودرو',
                'icon_class': 'fas fa-bolt',
                'sort_order': 3
            },
            {
                'category_name': 'Filters',
                'category_name_fa': 'فیلترها',
                'description': 'انواع فیلترهای خودرو',
                'icon_class': 'fas fa-filter',
                'sort_order': 4
            },
            {
                'category_name': 'Suspension',
                'category_name_fa': 'سیستم تعلیق',
                'description': 'قطعات سیستم تعلیق خودرو',
                'icon_class': 'fas fa-car-side',
                'sort_order': 5
            },
            {
                'category_name': 'Cooling System',
                'category_name_fa': 'سیستم خنک‌کننده',
                'description': 'قطعات سیستم خنک‌کننده',
                'icon_class': 'fas fa-thermometer-half',
                'sort_order': 6
            }
        ]
        
        categories = {}
        for category_data in categories_data:
            category = models.PartCategory(**category_data)
            db.session.add(category)
            db.session.flush()  # Get the ID
            categories[category_data['category_name']] = category
        
        # Sample Part Subcategories
        subcategories_data = [
            # Engine Parts Subcategories
            {
                'category_id': categories['Engine Parts'].id,
                'subcategory_name': 'Spark Plugs',
                'subcategory_name_fa': 'شمع',
                'sort_order': 1
            },
            {
                'category_id': categories['Engine Parts'].id,
                'subcategory_name': 'Oil Filters',
                'subcategory_name_fa': 'فیلتر روغن',
                'sort_order': 2
            },
            {
                'category_id': categories['Engine Parts'].id,
                'subcategory_name': 'Air Filters',
                'subcategory_name_fa': 'فیلتر هوا',
                'sort_order': 3
            },
            # Brake System Subcategories
            {
                'category_id': categories['Brake System'].id,
                'subcategory_name': 'Brake Pads',
                'subcategory_name_fa': 'لنت ترمز',
                'sort_order': 1
            },
            {
                'category_id': categories['Brake System'].id,
                'subcategory_name': 'Brake Discs',
                'subcategory_name_fa': 'دیسک ترمز',
                'sort_order': 2
            },
            # Electrical Subcategories
            {
                'category_id': categories['Electrical'].id,
                'subcategory_name': 'Batteries',
                'subcategory_name_fa': 'باتری',
                'sort_order': 1
            },
            {
                'category_id': categories['Electrical'].id,
                'subcategory_name': 'Alternators',
                'subcategory_name_fa': 'آلترناتور',
                'sort_order': 2
            }
        ]
        
        subcategories = {}
        for subcategory_data in subcategories_data:
            subcategory = models.PartSubcategory(**subcategory_data)
            db.session.add(subcategory)
            db.session.flush()  # Get the ID
            subcategories[f"{subcategory_data['category_id']}_{subcategory_data['subcategory_name']}"] = subcategory
        
        # Sample Products
        products_data = [
            # Toyota Corolla Products
            {
                'sku': 'TC-SP-001',
                'oem_code': '90915-YZZD2',
                'name': 'Toyota Corolla Spark Plug',
                'name_fa': 'شمع تویوتا کورولا',
                'description': 'Original spark plug for Toyota Corolla',
                'description_fa': 'شمع اصلی تویوتا کورولا',
                'brand_id': brands['Toyota'].id,
                'category_id': categories['Engine Parts'].id,
                'subcategory_id': subcategories[f"{categories['Engine Parts'].id}_Spark Plugs"].id,
                'compatible_models': json.dumps([vehicle_models[f"{brands['Toyota'].id}_Corolla"].id]),
                'bulk_price_cash': 0.0008,  # 800,000 Toman in billions
                'retail_price_cash': 0.001,  # 1,000,000 Toman in billions
                'bulk_price_check': 0.0009,  # 900,000 Toman in billions
                'retail_price_check': 0.0011,  # 1,100,000 Toman in billions
                'stock_quantity': 50,
                'min_order_quantity': 4,
                'primary_image': '/static/images/products/spark_plug.jpg',
                'tags': json.dumps(['spark plug', 'toyota', 'corolla', 'engine']),
                'is_featured': True
            },
            {
                'sku': 'TC-BP-001',
                'oem_code': '04465-YZZA1',
                'name': 'Toyota Corolla Brake Pad Set',
                'name_fa': 'ست لنت ترمز تویوتا کورولا',
                'description': 'Front brake pad set for Toyota Corolla',
                'description_fa': 'ست لنت ترمز جلو تویوتا کورولا',
                'brand_id': brands['Toyota'].id,
                'category_id': categories['Brake System'].id,
                'subcategory_id': subcategories[f"{categories['Brake System'].id}_Brake Pads"].id,
                'compatible_models': json.dumps([vehicle_models[f"{brands['Toyota'].id}_Corolla"].id]),
                'bulk_price_cash': 0.0025,  # 2,500,000 Toman in billions
                'retail_price_cash': 0.003,  # 3,000,000 Toman in billions
                'bulk_price_check': 0.0027,  # 2,700,000 Toman in billions
                'retail_price_check': 0.0032,  # 3,200,000 Toman in billions
                'stock_quantity': 25,
                'min_order_quantity': 1,
                'primary_image': '/static/images/products/brake_pad.jpg',
                'tags': json.dumps(['brake pad', 'toyota', 'corolla', 'brake']),
                'is_featured': True
            },
            # Hyundai Elantra Products
            {
                'sku': 'HE-OF-001',
                'oem_code': '26300-2G000',
                'name': 'Hyundai Elantra Oil Filter',
                'name_fa': 'فیلتر روغن هیوندای الانترا',
                'description': 'Original oil filter for Hyundai Elantra',
                'description_fa': 'فیلتر روغن اصلی هیوندای الانترا',
                'brand_id': brands['Hyundai'].id,
                'category_id': categories['Engine Parts'].id,
                'subcategory_id': subcategories[f"{categories['Engine Parts'].id}_Oil Filters"].id,
                'compatible_models': json.dumps([vehicle_models[f"{brands['Hyundai'].id}_Elantra"].id]),
                'bulk_price_cash': 0.0003,  # 300,000 Toman in billions
                'retail_price_cash': 0.0004,  # 400,000 Toman in billions
                'bulk_price_check': 0.00035,  # 350,000 Toman in billions
                'retail_price_check': 0.00045,  # 450,000 Toman in billions
                'stock_quantity': 100,
                'min_order_quantity': 1,
                'primary_image': '/static/images/products/filter_oil.jpg',
                'tags': json.dumps(['oil filter', 'hyundai', 'elantra', 'engine']),
                'is_featured': False
            },
            # KIA Sportage Products
            {
                'sku': 'KS-AF-001',
                'oem_code': '28113-2GA00',
                'name': 'KIA Sportage Air Filter',
                'name_fa': 'فیلتر هوا کیا اسپورتیج',
                'description': 'Original air filter for KIA Sportage',
                'description_fa': 'فیلتر هوای اصلی کیا اسپورتیج',
                'brand_id': brands['KIA'].id,
                'category_id': categories['Engine Parts'].id,
                'subcategory_id': subcategories[f"{categories['Engine Parts'].id}_Air Filters"].id,
                'compatible_models': json.dumps([vehicle_models[f"{brands['KIA'].id}_Sportage"].id]),
                'bulk_price_cash': 0.0002,  # 200,000 Toman in billions
                'retail_price_cash': 0.00025,  # 250,000 Toman in billions
                'bulk_price_check': 0.00022,  # 220,000 Toman in billions
                'retail_price_check': 0.00027,  # 270,000 Toman in billions
                'stock_quantity': 75,
                'min_order_quantity': 1,
                'primary_image': '/static/images/products/filter_oil_toyota.jpg',
                'tags': json.dumps(['air filter', 'kia', 'sportage', 'engine']),
                'is_featured': False
            }
        ]
        
        for product_data in products_data:
            product = models.Product(**product_data)
            db.session.add(product)
        
        # Create search indexes for products
        products = models.Product.query.all()
        for product in products:
            search_index = models.ProductSearchIndex(
                product_id=product.id,
                search_keywords=json.dumps([
                    product.name.lower(),
                    product.name_fa,
                    product.sku.lower(),
                    product.oem_code.lower() if product.oem_code else '',
                    *product.get_tags()
                ])
            )
            db.session.add(search_index)
        
        # Commit all changes
        db.session.commit()
        
        print("Sample data initialized successfully!")
        print(f"Created {len(brands)} brands")
        print(f"Created {len(vehicle_models)} vehicle models")
        print(f"Created {len(categories)} categories")
        print(f"Created {len(subcategories)} subcategories")
        print(f"Created {len(products)} products")

if __name__ == '__main__':
    init_sample_data()
