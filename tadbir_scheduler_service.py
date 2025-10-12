"""
سرویس زمان‌بندی همگام‌سازی تدبیر
Tadbir Accounting System Scheduler Service
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from tadbir_sync_service import TadbirSyncService
from shop_sync_service import get_shop_sync_service
from models import db, TadbirSyncSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TadbirSchedulerService:
    """سرویس زمان‌بندی همگام‌سازی تدبیر"""
    
    def __init__(self):
        """Initialize Tadbir scheduler service"""
        self.sync_service = TadbirSyncService()
        self.shop_sync_service = get_shop_sync_service()
        self._scheduler_thread = None
        self._is_running = False
        self._stop_event = threading.Event()
        
        # Default settings
        self.default_settings = {
            'sync_interval': 3,  # hours
            'auto_sync_enabled': True,
            'sync_products': True,
            'sync_inventory': True,
            'sync_prices': True,
            'sync_shop': True  # همگام‌سازی فروشگاه
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
        """Background sync job"""
        from flask import current_app
        
        try:
            logger.info("Starting scheduled sync job")
            
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
                    
                    sync_logs = []
                    
                    # ========== بخش اول: همگام‌سازی با تدبیر ==========
                    # Sync products from Tadbir
                    if sync_products:
                        try:
                            products_log = self.sync_service.sync_products(incremental=True)
                            sync_logs.append(products_log)
                            logger.info(f"Tadbir products sync completed: {products_log.status}")
                        except Exception as e:
                            logger.error(f"Tadbir products sync failed: {str(e)}")
                            db.session.rollback()
                    
                    # Sync inventory from Tadbir
                    if sync_inventory:
                        try:
                            inventory_log = self.sync_service.sync_inventory()
                            sync_logs.append(inventory_log)
                            logger.info(f"Tadbir inventory sync completed: {inventory_log.status}")
                        except Exception as e:
                            logger.error(f"Tadbir inventory sync failed: {str(e)}")
                            db.session.rollback()
                    
                    # Sync prices from Tadbir
                    if sync_prices:
                        try:
                            prices_log = self.sync_service.sync_prices()
                            sync_logs.append(prices_log)
                            logger.info(f"Tadbir prices sync completed: {prices_log.status}")
                        except Exception as e:
                            logger.error(f"Tadbir prices sync failed: {str(e)}")
                            db.session.rollback()
                    
                    # ========== بخش دوم: همگام‌سازی فروشگاه با cache تدبیر ==========
                    if sync_shop:
                        try:
                            logger.info("Starting shop sync from Tadbir cache")
                            
                            # Sync shop products info
                            shop_products_log = self.shop_sync_service.sync_shop_products()
                            sync_logs.append(shop_products_log)
                            logger.info(f"Shop products sync completed: {shop_products_log.status}")
                            
                            # Sync shop inventory
                            shop_inventory_log = self.shop_sync_service.sync_shop_inventory()
                            sync_logs.append(shop_inventory_log)
                            logger.info(f"Shop inventory sync completed: {shop_inventory_log.status}")
                            
                            # Sync shop prices
                            shop_prices_log = self.shop_sync_service.sync_shop_prices()
                            sync_logs.append(shop_prices_log)
                            logger.info(f"Shop prices sync completed: {shop_prices_log.status}")
                            
                            logger.info("Shop sync from Tadbir cache completed successfully")
                            
                        except Exception as e:
                            logger.error(f"Shop sync failed: {str(e)}")
                            db.session.rollback()
                    
                    logger.info("Scheduled sync job completed (Tadbir + Shop)")
                    
                finally:
                    # Clean up session only once at the end of app context
                    db.session.remove()
            
        except Exception as e:
            logger.error(f"Scheduled sync job failed: {str(e)}")
    
    def _scheduler_worker(self):
        """Scheduler worker thread"""
        logger.info("Tadbir scheduler worker started")
        
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler worker error: {str(e)}")
                time.sleep(60)
        
        logger.info("Tadbir scheduler worker stopped")
    
    def start_scheduler(self):
        """شروع زمان‌بندی"""
        if self._is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Clear existing jobs
            schedule.clear()
            
            # Get sync interval
            interval_hours = self._get_setting('sync_interval', 3)
            
            # Schedule sync job
            schedule.every(interval_hours).hours.do(self._sync_job)
            
            # Start scheduler thread
            self._stop_event.clear()
            self._scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
            self._scheduler_thread.start()
            
            self._is_running = True
            logger.info(f"Tadbir scheduler started with {interval_hours} hour interval")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def stop_scheduler(self):
        """توقف زمان‌بندی"""
        if not self._is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            # Stop scheduler thread
            self._stop_event.set()
            if self._scheduler_thread:
                self._scheduler_thread.join(timeout=10)
            
            # Clear scheduled jobs
            schedule.clear()
            
            self._is_running = False
            logger.info("Tadbir scheduler stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
            raise
    
    def schedule_sync(self, sync_type: str, interval_hours: int):
        """زمان‌بندی همگام‌سازی"""
        try:
            # Clear existing jobs
            schedule.clear()
            
            if sync_type == 'products':
                schedule.every(interval_hours).hours.do(self.sync_service.sync_products)
            elif sync_type == 'inventory':
                schedule.every(interval_hours).hours.do(self.sync_service.sync_inventory)
            elif sync_type == 'prices':
                schedule.every(interval_hours).hours.do(self.sync_service.sync_prices)
            elif sync_type == 'full':
                schedule.every(interval_hours).hours.do(self.sync_service.full_sync)
            else:
                raise ValueError(f"Invalid sync type: {sync_type}")
            
            # Update setting
            self._set_setting('sync_interval', interval_hours, f'Interval for {sync_type} sync')
            
            logger.info(f"Scheduled {sync_type} sync every {interval_hours} hours")
            
        except Exception as e:
            logger.error(f"Failed to schedule sync: {str(e)}")
            raise
    
    def run_sync_now(self, sync_type: str = 'full'):
        """اجرای فوری همگام‌سازی تدبیر"""
        try:
            logger.info(f"Running immediate Tadbir sync: {sync_type}")
            
            if sync_type == 'products':
                return self.sync_service.sync_products(incremental=True)
            elif sync_type == 'inventory':
                return self.sync_service.sync_inventory()
            elif sync_type == 'prices':
                return self.sync_service.sync_prices()
            elif sync_type == 'full':
                return self.sync_service.full_sync()
            else:
                raise ValueError(f"Invalid sync type: {sync_type}")
                
        except Exception as e:
            logger.error(f"Failed to run immediate sync: {str(e)}")
            raise
    
    def run_shop_sync_now(self, sync_type: str = 'full'):
        """اجرای فوری همگام‌سازی فروشگاه"""
        try:
            logger.info(f"Running immediate shop sync: {sync_type}")
            
            if sync_type == 'products':
                return self.shop_sync_service.sync_shop_products()
            elif sync_type == 'inventory':
                return self.shop_sync_service.sync_shop_inventory()
            elif sync_type == 'prices':
                return self.shop_sync_service.sync_shop_prices()
            elif sync_type == 'full':
                return self.shop_sync_service.full_shop_sync()
            else:
                raise ValueError(f"Invalid sync type: {sync_type}")
                
        except Exception as e:
            logger.error(f"Failed to run immediate shop sync: {str(e)}")
            raise
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """دریافت وضعیت زمان‌بندی"""
        try:
            # Get next scheduled run
            next_run = None
            if schedule.jobs:
                next_run = schedule.next_run()
            
            # Get settings
            settings = {
                'auto_sync_enabled': self._get_setting('auto_sync_enabled', True),
                'sync_interval': self._get_setting('sync_interval', 3),
                'sync_products': self._get_setting('sync_products', True),
                'sync_inventory': self._get_setting('sync_inventory', True),
                'sync_prices': self._get_setting('sync_prices', True),
                'sync_shop': self._get_setting('sync_shop', True)
            }
            
            return {
                'is_running': self._is_running,
                'next_run': next_run.isoformat() if next_run else None,
                'scheduled_jobs': len(schedule.jobs),
                'settings': settings,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler status: {str(e)}")
            return {'error': str(e)}
    
    def update_settings(self, settings: Dict[str, Any]):
        """بروزرسانی تنظیمات"""
        try:
            for key, value in settings.items():
                self._set_setting(key, value)
            
            # Restart scheduler if interval changed
            if 'sync_interval' in settings:
                if self._is_running:
                    self.stop_scheduler()
                    self.start_scheduler()
            
            logger.info("Scheduler settings updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update scheduler settings: {str(e)}")
            raise
    
    def get_sync_history(self, limit: int = 10) -> list:
        """دریافت تاریخچه همگام‌سازی"""
        try:
            from models import TadbirSyncLog
            
            history = TadbirSyncLog.query.order_by(
                TadbirSyncLog.started_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': log.id,
                    'sync_type': log.sync_type,
                    'status': log.status,
                    'started_at': log.started_at.isoformat(),
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                    'duration_seconds': log.duration_seconds,
                    'records_processed': log.records_processed,
                    'records_successful': log.records_successful,
                    'records_failed': log.records_failed,
                    'error_message': log.error_message
                }
                for log in history
            ]
            
        except Exception as e:
            logger.error(f"Failed to get sync history: {str(e)}")
            return []

# Global scheduler instance
_scheduler_instance = None

def get_scheduler() -> TadbirSchedulerService:
    """Get global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TadbirSchedulerService()
    return _scheduler_instance
