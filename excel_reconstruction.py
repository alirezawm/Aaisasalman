"""
Excel Reconstruction Module for Persian Product Data
مگاپرامپت برای دریافت فایل اکسل نامنظم و بازسازی آن به یک فایل اکسل استاندارد
"""

import pandas as pd
import numpy as np
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelReconstructor:
    """
    کلاس بازسازی فایل اکسل برای استانداردسازی داده‌های محصولات
    """
    
    def __init__(self):
        # ستون‌های هدف استاندارد
        self.target_columns = [
            "کد کالا",
            "شرح کالا", 
            "قیمت تکی",
            "قیمت نقدی عمده",
            "قیمت چکی عمده",
            "موجودی"
        ]
        
        # نگاشت نام‌های ستون‌های مختلف به ستون‌های استاندارد
        self.column_mappings = {
            "کد کالا": [
                "کد", "کد کالا", "SKU", "Item Code", "Product Code", "کد محصول",
                "کد کالا", "کد آیتم", "کد محصول", "شناسه کالا", "کد شناسایی",
                "کد کالا", "کد محصول", "کد آیتم", "شناسه محصول", "کد کالا"
            ],
            "شرح کالا": [
                "شرح", "شرح کالا", "نام", "نام کالا", "توضیحات", "Description",
                "Product Name", "Item Name", "نام محصول", "شرح محصول", "توضیح",
                "نام کالا", "شرح کالا", "توضیحات کالا", "نام آیتم", "شرح آیتم"
            ],
            "قیمت تکی": [
                "قیمت", "قیمت تکی", "قیمت واحد", "قیمت خرده", "Retail Price",
                "Unit Price", "Price", "قیمت فروش", "قیمت خرده فروشی", "قیمت تک",
                "قیمت واحد", "قیمت تکی", "قیمت خرده", "قیمت فروش", "قیمت تک"
            ],
            "قیمت نقدی عمده": [
                "قیمت عمده", "قیمت نقدی عمده", "قیمت عمده نقد", "Bulk Price Cash",
                "Wholesale Cash", "قیمت عمده نقدی", "قیمت نقدی عمده", "قیمت عمده",
                "قیمت عمده نقد", "قیمت نقدی عمده", "قیمت عمده نقدی", "قیمت عمده",
                "قیمت نقدی عمده (هزار ریال)", "قیمت عمده نقد (هزار ریال)"
            ],
            "قیمت چکی عمده": [
                "قیمت چکی عمده", "قیمت عمده چک", "Bulk Price Check", "Wholesale Check",
                "قیمت عمده چکی", "قیمت چکی عمده", "قیمت عمده چک", "قیمت چکی عمده",
                "قیمت عمده چکی", "قیمت چکی عمده", "قیمت عمده چک", "قیمت چکی عمده",
                "قیمت چکی عمده (هزار ریال)", "قیمت عمده چک (هزار ریال)"
            ],
            "موجودی": [
                "موجودی", "تعداد", "تعداد موجود", "Stock", "Quantity", "Inventory",
                "تعداد کالا", "موجودی کالا", "تعداد موجودی", "موجودی موجود",
                "تعداد", "موجودی", "تعداد موجود", "موجودی کالا", "تعداد کالا"
            ]
        }
        
        # الگوهای شناسایی قیمت
        self.price_patterns = [
            r'[\d,]+\.?\d*',  # اعداد با کاما و نقطه
            r'[\d.]+',        # اعداد با نقطه
            r'[\d,]+',        # اعداد با کاما
        ]
        
        # واحدهای پولی
        self.currency_symbols = ['ریال', 'تومان', 'Rial', 'Toman', 'هزار ریال', 'هزار تومان']
        
        # آمار پردازش
        self.processing_stats = {
            'input_rows': 0,
            'successful_rows': 0,
            'error_rows': 0,
            'duplicate_rows': 0,
            'mapped_columns': {},
            'conversion_rules': [],
            'errors': []
        }
    
    def clean_text(self, text: str) -> str:
        """پاک‌سازی متن از نویسه‌های کنترل و فاصله‌های اضافی"""
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text).strip()
        # حذف نویسه‌های کنترل
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # حذف فاصله‌های اضافی
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """استخراج قیمت از متن"""
        if pd.isna(price_text) or price_text is None:
            return None
        
        price_text = str(price_text).strip()
        if not price_text:
            return None
        
        # حذف واحدهای پولی
        for symbol in self.currency_symbols:
            price_text = price_text.replace(symbol, '')
        
        # حذف فاصله‌ها
        price_text = price_text.replace(' ', '')
        
        # شناسایی الگوی قیمت
        for pattern in self.price_patterns:
            match = re.search(pattern, price_text)
            if match:
                price_str = match.group()
                try:
                    # تبدیل کاما به نقطه برای اعداد اعشاری
                    if ',' in price_str and '.' in price_str:
                        # فرمت 1,234.56
                        price_str = price_str.replace(',', '')
                    elif ',' in price_str:
                        # فرمت 1,234 یا 1,234,567
                        if len(price_str.split(',')[-1]) <= 2:
                            # احتمالاً فرمت 1,234.56
                            price_str = price_str.replace(',', '.')
                        else:
                            # فرمت 1,234,567
                            price_str = price_str.replace(',', '')
                    
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_inventory(self, inventory_text: str) -> Optional[float]:
        """استخراج موجودی از متن"""
        if pd.isna(inventory_text) or inventory_text is None:
            return None
        
        inventory_text = str(inventory_text).strip()
        if not inventory_text:
            return None
        
        # حذف واحدها
        inventory_text = re.sub(r'[^\d.,\-+]', '', inventory_text)
        
        try:
            # تبدیل کاما به نقطه
            if ',' in inventory_text and '.' not in inventory_text:
                inventory_text = inventory_text.replace(',', '.')
            elif ',' in inventory_text:
                inventory_text = inventory_text.replace(',', '')
            
            return float(inventory_text)
        except ValueError:
            return None
    
    def map_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """نگاشت ستون‌های ورودی به ستون‌های استاندارد"""
        column_mapping = {}
        df_columns = [col.strip() for col in df.columns]
        
        for target_col, possible_names in self.column_mappings.items():
            for col in df_columns:
                if col in possible_names:
                    column_mapping[col] = target_col
                    break
        
        self.processing_stats['mapped_columns'] = column_mapping
        return column_mapping
    
    def process_row(self, row: pd.Series, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """پردازش یک ردیف داده"""
        processed_row = {}
        errors = []
        
        # کد کالا
        code_col = None
        for col, target in column_mapping.items():
            if target == "کد کالا":
                code_col = col
                break
        
        if code_col and code_col in row:
            code = self.clean_text(row[code_col])
            if code:
                processed_row["کد کالا"] = code
            else:
                errors.append("کد کالا خالی است")
        else:
            errors.append("ستون کد کالا یافت نشد")
        
        # شرح کالا
        desc_col = None
        for col, target in column_mapping.items():
            if target == "شرح کالا":
                desc_col = col
                break
        
        if desc_col and desc_col in row:
            description = self.clean_text(row[desc_col])
            processed_row["شرح کالا"] = description
        else:
            processed_row["شرح کالا"] = ""
        
        # قیمت تکی
        price_col = None
        for col, target in column_mapping.items():
            if target == "قیمت تکی":
                price_col = col
                break
        
        if price_col and price_col in row:
            price = self.extract_price(row[price_col])
            processed_row["قیمت تکی"] = price
        else:
            processed_row["قیمت تکی"] = None
        
        # قیمت نقدی عمده
        bulk_cash_col = None
        for col, target in column_mapping.items():
            if target == "قیمت نقدی عمده":
                bulk_cash_col = col
                break
        
        if bulk_cash_col and bulk_cash_col in row:
            bulk_cash_price = self.extract_price(row[bulk_cash_col])
            processed_row["قیمت نقدی عمده"] = bulk_cash_price
        else:
            processed_row["قیمت نقدی عمده"] = None
        
        # قیمت چکی عمده
        bulk_check_col = None
        for col, target in column_mapping.items():
            if target == "قیمت چکی عمده":
                bulk_check_col = col
                break
        
        if bulk_check_col and bulk_check_col in row:
            bulk_check_price = self.extract_price(row[bulk_check_col])
            processed_row["قیمت چکی عمده"] = bulk_check_price
        else:
            processed_row["قیمت چکی عمده"] = None
        
        # موجودی
        inventory_col = None
        for col, target in column_mapping.items():
            if target == "موجودی":
                inventory_col = col
                break
        
        if inventory_col and inventory_col in row:
            inventory = self.extract_inventory(row[inventory_col])
            processed_row["موجودی"] = inventory
        else:
            processed_row["موجودی"] = None
        
        return processed_row, errors
    
    def handle_duplicates(self, df: pd.DataFrame, strategy: str = "merge_sum_inventory") -> pd.DataFrame:
        """مدیریت ردیف‌های تکراری"""
        if "کد کالا" not in df.columns:
            return df
        
        if strategy == "merge_sum_inventory":
            # ادغام ردیف‌های تکراری و جمع موجودی
            grouped = df.groupby("کد کالا").agg({
                "شرح کالا": lambda x: max(x, key=len) if x.any() else "",  # طولانی‌ترین شرح
                "قیمت تکی": "first",
                "قیمت نقدی عمده": "first", 
                "قیمت چکی عمده": "first",
                "موجودی": "sum"
            }).reset_index()
            
            self.processing_stats['duplicate_rows'] = len(df) - len(grouped)
            return grouped
        
        elif strategy == "keep_first":
            return df.drop_duplicates(subset=["کد کالا"], keep="first")
        
        elif strategy == "keep_most_complete":
            # نگه داشتن ردیفی با بیشترین اطلاعات
            df['completeness'] = df.count(axis=1)
            return df.sort_values('completeness', ascending=False).drop_duplicates(subset=["کد کالا"], keep="first").drop('completeness', axis=1)
        
        return df
    
    def reconstruct_excel(self, 
                         input_file_path: str,
                         output_file_path: str,
                         missing_value_strategy: str = "leave_blank",
                         duplicate_strategy: str = "merge_sum_inventory",
                         output_format: str = "xlsx") -> Dict[str, Any]:
        """
        بازسازی فایل اکسل
        
        Args:
            input_file_path: مسیر فایل ورودی
            output_file_path: مسیر فایل خروجی
            missing_value_strategy: استراتژی مقادیر گم‌شده
            duplicate_strategy: استراتژی ردیف‌های تکراری
            output_format: فرمت خروجی (xlsx یا csv)
        
        Returns:
            دیکشنری شامل آمار پردازش و مسیر فایل‌های خروجی
        """
        
        try:
            # خواندن فایل ورودی
            logger.info(f"خواندن فایل ورودی: {input_file_path}")
            df = pd.read_excel(input_file_path)
            self.processing_stats['input_rows'] = len(df)
            
            # نگاشت ستون‌ها
            column_mapping = self.map_columns(df)
            logger.info(f"ستون‌های نگاشت شده: {column_mapping}")
            
            # پردازش ردیف‌ها
            processed_rows = []
            error_rows = []
            
            for idx, row in df.iterrows():
                processed_row, errors = self.process_row(row, column_mapping)
                
                if errors:
                    error_rows.append({
                        'row_number': idx + 2,  # +2 برای شماره ردیف در اکسل
                        'errors': errors,
                        'original_data': row.to_dict(),
                        'processed_data': processed_row
                    })
                    self.processing_stats['error_rows'] += 1
                else:
                    processed_rows.append(processed_row)
                    self.processing_stats['successful_rows'] += 1
            
            # ایجاد DataFrame پردازش شده
            if processed_rows:
                processed_df = pd.DataFrame(processed_rows)
                
                # مدیریت ردیف‌های تکراری
                processed_df = self.handle_duplicates(processed_df, duplicate_strategy)
                
                # ذخیره فایل خروجی اصلی
                if output_format.lower() == "xlsx":
                    processed_df.to_excel(output_file_path, index=False, engine='openpyxl')
                else:
                    processed_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
                
                logger.info(f"فایل خروجی ذخیره شد: {output_file_path}")
            else:
                logger.warning("هیچ ردیف معتبری یافت نشد")
            
            # ایجاد فایل گزارش خطا
            error_report_path = output_file_path.replace(f'.{output_format}', '_error_report.xlsx')
            if error_rows:
                error_df = pd.DataFrame(error_rows)
                error_df.to_excel(error_report_path, index=False, engine='openpyxl')
                logger.info(f"گزارش خطا ذخیره شد: {error_report_path}")
            
            # ایجاد فایل متادیتا
            metadata_path = output_file_path.replace(f'.{output_format}', '_metadata.json')
            metadata = {
                'processing_date': datetime.now().isoformat(),
                'input_file': input_file_path,
                'output_file': output_file_path,
                'error_report_file': error_report_path if error_rows else None,
                'statistics': self.processing_stats,
                'column_mapping': column_mapping,
                'settings': {
                    'missing_value_strategy': missing_value_strategy,
                    'duplicate_strategy': duplicate_strategy,
                    'output_format': output_format
                }
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"متادیتا ذخیره شد: {metadata_path}")
            
            return {
                'success': True,
                'output_file': output_file_path,
                'error_report': error_report_path if error_rows else None,
                'metadata': metadata_path,
                'statistics': self.processing_stats
            }
            
        except Exception as e:
            logger.error(f"خطا در پردازش فایل: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'statistics': self.processing_stats
            }

def reconstruct_excel_file(input_file_path: str,
                          output_file_path: str,
                          missing_value_strategy: str = "leave_blank",
                          duplicate_strategy: str = "merge_sum_inventory", 
                          output_format: str = "xlsx",
                          import_to_database: bool = False) -> Dict[str, Any]:
    """
    تابع اصلی برای بازسازی فایل اکسل
    
    Args:
        input_file_path: مسیر فایل ورودی
        output_file_path: مسیر فایل خروجی
        missing_value_strategy: استراتژی مقادیر گم‌شده
        duplicate_strategy: استراتژی ردیف‌های تکراری
        output_format: فرمت خروجی
        import_to_database: آیا محصولات به دیتابیس وارد شوند
    
    Returns:
        دیکشنری نتیجه پردازش
    """
    
    reconstructor = ExcelReconstructor()
    result = reconstructor.reconstruct_excel(
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        missing_value_strategy=missing_value_strategy,
        duplicate_strategy=duplicate_strategy,
        output_format=output_format
    )
    
    # اگر بازسازی موفق بود و درخواست واردات به دیتابیس داده شده
    if result['success'] and import_to_database:
        import_result = import_reconstructed_products_to_database(output_file_path)
        result['import_result'] = import_result
    
    return result

def import_reconstructed_products_to_database(reconstructed_file_path: str) -> Dict[str, Any]:
    """
    واردات محصولات بازسازی شده به دیتابیس
    
    Args:
        reconstructed_file_path: مسیر فایل بازسازی شده
    
    Returns:
        دیکشنری نتیجه واردات
    """
    try:
        logger.info(f"شروع واردات محصولات از فایل: {reconstructed_file_path}")
        
        # خواندن فایل بازسازی شده
        df = pd.read_excel(reconstructed_file_path)
        logger.info(f"فایل خوانده شد. تعداد ردیف‌ها: {len(df)}, ستون‌ها: {list(df.columns)}")
        
        # نگاشت ستون‌های بازسازی شده به ستون‌های دیتابیس
        column_mapping = {
            'کد کالا': 'code',
            'شرح کالا': 'name_fa', 
            'قیمت تکی': 'retail_price_cash',
            'قیمت نقدی عمده': 'bulk_price_cash',
            'قیمت چکی عمده': 'bulk_price_check',
            'موجودی': 'stock_quantity'
        }
        
        # تغییر نام ستون‌ها
        df_mapped = df.rename(columns=column_mapping)
        logger.info(f"ستون‌ها نگاشت شدند: {list(df_mapped.columns)}")
        
        # اضافه کردن ستون‌های مورد نیاز
        df_mapped['name'] = df_mapped['name_fa']  # نام انگلیسی همان نام فارسی
        df_mapped['brand_name'] = 'نامشخص'  # برند پیش‌فرض
        df_mapped['retail_price_check'] = df_mapped['retail_price_cash']  # قیمت چکی تکی همان نقدی
        df_mapped['min_order_quantity'] = 1  # حداقل سفارش پیش‌فرض
        logger.info("ستون‌های اضافی اضافه شدند")
        
        # قیمت‌ها در هزار ریال هستند، نیازی به تبدیل نیست
        # price_columns = ['retail_price_cash', 'bulk_price_cash', 'bulk_price_check', 'retail_price_check']
        
        # ذخیره فایل موقت برای واردات
        temp_import_file = reconstructed_file_path.replace('.xlsx', '_for_import.xlsx')
        df_mapped.to_excel(temp_import_file, index=False, engine='openpyxl')
        
        # واردات به دیتابیس (استفاده از منطق موجود)
        from app import app, db
        import models
        
        with app.app_context():
            logger.info("شروع واردات به دیتابیس")
            imported_count = 0
            error_count = 0
            errors = []
            
            for index, row in df_mapped.iterrows():
                logger.info(f"پردازش ردیف {index + 1}: {row.get('code', 'نامشخص')}")
                try:
                    # دریافت یا ایجاد برند
                    brand_name = row.get('brand_name', 'نامشخص')
                    brand = models.Brand.query.filter_by(name=brand_name).first()
                    if not brand:
                        brand = models.Brand(name=brand_name, name_fa=brand_name)
                        db.session.add(brand)
                        db.session.flush()
                    
                    # بررسی وجود محصول
                    code = str(row.get('code', '')).strip()
                    if not code:
                        continue
                        
                    if not models.Product.query.filter_by(sku=code).first():
                        product = models.Product(
                            sku=code,
                            code=code,  # Populate both sku and code for backward compatibility
                            name=row.get('name', ''),
                            name_fa=row.get('name_fa', ''),
                            description=row.get('description', ''),
                            description_fa=row.get('description_fa', ''),
                            brand_id=brand.id,
                            stock_quantity=int(row.get('stock_quantity', 0)),
                            min_order_quantity=int(row.get('min_order_quantity', 1)),
                            # قیمت‌ها اکنون در هزار ریال ذخیره می‌شوند
                            bulk_price_cash=row.get('bulk_price_cash', 0),
                            retail_price_cash=row.get('retail_price_cash', 0),
                            bulk_price_check=row.get('bulk_price_check', 0),
                            retail_price_check=row.get('retail_price_check', 0),
                        )
                        db.session.add(product)
                        imported_count += 1
                        logger.info(f"محصول {code} اضافه شد")
                    else:
                        logger.info(f"محصول با کد {code} قبلاً موجود است، رد شد")
                        
                except Exception as row_error:
                    error_count += 1
                    error_msg = f"خطا در ردیف {index + 2}: {str(row_error)}"
                    errors.append(error_msg)
                    logger.error(f"Error importing row {index + 2}: {str(row_error)}")
                    continue
            
            db.session.commit()
            logger.info(f"واردات تکمیل شد. {imported_count} محصول وارد شد، {error_count} خطا")
            
            # حذف فایل موقت
            try:
                os.remove(temp_import_file)
            except:
                pass
            
            return {
                'success': True,
                'imported_count': imported_count,
                'error_count': error_count,
                'errors': errors[:5]  # فقط 5 خطای اول
            }
            
    except Exception as e:
        logger.error(f"Error importing products to database: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'imported_count': 0,
            'error_count': 0
        }

# مثال استفاده
if __name__ == "__main__":
    # تست با فایل نمونه
    result = reconstruct_excel_file(
        input_file_path="test_products.xlsx",
        output_file_path="reconstructed_products.xlsx",
        missing_value_strategy="leave_blank",
        duplicate_strategy="merge_sum_inventory",
        output_format="xlsx"
    )
    
    print("نتیجه پردازش:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
