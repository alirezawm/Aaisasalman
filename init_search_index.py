"""
Script for initializing Meilisearch index and syncing all products
Run this script once to set up the search index
"""
from app import app
from search_sync import get_sync_service
from search_service import get_search_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_search_index():
    """Initialize Meilisearch index and sync all products"""
    with app.app_context():
        try:
            # Get services
            search_service = get_search_service()
            sync_service = get_sync_service()
            
            # Check if Meilisearch client is initialized
            if not search_service.client:
                logger.error("Meilisearch client is not initialized. Please check installation.")
                logger.info("Install with: pip install meilisearch")
                return False
            
            # Check if Meilisearch server is available
            try:
                search_service.client.health()
                logger.info("✓ Meilisearch server is available")
            except Exception as e:
                logger.error(f"✗ Meilisearch server is not available: {e}")
                logger.info("Start Meilisearch with: docker-compose -f docker-compose.meilisearch.yml up -d")
                return False
            
            logger.info("Starting index initialization...")
            
            # Ensure index exists and is configured
            try:
                search_service._ensure_index_exists()
                logger.info("✓ Index created/configured successfully")
            except Exception as e:
                logger.error(f"✗ Failed to create/configure index: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
            
            # Sync all products
            logger.info("Starting sync of all products...")
            result = sync_service.sync_all_products(batch_size=100)
            
            if result['success']:
                logger.info(f"✓ Successfully synced {result['synced']} products out of {result['total']}")
                logger.info("Search index is ready to use!")
                return True
            else:
                logger.error(f"✗ Sync failed: {result['message']}")
                return False
                
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Meilisearch Index Initialization")
    print("=" * 60)
    print()
    
    success = init_search_index()
    
    if success:
        print()
        print("=" * 60)
        print("✓ Initialization completed successfully!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("✗ Initialization failed. Please check the errors above.")
        print("=" * 60)
        exit(1)

