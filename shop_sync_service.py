"""
سرویس همگام‌سازی فروشگاه با cache تدبیر
Shop Sync Service with Tadbir Cache
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

from models import (
    db, Product, TadbirProductCache, TadbirPriceCache, 
    TadbirInventoryCache, TadbirSyncLog
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShopSyncService:
    """سرویس همگام‌سازی فروشگاه با cache تدبیر"""
    
    def __init__(self):
        """Initialize Shop sync service"""
        self.default_stock_code = '10'  # کد انبار پیش‌فرض
        # ISACO warehouse code as string to match TadbirInventoryCache.stock_code
        from app import app as flask_app
        self.isaco_stock_code = str(flask_app.config.get('ISACO_WAREHOUSE_ID', 15))
        
    def _create_sync_log(self, sync_type: str) -> TadbirSyncLog:
        """Create sync log entry"""
        sync_log = TadbirSyncLog(
            sync_type=sync_type,
            status='started',
            started_at=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.flush()
        return sync_log
    
    def _update_sync_log(self, sync_log: TadbirSyncLog, status: str, 
                        records_processed: int = 0, records_successful: int = 0, 
                        records_failed: int = 0, error_message: str = None):
        """Update sync log entry"""
        sync_log.status = status
        sync_log.records_processed = records_processed
        sync_log.records_successful = records_successful
        sync_log.records_failed = records_failed
        sync_log.error_message = error_message
        
        if status in ['completed', 'failed', 'cancelled']:
            sync_log.completed_at = datetime.utcnow()
            if sync_log.started_at:
                sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
        
        db.session.commit()
    
    def sync_shop_prices(self) -> TadbirSyncLog:
        """همگام‌سازی قیمت‌های فروشگاه با cache تدبیر"""
        sync_log = self._create_sync_log('shop_prices')
        
        try:
            logger.info("Starting shop price sync from Tadbir cache")
            
            # Get all products from shop
            products = Product.query.all()
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            for product in products:
                try:
                    records_processed += 1
                    
                    # Get prices for this product from TadbirPriceCache
                    # لیست 13 = چکی (برای تکی و عمده)
                    # لیست 14 = نقدی (فقط برای عمده)
                    cash_prices = TadbirPriceCache.query.filter_by(
                        item_code=product.sku,
                        price_list_key=14  # لیست قیمت نقدی
                    ).order_by(TadbirPriceCache.last_update.desc()).first()
                    
                    check_prices = TadbirPriceCache.query.filter_by(
                        item_code=product.sku,
                        price_list_key=13  # لیست قیمت چکی
                    ).order_by(TadbirPriceCache.last_update.desc()).first()
                    
                    # If no prices found, skip this product
                    if not cash_prices and not check_prices:
                        logger.debug(f"No prices found for product {product.sku}")
                        continue
                    
                    # Update product prices
                    updated = False
                    
                    # قیمت نقدی عمده (لیست 14)
                    if cash_prices and cash_prices.final_price:
                        product.bulk_price_cash = float(cash_prices.final_price)
                        updated = True
                    
                    # قیمت چکی (لیست 13) - برای هر دو تکی و عمده
                    if check_prices and check_prices.final_price:
                        product.retail_price_check = float(check_prices.final_price)
                        product.retail_price_cash = float(check_prices.final_price)  # برای سازگاری
                        product.bulk_price_check = float(check_prices.final_price)
                        updated = True
                    
                    # اگر قیمت نقدی عمده نداریم، از چکی استفاده می‌کنیم
                    if not cash_prices and check_prices and check_prices.final_price:
                        product.bulk_price_cash = float(check_prices.final_price)
                        updated = True
                    
                    if updated:
                        product.updated_at = datetime.utcnow()
                        records_successful += 1
                        logger.debug(f"Updated prices for product {product.sku}")
                    else:
                        logger.warning(f"No valid prices to update for product {product.sku}")

                    # ISACO special: map four plans from specific Tadbir price lists
                    try:
                        # Get ISACO prices from specific lists
                        isaco_cash = TadbirPriceCache.query.filter_by(
                            item_code=product.sku,
                            price_list_key=61  # نقدی
                        ).order_by(TadbirPriceCache.last_update.desc()).first()
                        
                        isaco_1m = TadbirPriceCache.query.filter_by(
                            item_code=product.sku,
                            price_list_key=62  # یکماهه
                        ).order_by(TadbirPriceCache.last_update.desc()).first()
                        
                        isaco_2m = TadbirPriceCache.query.filter_by(
                            item_code=product.sku,
                            price_list_key=63  # دوماهه
                        ).order_by(TadbirPriceCache.last_update.desc()).first()
                        
                        isaco_3m = TadbirPriceCache.query.filter_by(
                            item_code=product.sku,
                            price_list_key=60  # سه‌ماهه
                        ).order_by(TadbirPriceCache.last_update.desc()).first()
                        
                        # Update ISACO prices if any are available
                        if any([isaco_cash, isaco_1m, isaco_2m, isaco_3m]):
                            product.is_isaco_wh15 = True
                            
                            if isaco_cash and isaco_cash.final_price is not None:
                                product.isaco_cash = float(isaco_cash.final_price)
                            
                            if isaco_1m and isaco_1m.final_price is not None:
                                product.isaco_1m = float(isaco_1m.final_price)
                            
                            if isaco_2m and isaco_2m.final_price is not None:
                                product.isaco_2m = float(isaco_2m.final_price)
                            
                            if isaco_3m and isaco_3m.final_price is not None:
                                product.isaco_3m = float(isaco_3m.final_price)
                            
                            updated = True
                    except Exception as ie:
                        logger.debug(f"ISACO pricing map skipped for {product.sku}: {ie}")
                        
                except Exception as e:
                    logger.error(f"Error updating prices for product {product.sku}: {str(e)}")
                    records_failed += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
            self._update_sync_log(
                sync_log, 'completed',
                records_processed, records_successful, records_failed
            )
            
            logger.info(f"Shop price sync completed: {records_successful}/{records_processed} successful")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Shop price sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def sync_shop_inventory(self, stock_code: str = None) -> TadbirSyncLog:
        """همگام‌سازی موجودی فروشگاه با cache تدبیر"""
        sync_log = self._create_sync_log('shop_inventory')
        
        if stock_code is None:
            stock_code = self.default_stock_code
        
        try:
            logger.info(f"Starting shop inventory sync from Tadbir cache (stock code: {stock_code})")
            
            # Get all products from shop
            products = Product.query.all()
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            for product in products:
                try:
                    records_processed += 1
                    
                    # Get inventory for this product from TadbirInventoryCache
                    # ابتدا انبار اصلی (10) را چک می‌کنیم
                    inventory = TadbirInventoryCache.query.filter_by(
                        item_code=product.sku,
                        stock_code=stock_code
                    ).first()

                    # ISACO WH15 inventory flagging and fallback
                    isaco_inventory = TadbirInventoryCache.query.filter_by(
                        item_code=product.sku,
                        stock_code=self.isaco_stock_code
                    ).first()
                    
                    # اگر موجودی انبار اصلی نبود یا صفر بود، از انبار ایساکو استفاده می‌کنیم
                    if not inventory or inventory.available_quantity is None or float(inventory.available_quantity or 0) == 0:
                        if isaco_inventory and isaco_inventory.available_quantity is not None and float(isaco_inventory.available_quantity or 0) > 0:
                            inventory = isaco_inventory
                            product.is_isaco_wh15 = True
                    elif isaco_inventory:
                        # اگر موجودی انبار اصلی وجود دارد، فقط پرچم را تنظیم می‌کنیم
                        product.is_isaco_wh15 = True

                    if not inventory:
                        logger.debug(f"No inventory found for product {product.sku}")
                        continue
                    
                    # Update product inventory
                    # استفاده از available_quantity که موجودی قابل فروش است
                    old_quantity = product.stock_quantity
                    try:
                        stock_qty = float(inventory.available_quantity or 0)
                        # اگر موجودی صفر است، حداقل 1 قرار می‌دهیم تا کالا نمایش داده شود
                        product.stock_quantity = int(stock_qty) if stock_qty > 0 else 1
                    except (ValueError, TypeError):
                        # اگر خطا در تبدیل بود، حداقل 1 قرار می‌دهیم
                        product.stock_quantity = 1
                    product.updated_at = datetime.utcnow()
                    
                    records_successful += 1
                    
                    if old_quantity != product.stock_quantity:
                        logger.info(f"Updated inventory for product {product.sku}: {old_quantity} -> {product.stock_quantity}")
                    
                except Exception as e:
                    logger.error(f"Error updating inventory for product {product.sku}: {str(e)}")
                    records_failed += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
            self._update_sync_log(
                sync_log, 'completed',
                records_processed, records_successful, records_failed
            )
            
            logger.info(f"Shop inventory sync completed: {records_successful}/{records_processed} successful")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Shop inventory sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def sync_shop_products(self) -> TadbirSyncLog:
        """همگام‌سازی اطلاعات محصولات فروشگاه با cache تدبیر"""
        sync_log = self._create_sync_log('shop_products')
        
        try:
            logger.info("Starting shop product sync from Tadbir cache")
            
            # مرحله 1: ایجاد خودکار محصولات جدید بر اساس TadbirProductCache
            tadbir_products = TadbirProductCache.query.all()
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            for t_product in tadbir_products:
                try:
                    records_processed += 1
                    sku = t_product.item_code
                    if not sku:
                        records_failed += 1
                        continue
                    
                    existing = Product.query.filter_by(sku=sku).first()
                    if existing:
                        continue
                    
                    # Build minimal viable product
                    name_source = t_product.description or sku
                    new_product = Product(
                        sku=sku,
                        name=name_source,
                        name_fa=name_source,
                        description_fa=t_product.description,
                        is_active=True,  # همیشه فعال برای نمایش در فروشگاه
                        # قیمت‌ها به هزار ریال هستند؛ در نبود قیمت، صفر تنظیم می‌شود
                        bulk_price_cash=0.0,
                        retail_price_cash=0.0,
                        bulk_price_check=0.0,
                        retail_price_check=0.0,
                        stock_quantity=0,
                    )
                    
                    # تلاش برای مقداردهی قیمت‌ها از کش قیمت تدبیر
                    latest_cash = TadbirPriceCache.query.filter_by(
                        item_code=sku, price_list_key=14
                    ).order_by(TadbirPriceCache.last_update.desc()).first()
                    latest_check = TadbirPriceCache.query.filter_by(
                        item_code=sku, price_list_key=13
                    ).order_by(TadbirPriceCache.last_update.desc()).first()
                    
                    if latest_cash and latest_cash.final_price is not None:
                        new_product.bulk_price_cash = float(latest_cash.final_price)
                    if latest_check and latest_check.final_price is not None:
                        check_price = float(latest_check.final_price)
                        new_product.retail_price_check = check_price
                        new_product.retail_price_cash = check_price  # برای سازگاری
                        new_product.bulk_price_check = check_price
                        # اگر قیمت نقدی عمده نداریم، از چکی استفاده شود
                        if new_product.bulk_price_cash == 0.0:
                            new_product.bulk_price_cash = check_price
                    
                    # تلاش برای مقداردهی موجودی از کش موجودی تدبیر
                    # ابتدا انبار اصلی (10) را چک می‌کنیم
                    inv = TadbirInventoryCache.query.filter_by(
                        item_code=sku, stock_code=self.default_stock_code
                    ).first()
                    
                    # اگر موجودی انبار اصلی نبود یا صفر بود، انبار ایساکو (15) را چک می‌کنیم
                    if not inv or inv.available_quantity is None or float(inv.available_quantity or 0) == 0:
                        inv_isaco = TadbirInventoryCache.query.filter_by(
                            item_code=sku, stock_code=self.isaco_stock_code
                        ).first()
                        if inv_isaco and inv_isaco.available_quantity is not None and float(inv_isaco.available_quantity or 0) > 0:
                            inv = inv_isaco
                            new_product.is_isaco_wh15 = True
                    
                    if inv and inv.available_quantity is not None:
                        try:
                            stock_qty = float(inv.available_quantity)
                            new_product.stock_quantity = int(stock_qty) if stock_qty > 0 else 1  # حداقل 1 برای نمایش
                        except Exception:
                            new_product.stock_quantity = 1  # حداقل 1 برای نمایش
                    else:
                        # اگر موجودی وجود ندارد، حداقل 1 قرار می‌دهیم تا کالا نمایش داده شود
                        new_product.stock_quantity = 1
                    
                    db.session.add(new_product)
                    records_successful += 1
                
                except Exception as e:
                    logger.error(f"Error creating product from Tadbir cache for {t_product.item_code}: {str(e)}")
                    records_failed += 1
                    continue
            
            # مرحله 1.5: ایجاد کالاهایی که در موجودی هستند ولی در TadbirProductCache نیستند
            all_inventory_items = db.session.query(TadbirInventoryCache.item_code).distinct().all()
            for (item_code,) in all_inventory_items:
                if not item_code:
                    continue
                
                # چک می‌کنیم که آیا کالا در Product وجود دارد
                existing = Product.query.filter_by(sku=item_code).first()
                if existing:
                    continue
                
                # چک می‌کنیم که آیا کالا در TadbirProductCache وجود دارد (اگر وجود دارد، قبلاً ایجاد شده)
                tadbir_product = TadbirProductCache.query.filter_by(item_code=item_code).first()
                if tadbir_product:
                    continue
                
                try:
                    records_processed += 1
                    
                    # ایجاد کالای جدید با اطلاعات حداقلی
                    new_product = Product(
                        sku=item_code,
                        name=item_code,
                        name_fa=item_code,
                        description_fa=f"کالا با کد {item_code}",
                        is_active=True,  # به صورت پیش‌فرض فعال
                        bulk_price_cash=0.0,
                        retail_price_cash=0.0,
                        bulk_price_check=0.0,
                        retail_price_check=0.0,
                        stock_quantity=0,
                    )
                    
                    # تلاش برای مقداردهی موجودی
                    inv = TadbirInventoryCache.query.filter_by(
                        item_code=item_code, stock_code=self.default_stock_code
                    ).first()
                    
                    if not inv or inv.available_quantity is None or float(inv.available_quantity or 0) == 0:
                        inv = TadbirInventoryCache.query.filter_by(
                            item_code=item_code, stock_code=self.isaco_stock_code
                        ).first()
                        if inv and inv.available_quantity is not None and float(inv.available_quantity or 0) > 0:
                            new_product.is_isaco_wh15 = True
                    
                    if inv and inv.available_quantity is not None:
                        try:
                            stock_qty = float(inv.available_quantity)
                            new_product.stock_quantity = int(stock_qty) if stock_qty > 0 else 1  # حداقل 1 برای نمایش
                        except Exception:
                            new_product.stock_quantity = 1  # حداقل 1 برای نمایش
                    else:
                        # اگر موجودی وجود ندارد، حداقل 1 قرار می‌دهیم تا کالا نمایش داده شود
                        new_product.stock_quantity = 1
                    
                    # تلاش برای مقداردهی قیمت‌ها
                    latest_cash = TadbirPriceCache.query.filter_by(
                        item_code=item_code, price_list_key=14
                    ).order_by(TadbirPriceCache.last_update.desc()).first()
                    latest_check = TadbirPriceCache.query.filter_by(
                        item_code=item_code, price_list_key=13
                    ).order_by(TadbirPriceCache.last_update.desc()).first()
                    
                    if latest_cash and latest_cash.final_price is not None:
                        new_product.bulk_price_cash = float(latest_cash.final_price)
                    if latest_check and latest_check.final_price is not None:
                        check_price = float(latest_check.final_price)
                        new_product.retail_price_check = check_price
                        new_product.retail_price_cash = check_price
                        new_product.bulk_price_check = check_price
                        if new_product.bulk_price_cash == 0.0:
                            new_product.bulk_price_cash = check_price
                    
                    db.session.add(new_product)
                    records_successful += 1
                    logger.info(f"Created product from inventory cache: {item_code}")
                    
                except Exception as e:
                    logger.error(f"Error creating product from inventory cache for {item_code}: {str(e)}")
                    records_failed += 1
                    continue
            
            # مرحله 2: بروزرسانی اطلاعات محصولات موجود بر اساس TadbirProductCache
            products = Product.query.all()
            
            
            for product in products:
                try:
                    records_processed += 1
                    
                    # Get product info from TadbirProductCache
                    tadbir_product = TadbirProductCache.query.filter_by(
                        item_code=product.sku
                    ).first()
                    
                    if not tadbir_product:
                        logger.debug(f"No Tadbir product found for {product.sku}")
                        continue
                    
                    # Update product information if changed
                    updated = False
                    
                    # بروزرسانی وضعیت فعال بودن
                    if product.is_active != tadbir_product.is_active:
                        product.is_active = tadbir_product.is_active
                        updated = True
                        logger.info(f"Updated active status for product {product.sku}: {tadbir_product.is_active}")
                    
                    # بروزرسانی توضیحات فارسی اگر خالی باشد
                    if tadbir_product.description and not product.description_fa:
                        product.description_fa = tadbir_product.description
                        updated = True
                    
                    # بروزرسانی نام فارسی اگر خالی باشد
                    if tadbir_product.description and not product.name_fa:
                        product.name_fa = tadbir_product.description[:200]  # محدود به 200 کاراکتر
                        updated = True
                    
                    if updated:
                        product.updated_at = datetime.utcnow()
                        records_successful += 1
                        
                except Exception as e:
                    logger.error(f"Error updating product info for {product.sku}: {str(e)}")
                    records_failed += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
            self._update_sync_log(
                sync_log, 'completed',
                records_processed, records_successful, records_failed
            )
            
            logger.info(f"Shop product sync completed: {records_successful}/{records_processed} successful")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Shop product sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def full_shop_sync(self) -> Dict[str, TadbirSyncLog]:
        """همگام‌سازی کامل فروشگاه (قیمت‌ها، موجودی‌ها و اطلاعات محصولات)"""
        logger.info("Starting full shop sync")
        
        sync_logs = {}
        
        try:
            # 1. Sync product information
            products_log = self.sync_shop_products()
            sync_logs['products'] = products_log
            
            # 2. Sync inventory
            inventory_log = self.sync_shop_inventory()
            sync_logs['inventory'] = inventory_log
            
            # 3. Sync prices
            prices_log = self.sync_shop_prices()
            sync_logs['prices'] = prices_log
            
            logger.info("Full shop sync completed successfully")
            return sync_logs
            
        except Exception as e:
            logger.error(f"Full shop sync failed: {str(e)}")
            return sync_logs
    
    def get_sync_status(self) -> Dict[str, Any]:
        """دریافت وضعیت همگام‌سازی فروشگاه"""
        try:
            # Get last sync for each type
            last_products_sync = TadbirSyncLog.query.filter_by(
                sync_type='shop_products'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            last_inventory_sync = TadbirSyncLog.query.filter_by(
                sync_type='shop_inventory'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            last_prices_sync = TadbirSyncLog.query.filter_by(
                sync_type='shop_prices'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            # Get product count
            products_count = Product.query.count()
            active_products_count = Product.query.filter_by(is_active=True).count()
            
            return {
                'last_products_sync': {
                    'status': last_products_sync.status if last_products_sync else None,
                    'started_at': last_products_sync.started_at if last_products_sync else None,
                    'completed_at': last_products_sync.completed_at if last_products_sync else None,
                    'records_successful': last_products_sync.records_successful if last_products_sync else 0
                },
                'last_inventory_sync': {
                    'status': last_inventory_sync.status if last_inventory_sync else None,
                    'started_at': last_inventory_sync.started_at if last_inventory_sync else None,
                    'completed_at': last_inventory_sync.completed_at if last_inventory_sync else None,
                    'records_successful': last_inventory_sync.records_successful if last_inventory_sync else 0
                },
                'last_prices_sync': {
                    'status': last_prices_sync.status if last_prices_sync else None,
                    'started_at': last_prices_sync.started_at if last_prices_sync else None,
                    'completed_at': last_prices_sync.completed_at if last_prices_sync else None,
                    'records_successful': last_prices_sync.records_successful if last_prices_sync else 0
                },
                'shop_stats': {
                    'total_products': products_count,
                    'active_products': active_products_count
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {str(e)}")
            return {'error': str(e)}


# Global service instance
_shop_sync_instance = None


def get_shop_sync_service() -> ShopSyncService:
    """Get global shop sync service instance"""
    global _shop_sync_instance
    if _shop_sync_instance is None:
        _shop_sync_instance = ShopSyncService()
    return _shop_sync_instance

