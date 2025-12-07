"""
سرویس بهینه‌شده همگام‌سازی تدبیر
Optimized Tadbir Sync Service for Fastest Product Updates
"""

import logging
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import text, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import threading
import time

from models import (
    db, Product, TadbirProductCache, TadbirPriceCache, 
    TadbirInventoryCache, TadbirSyncLog
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizedTadbirSyncService:
    """
    سرویس بهینه‌شده همگام‌سازی تدبیر
    - پردازش موازی برای سرعت بالا
    - به‌روزرسانی دسته‌ای برای کاهش عملیات دیتابیس
    - کش هوشمند برای جلوگیری از درخواست‌های تکراری
    - همگام‌سازی بلادرنگ
    """
    
    def __init__(self):
        """Initialize optimized sync service"""
        self.default_stock_code = '10'
        self.isaco_stock_code = '15'
        self.batch_size = 1000  # اندازه دسته برای پردازش
        self.max_workers = 4  # تعداد thread های موازی
        self.cache = {}  # کش موقت برای جلوگیری از درخواست‌های تکراری
        self.cache_ttl = 300  # 5 دقیقه TTL برای کش
        self._lock = threading.Lock()
        
    def _create_sync_log(self, sync_type: str) -> TadbirSyncLog:
        """ایجاد لاگ همگام‌سازی"""
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
                        records_failed: int = 0, error_message: str = None,
                        performance_metrics: Dict = None):
        """بروزرسانی لاگ همگام‌سازی"""
        sync_log.status = status
        sync_log.records_processed = records_processed
        sync_log.records_successful = records_successful
        sync_log.records_failed = records_failed
        sync_log.error_message = error_message
        
        if status in ['completed', 'failed', 'cancelled']:
            sync_log.completed_at = datetime.utcnow()
            if sync_log.started_at:
                sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
        
        # ذخیره معیارهای عملکرد
        if performance_metrics:
            sync_log.error_message = f"{error_message or ''}\nPerformance: {performance_metrics}"
        
        db.session.commit()
    
    def _get_cached_data(self, key: str) -> Optional[Any]:
        """دریافت داده از کش"""
        with self._lock:
            if key in self.cache:
                data, timestamp = self.cache[key]
                if time.time() - timestamp < self.cache_ttl:
                    return data
                else:
                    del self.cache[key]
            return None
    
    def _set_cached_data(self, key: str, data: Any):
        """ذخیره داده در کش"""
        with self._lock:
            self.cache[key] = (data, time.time())
    
    def _bulk_update_products(self, updates: List[Dict]) -> Tuple[int, int]:
        """
        بروزرسانی دسته‌ای محصولات
        Returns: (successful_count, failed_count)
        """
        if not updates:
            return 0, 0
        
        successful = 0
        failed = 0
        
        try:
            # استفاده از bulk_update_mappings برای سرعت بالا
            db.session.bulk_update_mappings(Product, updates)
            db.session.commit()
            successful = len(updates)
            logger.info(f"Bulk updated {successful} products successfully")
            
        except Exception as e:
            logger.error(f"Bulk update failed: {str(e)}")
            db.session.rollback()
            
            # Fallback: بروزرسانی تک‌تک
            for update_data in updates:
                try:
                    product = Product.query.get(update_data['id'])
                    if product:
                        for key, value in update_data.items():
                            if key != 'id' and hasattr(product, key):
                                setattr(product, key, value)
                        product.updated_at = datetime.utcnow()
                        successful += 1
                except Exception as item_error:
                    logger.error(f"Failed to update product {update_data.get('id')}: {str(item_error)}")
                    failed += 1
            
            try:
                db.session.commit()
            except Exception as commit_error:
                logger.error(f"Failed to commit individual updates: {str(commit_error)}")
                db.session.rollback()
                failed += successful
                successful = 0
        
        return successful, failed
    
    def _get_products_batch(self, offset: int, limit: int) -> List[Product]:
        """دریافت دسته‌ای محصولات"""
        return Product.query.offset(offset).limit(limit).all()
    
    def _get_tadbir_prices_batch(self, skus: List[str]) -> Dict[str, Dict]:
        """دریافت دسته‌ای قیمت‌های تدبیر"""
        cache_key = f"prices_{hash(tuple(sorted(skus)))}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        prices_data = {}
        
        try:
            # دریافت قیمت‌های نقدی (لیست 14)
            cash_prices = db.session.query(TadbirPriceCache).filter(
                and_(
                    TadbirPriceCache.item_code.in_(skus),
                    TadbirPriceCache.price_list_key == 14
                )
            ).all()
            
            # دریافت قیمت‌های چکی (لیست 13)
            check_prices = db.session.query(TadbirPriceCache).filter(
                and_(
                    TadbirPriceCache.item_code.in_(skus),
                    TadbirPriceCache.price_list_key == 13
                )
            ).all()
            
            # دریافت قیمت‌های ISACO
            isaco_prices = db.session.query(TadbirPriceCache).filter(
                and_(
                    TadbirPriceCache.item_code.in_(skus),
                    TadbirPriceCache.price_list_key.in_([60, 61, 62, 63])
                )
            ).all()
            
            # سازماندهی داده‌ها
            for sku in skus:
                prices_data[sku] = {
                    'cash': None,
                    'check': None,
                    'isaco': {}
                }
            
            # قیمت‌های نقدی
            for price in cash_prices:
                if price.item_code in prices_data:
                    prices_data[price.item_code]['cash'] = price
            
            # قیمت‌های چکی
            for price in check_prices:
                if price.item_code in prices_data:
                    prices_data[price.item_code]['check'] = price
            
            # قیمت‌های ISACO
            for price in isaco_prices:
                if price.item_code in prices_data:
                    if price.price_list_key == 60:
                        prices_data[price.item_code]['isaco']['3m'] = price
                    elif price.price_list_key == 61:
                        prices_data[price.item_code]['isaco']['cash'] = price
                    elif price.price_list_key == 62:
                        prices_data[price.item_code]['isaco']['1m'] = price
                    elif price.price_list_key == 63:
                        prices_data[price.item_code]['isaco']['2m'] = price
            
            # ذخیره در کش
            self._set_cached_data(cache_key, prices_data)
            
        except Exception as e:
            logger.error(f"Failed to get Tadbir prices batch: {str(e)}")
        
        return prices_data
    
    def _get_tadbir_inventory_batch(self, skus: List[str]) -> Dict[str, Dict]:
        """دریافت دسته‌ای موجودی‌های تدبیر"""
        cache_key = f"inventory_{hash(tuple(sorted(skus)))}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        inventory_data = {}
        
        try:
            # موجودی عمومی
            general_inventory = db.session.query(TadbirInventoryCache).filter(
                and_(
                    TadbirInventoryCache.item_code.in_(skus),
                    TadbirInventoryCache.stock_code == self.default_stock_code
                )
            ).all()
            
            # موجودی ISACO
            isaco_inventory = db.session.query(TadbirInventoryCache).filter(
                and_(
                    TadbirInventoryCache.item_code.in_(skus),
                    TadbirInventoryCache.stock_code == self.isaco_stock_code
                )
            ).all()
            
            # سازماندهی داده‌ها
            for sku in skus:
                inventory_data[sku] = {
                    'general': None,
                    'isaco': None
                }
            
            # موجودی عمومی
            for inv in general_inventory:
                if inv.item_code in inventory_data:
                    inventory_data[inv.item_code]['general'] = inv
            
            # موجودی ISACO
            for inv in isaco_inventory:
                if inv.item_code in inventory_data:
                    inventory_data[inv.item_code]['isaco'] = inv
            
            # ذخیره در کش
            self._set_cached_data(cache_key, inventory_data)
            
        except Exception as e:
            logger.error(f"Failed to get Tadbir inventory batch: {str(e)}")
        
        return inventory_data
    
    def _process_price_updates(self, products: List[Product]) -> List[Dict]:
        """پردازش بروزرسانی قیمت‌ها"""
        skus = [p.sku for p in products]
        prices_data = self._get_tadbir_prices_batch(skus)
        
        updates = []
        
        for product in products:
            try:
                sku = product.sku
                if sku not in prices_data:
                    continue
                
                price_info = prices_data[sku]
                updated = False
                update_data = {'id': product.id}
                
                # قیمت نقدی عمده (لیست 14)
                if price_info['cash'] and price_info['cash'].final_price:
                    new_price = float(price_info['cash'].final_price)
                    if product.bulk_price_cash != new_price:
                        update_data['bulk_price_cash'] = new_price
                        updated = True
                
                # قیمت چکی (لیست 13)
                if price_info['check'] and price_info['check'].final_price:
                    new_price = float(price_info['check'].final_price)
                    if (product.retail_price_check != new_price or 
                        product.retail_price_cash != new_price or 
                        product.bulk_price_check != new_price):
                        update_data['retail_price_check'] = new_price
                        update_data['retail_price_cash'] = new_price  # برای سازگاری
                        update_data['bulk_price_check'] = new_price
                        updated = True
                    
                    # اگر قیمت نقدی عمده نداریم، از چکی استفاده می‌کنیم
                    if not price_info['cash'] and product.bulk_price_cash != new_price:
                        update_data['bulk_price_cash'] = new_price
                        updated = True
                
                # قیمت‌های ISACO
                isaco_updated = False
                isaco_prices = price_info['isaco']
                
                if isaco_prices.get('cash') and isaco_prices['cash'].final_price is not None:
                    new_price = float(isaco_prices['cash'].final_price)
                    if product.isaco_cash != new_price:
                        update_data['isaco_cash'] = new_price
                        isaco_updated = True
                
                if isaco_prices.get('1m') and isaco_prices['1m'].final_price is not None:
                    new_price = float(isaco_prices['1m'].final_price)
                    if product.isaco_1m != new_price:
                        update_data['isaco_1m'] = new_price
                        isaco_updated = True
                
                if isaco_prices.get('2m') and isaco_prices['2m'].final_price is not None:
                    new_price = float(isaco_prices['2m'].final_price)
                    if product.isaco_2m != new_price:
                        update_data['isaco_2m'] = new_price
                        isaco_updated = True
                
                if isaco_prices.get('3m') and isaco_prices['3m'].final_price is not None:
                    new_price = float(isaco_prices['3m'].final_price)
                    if product.isaco_3m != new_price:
                        update_data['isaco_3m'] = new_price
                        isaco_updated = True
                
                # علامت‌گذاری محصولات ISACO
                if isaco_updated and not product.is_isaco_wh15:
                    update_data['is_isaco_wh15'] = True
                    isaco_updated = True
                
                if updated or isaco_updated:
                    update_data['updated_at'] = datetime.utcnow()
                    updates.append(update_data)
                
            except Exception as e:
                logger.error(f"Error processing price update for product {product.sku}: {str(e)}")
                continue
        
        return updates
    
    def _process_inventory_updates(self, products: List[Product]) -> List[Dict]:
        """پردازش بروزرسانی موجودی‌ها"""
        skus = [p.sku for p in products]
        inventory_data = self._get_tadbir_inventory_batch(skus)
        
        updates = []
        
        for product in products:
            try:
                sku = product.sku
                if sku not in inventory_data:
                    continue
                
                inv_info = inventory_data[sku]
                updated = False
                update_data = {'id': product.id}
                
                # موجودی عمومی
                if inv_info['general'] and inv_info['general'].available_quantity is not None:
                    new_quantity = int(inv_info['general'].available_quantity)
                    if product.stock_quantity != new_quantity:
                        update_data['stock_quantity'] = new_quantity
                        updated = True
                
                # علامت‌گذاری محصولات ISACO
                if inv_info['isaco'] and not product.is_isaco_wh15:
                    update_data['is_isaco_wh15'] = True
                    updated = True
                
                if updated:
                    update_data['updated_at'] = datetime.utcnow()
                    updates.append(update_data)
                
            except Exception as e:
                logger.error(f"Error processing inventory update for product {product.sku}: {str(e)}")
                continue
        
        return updates
    
    def _process_batch(self, products: List[Product], update_type: str) -> Tuple[int, int]:
        """پردازش یک دسته محصول"""
        if update_type == 'prices':
            updates = self._process_price_updates(products)
        elif update_type == 'inventory':
            updates = self._process_inventory_updates(products)
        else:
            return 0, 0
        
        if updates:
            return self._bulk_update_products(updates)
        return 0, 0
    
    def sync_prices_optimized(self) -> TadbirSyncLog:
        """همگام‌سازی بهینه قیمت‌ها"""
        sync_log = self._create_sync_log('optimized_prices')
        start_time = time.time()
        
        try:
            logger.info("Starting optimized price sync")
            
            # دریافت تعداد کل محصولات
            total_products = Product.query.count()
            logger.info(f"Total products to process: {total_products}")
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            # پردازش موازی
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                # تقسیم محصولات به دسته‌ها
                for offset in range(0, total_products, self.batch_size):
                    products = self._get_products_batch(offset, self.batch_size)
                    if products:
                        future = executor.submit(self._process_batch, products, 'prices')
                        futures.append(future)
                
                # جمع‌آوری نتایج
                for future in concurrent.futures.as_completed(futures):
                    try:
                        successful, failed = future.result()
                        records_successful += successful
                        records_failed += failed
                        records_processed += self.batch_size
                    except Exception as e:
                        logger.error(f"Batch processing failed: {str(e)}")
                        records_failed += self.batch_size
                        records_processed += self.batch_size
            
            # محاسبه معیارهای عملکرد
            duration = time.time() - start_time
            performance_metrics = {
                'duration_seconds': duration,
                'products_per_second': records_processed / duration if duration > 0 else 0,
                'success_rate': (records_successful / records_processed * 100) if records_processed > 0 else 0
            }
            
            self._update_sync_log(
                sync_log, 'completed',
                records_processed, records_successful, records_failed,
                performance_metrics=performance_metrics
            )
            
            logger.info(f"Optimized price sync completed: {records_successful}/{records_processed} successful in {duration:.2f}s")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Optimized price sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def sync_inventory_optimized(self) -> TadbirSyncLog:
        """همگام‌سازی بهینه موجودی‌ها"""
        sync_log = self._create_sync_log('optimized_inventory')
        start_time = time.time()
        
        try:
            logger.info("Starting optimized inventory sync")
            
            # دریافت تعداد کل محصولات
            total_products = Product.query.count()
            logger.info(f"Total products to process: {total_products}")
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            
            # پردازش موازی
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                # تقسیم محصولات به دسته‌ها
                for offset in range(0, total_products, self.batch_size):
                    products = self._get_products_batch(offset, self.batch_size)
                    if products:
                        future = executor.submit(self._process_batch, products, 'inventory')
                        futures.append(future)
                
                # جمع‌آوری نتایج
                for future in concurrent.futures.as_completed(futures):
                    try:
                        successful, failed = future.result()
                        records_successful += successful
                        records_failed += failed
                        records_processed += self.batch_size
                    except Exception as e:
                        logger.error(f"Batch processing failed: {str(e)}")
                        records_failed += self.batch_size
                        records_processed += self.batch_size
            
            # محاسبه معیارهای عملکرد
            duration = time.time() - start_time
            performance_metrics = {
                'duration_seconds': duration,
                'products_per_second': records_processed / duration if duration > 0 else 0,
                'success_rate': (records_successful / records_processed * 100) if records_processed > 0 else 0
            }
            
            self._update_sync_log(
                sync_log, 'completed',
                records_processed, records_successful, records_failed,
                performance_metrics=performance_metrics
            )
            
            logger.info(f"Optimized inventory sync completed: {records_successful}/{records_processed} successful in {duration:.2f}s")
            return sync_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Optimized inventory sync failed: {str(e)}")
            self._update_sync_log(sync_log, 'failed', error_message=str(e))
            return sync_log
    
    def sync_all_optimized(self) -> Dict[str, TadbirSyncLog]:
        """همگام‌سازی کامل بهینه"""
        logger.info("Starting optimized full sync")
        
        sync_logs = {}
        
        try:
            # همگام‌سازی قیمت‌ها
            prices_log = self.sync_prices_optimized()
            sync_logs['prices'] = prices_log
            
            # همگام‌سازی موجودی‌ها
            inventory_log = self.sync_inventory_optimized()
            sync_logs['inventory'] = inventory_log
            
            logger.info("Optimized full sync completed successfully")
            return sync_logs
            
        except Exception as e:
            logger.error(f"Optimized full sync failed: {str(e)}")
            return sync_logs
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """دریافت آمار عملکرد"""
        try:
            # آمار آخرین همگام‌سازی‌ها
            last_prices_sync = TadbirSyncLog.query.filter_by(
                sync_type='optimized_prices'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            last_inventory_sync = TadbirSyncLog.query.filter_by(
                sync_type='optimized_inventory'
            ).order_by(TadbirSyncLog.started_at.desc()).first()
            
            # آمار کلی
            total_products = Product.query.count()
            active_products = Product.query.filter_by(is_active=True).count()
            
            # آمار کش
            cache_size = len(self.cache)
            cache_hit_rate = 0  # TODO: پیاده‌سازی محاسبه cache hit rate
            
            return {
                'last_prices_sync': {
                    'status': last_prices_sync.status if last_prices_sync else None,
                    'duration_seconds': last_prices_sync.duration_seconds if last_prices_sync else None,
                    'records_successful': last_prices_sync.records_successful if last_prices_sync else 0,
                    'started_at': last_prices_sync.started_at.isoformat() if last_prices_sync else None
                },
                'last_inventory_sync': {
                    'status': last_inventory_sync.status if last_inventory_sync else None,
                    'duration_seconds': last_inventory_sync.duration_seconds if last_inventory_sync else None,
                    'records_successful': last_inventory_sync.records_successful if last_inventory_sync else 0,
                    'started_at': last_inventory_sync.started_at.isoformat() if last_inventory_sync else None
                },
                'shop_stats': {
                    'total_products': total_products,
                    'active_products': active_products
                },
                'performance': {
                    'cache_size': cache_size,
                    'cache_hit_rate': cache_hit_rate,
                    'batch_size': self.batch_size,
                    'max_workers': self.max_workers
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {str(e)}")
            return {'error': str(e)}
    
    def clear_cache(self):
        """پاک کردن کش"""
        with self._lock:
            self.cache.clear()
        logger.info("Cache cleared")


# Global service instance
_optimized_sync_instance = None


def get_optimized_sync_service() -> OptimizedTadbirSyncService:
    """Get global optimized sync service instance"""
    global _optimized_sync_instance
    if _optimized_sync_instance is None:
        _optimized_sync_instance = OptimizedTadbirSyncService()
    return _optimized_sync_instance
