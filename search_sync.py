"""
Search Sync Service
Syncs products from SQLite database to Meilisearch
"""
import logging
from typing import List, Optional, Dict, Any
from flask import current_app
from search_service import get_search_service
import models

logger = logging.getLogger(__name__)

class SearchSyncService:
    """Service for syncing products to Meilisearch"""
    
    def __init__(self):
        """Initialize sync service"""
        self.search_service = get_search_service()
    
    def sync_all_products(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Sync all active products to Meilisearch
        
        Args:
            batch_size: Number of products to index in each batch
        
        Returns:
            Dictionary with sync results
        """
        if not self.search_service.is_available():
            return {
                'success': False,
                'message': 'Meilisearch is not available',
                'synced': 0,
                'total': 0
            }
        
        try:
            # Get all active products
            products = models.Product.query.filter_by(is_active=True).all()
            total = len(products)
            
            logger.info(f"Starting sync of {total} products to Meilisearch")
            
            # Sync in batches
            synced = 0
            for i in range(0, total, batch_size):
                batch = products[i:i + batch_size]
                if self.search_service.bulk_index(batch):
                    synced += len(batch)
                    logger.info(f"Synced batch {i // batch_size + 1}: {len(batch)} products")
                else:
                    logger.error(f"Failed to sync batch {i // batch_size + 1}")
            
            return {
                'success': True,
                'message': f'Successfully synced {synced} products',
                'synced': synced,
                'total': total
            }
            
        except Exception as e:
            logger.error(f"Sync all products failed: {e}")
            return {
                'success': False,
                'message': f'Sync failed: {str(e)}',
                'synced': 0,
                'total': 0
            }
    
    def sync_product(self, product_id: int) -> bool:
        """
        Sync a single product to Meilisearch
        
        Args:
            product_id: Product ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            product = models.Product.query.get(product_id)
            if not product:
                logger.warning(f"Product {product_id} not found")
                return False
            
            # If product is not active, delete from index
            if not product.is_active:
                return self.search_service.delete_product(product_id)
            
            # Index product
            return self.search_service.index_product(product)
            
        except Exception as e:
            logger.error(f"Sync product {product_id} failed: {e}")
            return False
    
    def sync_products_batch(self, product_ids: List[int]) -> Dict[str, Any]:
        """
        Sync multiple products to Meilisearch
        
        Args:
            product_ids: List of product IDs
        
        Returns:
            Dictionary with sync results
        """
        try:
            products = models.Product.query.filter(
                models.Product.id.in_(product_ids),
                models.Product.is_active == True
            ).all()
            
            if not products:
                return {
                    'success': False,
                    'message': 'No active products found',
                    'synced': 0
                }
            
            success = self.search_service.bulk_index(products)
            
            return {
                'success': success,
                'message': f'Synced {len(products)} products' if success else 'Sync failed',
                'synced': len(products) if success else 0
            }
            
        except Exception as e:
            logger.error(f"Sync products batch failed: {e}")
            return {
                'success': False,
                'message': f'Sync failed: {str(e)}',
                'synced': 0
            }
    
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product from Meilisearch index
        
        Args:
            product_id: Product ID
        
        Returns:
            True if successful, False otherwise
        """
        return self.search_service.delete_product(product_id)
    
    def reindex(self) -> Dict[str, Any]:
        """
        Full reindex - delete all and re-sync
        
        Returns:
            Dictionary with reindex results
        """
        if not self.search_service.is_available():
            return {
                'success': False,
                'message': 'Meilisearch is not available'
            }
        
        try:
            # Note: Meilisearch doesn't have a direct "delete all" API
            # We'll sync all products which will update/create them
            # For a true reindex, you might want to delete the index and recreate it
            logger.info("Starting full reindex")
            return self.sync_all_products()
            
        except Exception as e:
            logger.error(f"Reindex failed: {e}")
            return {
                'success': False,
                'message': f'Reindex failed: {str(e)}'
            }

# Singleton instance
_sync_service = None

def get_sync_service() -> SearchSyncService:
    """Get singleton SearchSyncService instance"""
    global _sync_service
    if _sync_service is None:
        _sync_service = SearchSyncService()
    return _sync_service

