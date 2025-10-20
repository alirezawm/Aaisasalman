"""
سرویس زمان‌بندی پیشرفته تدبیر
Enhanced Tadbir Scheduler Service with Optimized Sync
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio
import concurrent.futures

from tadbir_sync_service import TadbirSyncService
from shop_sync_service import get_shop_sync_service
from optimized_tadbir_sync_service import get_optimized_sync_service
from models import db, TadbirSyncSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTadbirSchedulerService:
    """
    سرویس زمان‌بندی پیشرفته تدبیر
    - همگام‌سازی بهینه با سرعت بالا
    - پشتیبانی از همگام‌سازی بلادرنگ
    - مانیتورینگ پیشرفته عملکرد
    - تنظیمات انعطاف‌پذیر
    """
    
    def __init__(self):
        """Initialize enhanced scheduler service"""
        self.sync_service = TadbirSyncService()
        self.shop_sync_service = get_shop_sync_service()
        self.optimized_sync_service = get_optimized_sync_service()
        
        self._scheduler_thread = None
        self._is_running = False
        self._stop_event = threading.Event()
        self._real_time_sync_enabled = False
        self._real_time_thread = None
        
        # Default settings
        self.default_settings = {
            'sync_interval': 1,  # hours - کاهش به 1 ساعت برای به‌روزرسانی سریع‌تر
            'auto_sync_enabled': True,
            'sync_products': True,
            'sync_inventory': True,
            'sync_prices': True,
            'sync_shop': True,
            'use_optimized_sync': True,  # استفاده از سرویس بهینه
            'real_time_sync': False,  # همگام‌سازی بلادرنگ
            'real_time_interval': 300,  # 5 دقیقه برای همگام‌سازی بلادرنگ
            'batch_size': 1000,
            'max_workers': 4,
            'cache_ttl': 300
        }
        
    def _get_setting(self, key: str, default_value: Any = None) -> Any:
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
    
    def _set_setting(self, key: str, value: Any, description: str = None):
        """Set setting value in database"""
        try:
            setting = TadbirSyncSettings.query.filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = str(value)
                setting.description = description or setting.description
                setting.updated_at = datetime.utcnow()
            else:
                setting = TadbirSyncSettings(
                    setting_key=key,
                    setting_value=str(value),
                    description=description,
                    updated_at=datetime.utcnow()
                )
                db.session.add(setting)
            
            db.session.commit()
            logger.info(f"Setting {key} updated to {value}")
            
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {str(e)}")
            db.session.rollback()
    
    def _sync_job(self):
        """Background sync job with optimized performance"""
        from flask import current_app
        
        try:
            logger.info("Starting enhanced scheduled sync job")
            
            # Get Flask app instance
            from app import app
            
            with app.app_context():
                try:
                    # Check if auto sync is enabled
                    if not self._get_setting('auto_sync_enabled', True):
                        logger.info("Auto sync is disabled, skipping scheduled sync")
                        return
                    
                    # Get sync settings
                    sync_products = self._get_setting('sync_products', True)
                    sync_inventory = self._get_setting('sync_inventory', True)
                    sync_prices = self._get_setting('sync_prices', True)
                    sync_shop = self._get_setting('sync_shop', True)
                    use_optimized = self._get_setting('use_optimized_sync', True)
                    
                    sync_logs = []
                    start_time = time.time()
                    
                    # ========== بخش اول: همگام‌سازی با تدبیر ==========
                    if sync_products:
                        try:
                            products_log = self.sync_service.sync_products(incremental=True)
                            sync_logs.append(products_log)
                            logger.info(f"Tadbir products sync completed: {products_log.status}")
                        except Exception as e:
                            logger.error(f"Tadbir products sync failed: {str(e)}")
                            db.session.rollback()
                    
                    if sync_inventory:
                        try:
                            inventory_log = self.sync_service.sync_inventory()
                            sync_logs.append(inventory_log)
                            logger.info(f"Tadbir inventory sync completed: {inventory_log.status}")
                        except Exception as e:
                            logger.error(f"Tadbir inventory sync failed: {str(e)}")
                            db.session.rollback()
                    
                    if sync_prices:
                        try:
                            prices_log = self.sync_service.sync_prices()
                            sync_logs.append(prices_log)
                            logger.info(f"Tadbir prices sync completed: {prices_log.status}")
                        except Exception as e:
                            logger.error(f"Tadbir prices sync failed: {str(e)}")
                            db.session.rollback()
                    
                    # ========== بخش دوم: همگام‌سازی فروشگاه ==========
                    if sync_shop:
                        try:
                            logger.info("Starting enhanced shop sync")
                            
                            if use_optimized:
                                # استفاده از سرویس بهینه
                                logger.info("Using optimized sync service")
                                
                                # همگام‌سازی قیمت‌ها بهینه
                                if sync_prices:
                                    shop_prices_log = self.optimized_sync_service.sync_prices_optimized()
                                    sync_logs.append(shop_prices_log)
                                    logger.info(f"Optimized shop prices sync completed: {shop_prices_log.status}")
                                
                                # همگام‌سازی موجودی بهینه
                                if sync_inventory:
                                    shop_inventory_log = self.optimized_sync_service.sync_inventory_optimized()
                                    sync_logs.append(shop_inventory_log)
                                    logger.info(f"Optimized shop inventory sync completed: {shop_inventory_log.status}")
                                
                                # همگام‌سازی اطلاعات محصولات (از سرویس قدیمی)
                                shop_products_log = self.shop_sync_service.sync_shop_products()
                                sync_logs.append(shop_products_log)
                                logger.info(f"Shop products sync completed: {shop_products_log.status}")
                                
                            else:
                                # استفاده از سرویس قدیمی
                                logger.info("Using standard sync service")
                                
                                shop_products_log = self.shop_sync_service.sync_shop_products()
                                sync_logs.append(shop_products_log)
                                logger.info(f"Shop products sync completed: {shop_products_log.status}")
                                
                                shop_inventory_log = self.shop_sync_service.sync_shop_inventory()
                                sync_logs.append(shop_inventory_log)
                                logger.info(f"Shop inventory sync completed: {shop_inventory_log.status}")
                                
                                shop_prices_log = self.shop_sync_service.sync_shop_prices()
                                sync_logs.append(shop_prices_log)
                                logger.info(f"Shop prices sync completed: {shop_prices_log.status}")
                            
                            logger.info("Enhanced shop sync completed successfully")
                            
                        except Exception as e:
                            logger.error(f"Enhanced shop sync failed: {str(e)}")
                            db.session.rollback()
                    
                    # محاسبه زمان کل
                    total_duration = time.time() - start_time
                    logger.info(f"Enhanced scheduled sync job completed in {total_duration:.2f} seconds")
                    
                finally:
                    # Clean up session only once at the end of app context
                    db.session.remove()
            
        except Exception as e:
            logger.error(f"Enhanced scheduled sync job failed: {str(e)}")
    
    def _real_time_sync_job(self):
        """Real-time sync job for immediate updates"""
        from flask import current_app
        
        try:
            logger.info("Starting real-time sync job")
            
            # Get Flask app instance
            from app import app
            
            with app.app_context():
                try:
                    # فقط همگام‌سازی قیمت‌ها و موجودی‌ها (سریع‌ترین)
                    if self._get_setting('use_optimized_sync', True):
                        # استفاده از سرویس بهینه برای سرعت بالا
                        prices_log = self.optimized_sync_service.sync_prices_optimized()
                        inventory_log = self.optimized_sync_service.sync_inventory_optimized()
                        
                        logger.info(f"Real-time sync completed - Prices: {prices_log.status}, Inventory: {inventory_log.status}")
                    else:
                        # استفاده از سرویس قدیمی
                        prices_log = self.shop_sync_service.sync_shop_prices()
                        inventory_log = self.shop_sync_service.sync_shop_inventory()
                        
                        logger.info(f"Real-time sync completed - Prices: {prices_log.status}, Inventory: {inventory_log.status}")
                    
                finally:
                    db.session.remove()
            
        except Exception as e:
            logger.error(f"Real-time sync job failed: {str(e)}")
    
    def _scheduler_worker(self):
        """Scheduler worker thread"""
        logger.info("Enhanced Tadbir scheduler worker started")
        
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler worker error: {str(e)}")
                time.sleep(60)
        
        logger.info("Enhanced Tadbir scheduler worker stopped")
    
    def _real_time_worker(self):
        """Real-time sync worker thread"""
        logger.info("Real-time sync worker started")
        
        while not self._stop_event.is_set() and self._real_time_sync_enabled:
            try:
                self._real_time_sync_job()
                
                # انتظار برای interval بعدی
                interval_seconds = self._get_setting('real_time_interval', 300)
                for _ in range(interval_seconds):
                    if self._stop_event.is_set() or not self._real_time_sync_enabled:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Real-time worker error: {str(e)}")
                time.sleep(60)
        
        logger.info("Real-time sync worker stopped")
    
    def start_scheduler(self):
        """شروع زمان‌بندی پیشرفته"""
        if self._is_running:
            logger.warning("Enhanced scheduler is already running")
            return
        
        try:
            # Clear existing jobs
            schedule.clear()
            
            # Get sync interval
            interval_hours = self._get_setting('sync_interval', 1)
            
            # Schedule main sync job
            schedule.every(interval_hours).hours.do(self._sync_job)
            
            # Start scheduler thread
            self._stop_event.clear()
            self._scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
            self._scheduler_thread.start()
            
            # Start real-time sync if enabled
            if self._get_setting('real_time_sync', False):
                self.start_real_time_sync()
            
            self._is_running = True
            logger.info(f"Enhanced Tadbir scheduler started with {interval_hours} hour interval")
            
        except Exception as e:
            logger.error(f"Failed to start enhanced scheduler: {str(e)}")
            raise
    
    def stop_scheduler(self):
        """توقف زمان‌بندی پیشرفته"""
        if not self._is_running:
            logger.warning("Enhanced scheduler is not running")
            return
        
        try:
            # Stop real-time sync
            self.stop_real_time_sync()
            
            # Stop scheduler thread
            self._stop_event.set()
            if self._scheduler_thread:
                self._scheduler_thread.join(timeout=10)
            
            # Clear scheduled jobs
            schedule.clear()
            
            self._is_running = False
            logger.info("Enhanced Tadbir scheduler stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop enhanced scheduler: {str(e)}")
            raise
    
    def start_real_time_sync(self):
        """شروع همگام‌سازی بلادرنگ"""
        if self._real_time_sync_enabled:
            logger.warning("Real-time sync is already running")
            return
        
        try:
            self._real_time_sync_enabled = True
            self._real_time_thread = threading.Thread(target=self._real_time_worker, daemon=True)
            self._real_time_thread.start()
            
            logger.info("Real-time sync started")
            
        except Exception as e:
            logger.error(f"Failed to start real-time sync: {str(e)}")
            raise
    
    def stop_real_time_sync(self):
        """توقف همگام‌سازی بلادرنگ"""
        if not self._real_time_sync_enabled:
            logger.warning("Real-time sync is not running")
            return
        
        try:
            self._real_time_sync_enabled = False
            if self._real_time_thread:
                self._real_time_thread.join(timeout=10)
            
            logger.info("Real-time sync stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop real-time sync: {str(e)}")
            raise
    
    def run_optimized_sync_now(self, sync_type: str = 'all') -> Dict[str, Any]:
        """اجرای فوری همگام‌سازی بهینه"""
        try:
            logger.info(f"Running immediate optimized sync: {sync_type}")
            
            results = {}
            
            if sync_type in ['all', 'prices']:
                prices_log = self.optimized_sync_service.sync_prices_optimized()
                results['prices'] = {
                    'status': prices_log.status,
                    'records_successful': prices_log.records_successful,
                    'duration_seconds': prices_log.duration_seconds
                }
            
            if sync_type in ['all', 'inventory']:
                inventory_log = self.optimized_sync_service.sync_inventory_optimized()
                results['inventory'] = {
                    'status': inventory_log.status,
                    'records_successful': inventory_log.records_successful,
                    'duration_seconds': inventory_log.duration_seconds
                }
            
            if sync_type == 'all':
                # همگام‌سازی اطلاعات محصولات
                products_log = self.shop_sync_service.sync_shop_products()
                results['products'] = {
                    'status': products_log.status,
                    'records_successful': products_log.records_successful,
                    'duration_seconds': products_log.duration_seconds
                }
            
            logger.info(f"Optimized sync completed: {results}")
            return results
                
        except Exception as e:
            logger.error(f"Failed to run optimized sync: {str(e)}")
            raise
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """دریافت وضعیت پیشرفته زمان‌بندی"""
        try:
            # Get next scheduled run
            next_run = None
            if schedule.jobs:
                next_run = schedule.next_run()
            
            # Get settings
            settings = {
                'auto_sync_enabled': self._get_setting('auto_sync_enabled', True),
                'sync_interval': self._get_setting('sync_interval', 1),
                'sync_products': self._get_setting('sync_products', True),
                'sync_inventory': self._get_setting('sync_inventory', True),
                'sync_prices': self._get_setting('sync_prices', True),
                'sync_shop': self._get_setting('sync_shop', True),
                'use_optimized_sync': self._get_setting('use_optimized_sync', True),
                'real_time_sync': self._get_setting('real_time_sync', False),
                'real_time_interval': self._get_setting('real_time_interval', 300),
                'batch_size': self._get_setting('batch_size', 1000),
                'max_workers': self._get_setting('max_workers', 4)
            }
            
            # Get performance stats
            performance_stats = self.optimized_sync_service.get_performance_stats()
            
            return {
                'is_running': self._is_running,
                'real_time_enabled': self._real_time_sync_enabled,
                'next_run': next_run.isoformat() if next_run else None,
                'scheduled_jobs': len(schedule.jobs),
                'settings': settings,
                'performance': performance_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get enhanced status: {str(e)}")
            return {'error': str(e)}
    
    def update_enhanced_settings(self, settings: Dict[str, Any]):
        """بروزرسانی تنظیمات پیشرفته"""
        try:
            for key, value in settings.items():
                self._set_setting(key, value)
            
            # Restart scheduler if interval changed
            if 'sync_interval' in settings:
                if self._is_running:
                    self.stop_scheduler()
                    self.start_scheduler()
            
            # Update real-time sync if settings changed
            if 'real_time_sync' in settings or 'real_time_interval' in settings:
                if self._real_time_sync_enabled:
                    self.stop_real_time_sync()
                    if settings.get('real_time_sync', False):
                        self.start_real_time_sync()
                elif settings.get('real_time_sync', False):
                    self.start_real_time_sync()
            
            # Update optimized sync service settings
            if 'batch_size' in settings:
                self.optimized_sync_service.batch_size = settings['batch_size']
            if 'max_workers' in settings:
                self.optimized_sync_service.max_workers = settings['max_workers']
            if 'cache_ttl' in settings:
                self.optimized_sync_service.cache_ttl = settings['cache_ttl']
            
            logger.info("Enhanced scheduler settings updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update enhanced settings: {str(e)}")
            raise
    
    def clear_optimized_cache(self):
        """پاک کردن کش بهینه"""
        try:
            self.optimized_sync_service.clear_cache()
            logger.info("Optimized sync cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear optimized cache: {str(e)}")
            raise


# Global enhanced scheduler instance
_enhanced_scheduler_instance = None


def get_enhanced_scheduler() -> EnhancedTadbirSchedulerService:
    """Get global enhanced scheduler instance"""
    global _enhanced_scheduler_instance
    if _enhanced_scheduler_instance is None:
        _enhanced_scheduler_instance = EnhancedTadbirSchedulerService()
    return _enhanced_scheduler_instance
