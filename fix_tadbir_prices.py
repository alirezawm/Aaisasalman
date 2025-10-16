"""
Fix Tadbir Prices - Clear cache and re-sync with correct conversion
Clear old prices and re-sync from Tadbir with proper unit conversion (Rials to Thousands)
"""

import sys
import io

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
from models import db, TadbirPriceCache
from tadbir_sync_service import TadbirSyncService
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def fix_tadbir_prices():
    """Clear old prices and re-sync from Tadbir"""
    with app.app_context():
        try:
            # Show current price count
            current_count = TadbirPriceCache.query.count()
            logger.info(f"Current prices in cache: {current_count}")
            
            # Delete all cached prices
            logger.info("Clearing old prices...")
            TadbirPriceCache.query.delete()
            db.session.commit()
            logger.info("Old prices cleared successfully")
            
            # Re-sync prices from Tadbir
            logger.info("Syncing prices from Tadbir with correct conversion...")
            sync_service = TadbirSyncService()
            sync_log = sync_service.sync_prices()
            
            if sync_log.status == 'completed':
                logger.info(f"SUCCESS: {sync_log.records_successful} prices synced")
                
                # Sync prices to products
                logger.info("Syncing prices to products...")
                result = sync_service.sync_prices_to_products()
                
                if result.get('success'):
                    logger.info(f"SUCCESS: {result['updated_count']} products updated")
                    logger.info(f"  Skipped (no price): {result['skipped_count']}")
                else:
                    logger.error(f"ERROR syncing to products: {result.get('error')}")
            else:
                logger.error(f"ERROR: {sync_log.error_message}")
            
            logger.info("=" * 60)
            logger.info("Operation completed")
            logger.info("Prices are now stored in Thousands of Rials")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"ERROR: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Tadbir Prices Script")
    print("Clear old prices and re-sync with correct conversion")
    print("=" * 60)
    print()
    response = input("Are you sure you want to clear all prices and re-sync? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\nStarting operation...")
        fix_tadbir_prices()
    else:
        print("Operation cancelled.")

