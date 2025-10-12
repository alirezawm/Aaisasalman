"""
سرویس همگام‌سازی با تدبیر
Tadbir Accounting System Sync Service
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
import pytz

from models import db, TadbirSyncLog, TadbirProductCache, TadbirPriceCache, TadbirInventoryCache, TadbirSyncSettings
from tadbir_api_service import TadbirAPIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TadbirSyncService:
    """سرویس همگام‌سازی با تدبیر"""
    
    def __init__(self):
        """Initialize Tadbir sync service"""
        self.api_service = TadbirAPIService()
        self.batch_size = self._get_setting('batch_size', 1000)
        self.retry_attempts = self._get_setting('retry_attempts', 3)
        self.retry_delay = self._get_setting('retry_delay_seconds', 30)
        self.enable_incremental = self._get_setting('enable_incremental_sync', True)
        
    def _get_setting(self, key: str, default_value: Any) -> Any:
        """Get setting value from database"""
        try:
            setting = TadbirSyncSettings.query.filter_by(setting_key=key).first()
            if setting:
                # Try to convert to appropriate type
                if isinstance(default_value, bool):
                    return setting.setting_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default_value, int):
                    return int(setting.setting_value)
                elif isinstance(default_value, float):
                    return float(setting.setting_value)
                else:
                    return setting.setting_value
            return default_value
        except Exception as e:
            logger.warning(f"Failed to get setting {key}: {str(e)}")
            return default_value
    
    def _create_sync_log(self, sync_type: str) -> TadbirSyncLog:
        """Create sync log entry"""
        sync_log = TadbirSyncLog(
            sync_type=sync_type,
            status='started',
            started_at=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.flush()  # Get the ID
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
    
    def sync_products(self, incremental: bool = True) -> TadbirSyncLog:
        """همگام‌سازی کالاها"""
        sync_log = self._create_sync_log('products')
        
        try:
            logger.info(f"Starting product sync (incremental: {incremental})")
            
            # Get last update time for incremental sync
            last_update = None
            if incremental and self.enable_incremental:
                last_sync = TadbirSyncLog.query.filter_by(
                    sync_type='products', 
                    status='completed'
                ).order_by(TadbirSyncLog.completed_at.desc()).first()
                
                if last_sync:
                    last_update = last_sync.started_at
            
            # Get products from Tadbir API
            # For full sync, get all products; for incremental, use batch size
            if incremental and last_update:
                # Incremental sync - use batch size
                products = self.api_service.get_products(
                    last_update=last_update,
                    top=self.batch_size
                )
            else:
                # Full sync - get all products in batches
                products = []
                skip = 0
                batch_products = []
                
                while True:
                    batch_products = self.api_service.get_products(
                        last_update=last_update,
                        skip=skip,
                        top=self.batch_size
                    )
                    
                    if not batch_products:
                        break
                    
                    products.extend(batch_products)
                    skip += self.batch_size
                    
                    # Log progress
                    logger.info(f"Retrieved {len(products)} products so far...")
                    
                    # Safety check to prevent infinite loop
                    if len(batch_products) < self.batch_size:
                        break
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            for product_data in products:
                try:
                    records_processed += 1
                    
                    # Extract product data
                    item_code = product_data.get('Itemcode')
                    if not item_code:
                        records_failed += 1
                        continue
                    
                    # Check if product already exists
                    existing_product = TadbirProductCache.query.filter_by(item_code=item_code).first()
                    
                    if existing_product:
                        # Update existing product
                        existing_product.description = product_data.get('Description')
                        existing_product.alias = product_data.get('Alias')
                        existing_product.unit = product_data.get('Unit')
                        existing_product.techspec = product_data.get('Techspec')
                        existing_product.barcode = product_data.get('BarCode')
                        existing_product.is_item = product_data.get('IsItem', True)
                        existing_product.is_active = not product_data.get('UnActive', False)
                        existing_product.tadbir_guid = product_data.get('GeneralDescGuid')
                        existing_product.last_update = self._parse_datetime(product_data.get('LastUpdate'))
                        existing_product.cached_at = datetime.utcnow()
                    else:
                        # Create new product
                        new_product = TadbirProductCache(
                            item_code=item_code,
                            description=product_data.get('Description'),
                            alias=product_data.get('Alias'),
                            unit=product_data.get('Unit'),
                            techspec=product_data.get('Techspec'),
                            barcode=product_data.get('BarCode'),
                            is_item=product_data.get('IsItem', True),
                            is_active=not product_data.get('UnActive', False),
                            tadbir_guid=product_data.get('GeneralDescGuid'),
                            last_update=self._parse_datetime(product_data.get('LastUpdate')),
                            cached_at=datetime.utcnow()
                        )
                        db.session.add(new_product)
                    
                    records_successful += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process product {product_data.get('Itemcode', 'unknown')}: {str(e)}")
                    records_failed += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
            self._update_sync_log(
                sync_log, 'completed', 
                records_processed, records_successful, records_failed
            )
            
            logger.info(f"Product sync completed: {records_successful}/{records_processed} successful")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Product sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def sync_inventory(self, stock_code: str = '10') -> TadbirSyncLog:
        """همگام‌سازی موجودی"""
        sync_log = self._create_sync_log('inventory')
        
        try:
            logger.info(f"Starting inventory sync for stock code: {stock_code}")
            
            # Get inventory from Tadbir API in batches
            inventory_data = []
            skip = 0
            batch_inventory = []
            
            while True:
                batch_inventory = self.api_service.get_inventory(
                    stock_code=stock_code,
                    skip=skip,
                    top=self.batch_size
                )
                
                if not batch_inventory:
                    break
                
                inventory_data.extend(batch_inventory)
                skip += self.batch_size
                
                # Log progress
                logger.info(f"Retrieved {len(inventory_data)} inventory records so far...")
                
                # Safety check to prevent infinite loop
                if len(batch_inventory) < self.batch_size:
                    break
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            for inv_data in inventory_data:
                try:
                    records_processed += 1
                    
                    # Use 'Itemcode' instead of 'ItemCode' based on the API response
                    item_code = inv_data.get('Itemcode')
                    if not item_code:
                        records_failed += 1
                        continue
                    
                    # Check if inventory record already exists
                    existing_inventory = TadbirInventoryCache.query.filter_by(
                        item_code=item_code, 
                        stock_code=stock_code
                    ).first()
                    
                    if existing_inventory:
                        # Update existing inventory
                        # Map API fields to our model fields
                        existing_inventory.quantity = inv_data.get('Remain', 0)  # Use 'Remain' field
                        existing_inventory.reserved_quantity = 0  # Not available in API
                        existing_inventory.available_quantity = inv_data.get('Remain', 0)  # Same as quantity
                        existing_inventory.last_update = datetime.utcnow()  # Use current time
                        existing_inventory.cached_at = datetime.utcnow()
                    else:
                        # Create new inventory record
                        new_inventory = TadbirInventoryCache(
                            item_code=item_code,
                            stock_code=stock_code,
                            quantity=inv_data.get('Remain', 0),  # Use 'Remain' field
                            reserved_quantity=0,  # Not available in API
                            available_quantity=inv_data.get('Remain', 0),  # Same as quantity
                            last_update=datetime.utcnow(),  # Use current time
                            cached_at=datetime.utcnow()
                        )
                        db.session.add(new_inventory)
                    
                    records_successful += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process inventory {inv_data.get('ItemCode', 'unknown')}: {str(e)}")
                    records_failed += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
            self._update_sync_log(
                sync_log, 'completed', 
                records_processed, records_successful, records_failed
            )
            
            logger.info(f"Inventory sync completed: {records_successful}/{records_processed} successful")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Inventory sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def sync_prices(self, price_list_keys: Optional[List[int]] = None) -> TadbirSyncLog:
        """همگام‌سازی قیمت‌ها"""
        sync_log = self._create_sync_log('prices')
        
        try:
            logger.info("Starting price sync")
            
            # Use default price list keys if not provided
            if not price_list_keys:
                # Get all price list keys from API service configuration
                price_list_keys = [category['price_list_key'] for category in self.api_service.price_categories.values()]
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            for price_list_key in price_list_keys:
                try:
                    # Get prices for this price list in batches
                    prices = []
                    skip = 0
                    batch_prices = []
                    
                    while True:
                        batch_prices = self.api_service.get_prices(
                            price_list_key=price_list_key,
                            skip=skip,
                            top=self.batch_size
                        )
                        
                        if not batch_prices:
                            break
                        
                        prices.extend(batch_prices)
                        skip += self.batch_size
                        
                        # Log progress
                        logger.info(f"Retrieved {len(prices)} prices for price list {price_list_key} so far...")
                        
                        # Safety check to prevent infinite loop
                        if len(batch_prices) < self.batch_size:
                            break
                    
                    for price_data in prices:
                        try:
                            records_processed += 1
                            
                            item_code = price_data.get('ItemCode')
                            if not item_code:
                                records_failed += 1
                                continue
                            
                            # Determine price type based on price list key
                            price_type = self._get_price_type(price_list_key)
                            # قیمت تدبیر به ریال است، تبدیل به هزار ریال
                            base_price = float(price_data.get('Price', 0)) / 1000
                            
                            # Calculate final price with markup
                            final_price = self.api_service.calculate_final_price(base_price, price_type)
                            
                            # Check if price record already exists
                            existing_price = TadbirPriceCache.query.filter_by(
                                item_code=item_code,
                                price_type=price_type
                            ).first()
                            
                            if existing_price:
                                # Update existing price
                                existing_price.price_list_key = price_list_key
                                existing_price.base_price = base_price
                                existing_price.final_price = final_price
                                existing_price.discount_percentage = price_data.get('DiscountPrcnt', 0)
                                # تخفیف را نیز به هزار ریال تبدیل می‌کنیم
                                existing_price.discount_amount = float(price_data.get('Discount', 0)) / 1000
                                existing_price.min_order = price_data.get('MinOrder', 0)
                                existing_price.tadbir_guid = price_data.get('GUID')
                                existing_price.last_update = self._parse_datetime(price_data.get('LastUpdate'))
                                existing_price.cached_at = datetime.utcnow()
                            else:
                                # Create new price record
                                new_price = TadbirPriceCache(
                                    item_code=item_code,
                                    price_list_key=price_list_key,
                                    price_type=price_type,
                                    base_price=base_price,
                                    final_price=final_price,
                                    discount_percentage=price_data.get('DiscountPrcnt', 0),
                                    # تخفیف را نیز به هزار ریال تبدیل می‌کنیم
                                    discount_amount=float(price_data.get('Discount', 0)) / 1000,
                                    min_order=price_data.get('MinOrder', 0),
                                    tadbir_guid=price_data.get('GUID'),
                                    last_update=self._parse_datetime(price_data.get('LastUpdate')),
                                    cached_at=datetime.utcnow()
                                )
                                db.session.add(new_price)
                            
                            records_successful += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to process price {price_data.get('ItemCode', 'unknown')}: {str(e)}")
                            records_failed += 1
                            continue
                            
                except Exception as e:
                    logger.error(f"Failed to process price list {price_list_key}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            self._update_sync_log(
                sync_log, 'completed', 
                records_processed, records_successful, records_failed
            )
            
            logger.info(f"Price sync completed: {records_successful}/{records_processed} successful")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Price sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def full_sync(self) -> List[TadbirSyncLog]:
        """همگام‌سازی کامل"""
        logger.info("Starting full sync")
        
        sync_logs = []
        
        try:
            # Sync products first
            products_log = self.sync_products(incremental=False)
            sync_logs.append(products_log)
            
            # Sync inventory
            inventory_log = self.sync_inventory()
            sync_logs.append(inventory_log)
            
            # Sync prices
            prices_log = self.sync_prices()
            sync_logs.append(prices_log)
            
            logger.info("Full sync completed successfully")
            return sync_logs
            
        except Exception as e:
            logger.error(f"Full sync failed: {str(e)}")
            return sync_logs
    
    def _get_price_type(self, price_list_key: int) -> str:
        """Get price type from price list key"""
        # لیست 13 = چکی (برای تکی و عمده)
        # لیست 14 = نقدی (فقط برای عمده)
        if price_list_key == 14:
            return 'bulk_cash'  # لیست قیمت نقدی عمده
        elif price_list_key == 13:
            # لیست 13 برای هر دو retail_check و bulk_check استفاده می‌شود
            # در اینجا به صورت پیش‌فرض retail_check برمی‌گردانیم
            return 'retail_check'  # لیست قیمت چکی
        else:
            return 'bulk_cash'  # Default fallback
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse datetime string from Tadbir API"""
        if not datetime_str:
            return None
        
        try:
            # Try different datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            logger.warning(f"Could not parse datetime: {datetime_str}")
            return datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error parsing datetime {datetime_str}: {str(e)}")
            return datetime.utcnow()
    
    def _convert_utc_to_tehran(self, utc_datetime):
        """تبدیل زمان UTC به زمان تهران"""
        if utc_datetime is None:
            return None
        
        # Set UTC timezone if not set
        if utc_datetime.tzinfo is None:
            utc_datetime = pytz.utc.localize(utc_datetime)
        
        # Convert to Tehran timezone
        tehran_tz = pytz.timezone('Asia/Tehran')
        return utc_datetime.astimezone(tehran_tz)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        try:
            # Get last sync for each type
            last_products_sync = TadbirSyncLog.query.filter_by(
                sync_type='products'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            last_inventory_sync = TadbirSyncLog.query.filter_by(
                sync_type='inventory'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            last_prices_sync = TadbirSyncLog.query.filter_by(
                sync_type='prices'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            # Get cache counts
            products_count = TadbirProductCache.query.count()
            inventory_count = TadbirInventoryCache.query.count()
            prices_count = TadbirPriceCache.query.count()
            
            return {
                'last_products_sync': {
                    'status': last_products_sync.status if last_products_sync else None,
                    'started_at': self._convert_utc_to_tehran(last_products_sync.started_at) if last_products_sync else None,
                    'completed_at': self._convert_utc_to_tehran(last_products_sync.completed_at) if last_products_sync and last_products_sync.completed_at else None,
                    'records_successful': last_products_sync.records_successful if last_products_sync else 0
                },
                'last_inventory_sync': {
                    'status': last_inventory_sync.status if last_inventory_sync else None,
                    'started_at': self._convert_utc_to_tehran(last_inventory_sync.started_at) if last_inventory_sync else None,
                    'completed_at': self._convert_utc_to_tehran(last_inventory_sync.completed_at) if last_inventory_sync and last_inventory_sync.completed_at else None,
                    'records_successful': last_inventory_sync.records_successful if last_inventory_sync else 0
                },
                'last_prices_sync': {
                    'status': last_prices_sync.status if last_prices_sync else None,
                    'started_at': self._convert_utc_to_tehran(last_prices_sync.started_at) if last_prices_sync else None,
                    'completed_at': self._convert_utc_to_tehran(last_prices_sync.completed_at) if last_prices_sync and last_prices_sync.completed_at else None,
                    'records_successful': last_prices_sync.records_successful if last_prices_sync else 0
                },
                'cache_counts': {
                    'products': products_count,
                    'inventory': inventory_count,
                    'prices': prices_count
                },
                'api_status': self.api_service.get_api_status()
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {str(e)}")
            return {'error': str(e)}
    
    def sync_prices_to_products(self) -> Dict[str, Any]:
        """همگام‌سازی قیمت‌های تدبیر با محصولات محلی"""
        try:
            logger.info("Starting price sync to products")
            
            from models import Product, TadbirPriceCache
            
            # Get all local products
            products = Product.query.all()
            updated_count = 0
            skipped_count = 0
            
            for product in products:
                try:
                    # Get prices for this product from TadbirPriceCache for both price lists
                    cash_prices = TadbirPriceCache.query.filter_by(
                        item_code=product.sku,
                        price_list_key=14  # لیست قیمت نقدی
                    ).all()
                    
                    check_prices = TadbirPriceCache.query.filter_by(
                        item_code=product.sku,
                        price_list_key=13  # لیست قیمت چکی
                    ).all()
                    
                    if not cash_prices and not check_prices:
                        skipped_count += 1
                        continue
                    
                    # Get the best prices from each list
                    best_cash_price = self._get_best_price(cash_prices) if cash_prices else None
                    best_check_price = self._get_best_price(check_prices) if check_prices else None
                    
                    # Use cash price as base if available, otherwise use check price
                    base_price_cash = None
                    base_price_check = None
                    
                    if best_cash_price:
                        base_price_cash = float(best_cash_price.final_price)
                    
                    if best_check_price:
                        base_price_check = float(best_check_price.final_price)
                    
                    # If we don't have both prices, use the available one for both
                    if base_price_cash is None and base_price_check is not None:
                        base_price_cash = base_price_check
                    elif base_price_check is None and base_price_cash is not None:
                        base_price_check = base_price_cash
                    elif base_price_cash is None and base_price_check is None:
                        skipped_count += 1
                        continue
                    
                    # استفاده از قیمت نهایی تدبیر بدون markup اضافی
                    # لیست 13 = چکی (برای تکی و عمده)
                    # لیست 14 = نقدی (فقط برای عمده)
                    
                    # Set prices directly from Tadbir final prices (no additional markup)
                    # خریدار تکی فقط قیمت چکی دارد
                    product.retail_price_check = base_price_check  # قیمت نهایی تدبیر - چکی
                    product.retail_price_cash = base_price_check  # برای سازگاری با کد قدیمی - همان قیمت چکی
                    
                    # خریدار عمده هر دو قیمت دارد
                    product.bulk_price_cash = base_price_cash  # قیمت نهایی تدبیر - نقدی عمده
                    product.bulk_price_check = base_price_check  # قیمت نهایی تدبیر - چکی عمده
                    
                    product.updated_at = datetime.utcnow()
                    updated_count += 1
                    
                    logger.info(f"Updated prices for product {product.sku}: retail_check={product.retail_price_check}, bulk_cash={product.bulk_price_cash}, bulk_check={product.bulk_price_check}")
                        
                except Exception as e:
                    logger.error(f"Error updating prices for product {product.sku}: {str(e)}")
                    skipped_count += 1
            
            # Commit changes
            db.session.commit()
            
            logger.info(f"Price sync to products completed: {updated_count} updated, {skipped_count} skipped")
            
            return {
                'success': True,
                'updated_count': updated_count,
                'skipped_count': skipped_count,
                'total_products': len(products)
            }
            
        except Exception as e:
            logger.error(f"Failed to sync prices to products: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}
    
    def _get_price_type_from_key(self, price_list_key: int) -> str:
        """Get price type from price list key"""
        for price_type, config in self.api_service.price_categories.items():
            if config['price_list_key'] == price_list_key:
                return price_type
        return 'unknown'
    
    def _get_best_price(self, prices: List) -> Optional:
        """Get the best price from a list of prices"""
        if not prices:
            return None
        
        # Return the price with highest final_price (most recent and highest value)
        # Sort by last_update first, then by final_price
        best_price = max(prices, key=lambda p: (p.last_update or datetime.min, p.final_price))
        return best_price
