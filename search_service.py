"""
Search Service for Meilisearch integration
Provides search functionality with fallback to SQL search
"""
import logging
from typing import List, Dict, Optional, Any
from flask import current_app
from search_config import SearchConfig

logger = logging.getLogger(__name__)

class SearchService:
    """Service class for interacting with Meilisearch"""
    
    def __init__(self):
        """Initialize search service"""
        self.client = None
        self.index = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Meilisearch client"""
        try:
            from meilisearch import Client
            
            config = SearchConfig.get_config()
            self.client = Client(
                url=config['host'],
                api_key=config['master_key'],
                timeout=config['timeout']
            )
            
            # Get or create index
            try:
                self.index = self.client.get_index(SearchConfig.INDEX_NAME)
            except Exception:
                # Index doesn't exist, will be created on first sync
                logger.warning(f"Index {SearchConfig.INDEX_NAME} does not exist. It will be created on first sync.")
                self.index = None
            
            logger.info("Meilisearch client initialized successfully")
            
        except ImportError:
            logger.warning("meilisearch package not installed. Search will fallback to SQL.")
            self.client = None
            self.index = None
        except Exception as e:
            logger.error(f"Failed to initialize Meilisearch client: {e}")
            self.client = None
            self.index = None
    
    def is_available(self) -> bool:
        """Check if Meilisearch is available"""
        if not self.client:
            return False
        
        try:
            # Try to connect to Meilisearch (check health)
            self.client.health()
            
            # Try to get or create index
            if not self.index:
                try:
                    self.index = self.client.get_index(SearchConfig.INDEX_NAME)
                except Exception:
                    # Index doesn't exist, but Meilisearch is available
                    # We can create it later
                    pass
            
            return True
        except Exception as e:
            logger.debug(f"Meilisearch availability check failed: {e}")
            return False
    
    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        sort: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 12,
        highlight: bool = True
    ) -> Dict[str, Any]:
        """
        Search products with Meilisearch
        
        Args:
            query: Search query string
            filters: Dictionary of filters (e.g., {'brand_id': 1, 'stock_quantity': '> 0'})
            sort: List of sort criteria (e.g., ['created_at:desc'])
            page: Page number (1-indexed)
            per_page: Number of results per page
            highlight: Whether to highlight matches
        
        Returns:
            Dictionary with 'products' (list of product IDs), 'total', 'page', 'per_page'
        """
        if not self.is_available():
            logger.warning("Meilisearch not available, returning empty results")
            return {
                'products': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'from_search_engine': False
            }
        
        try:
            # Build filter string
            filter_string = self._build_filter_string(filters)
            
            # Prepare search parameters
            search_params = {
                'q': query,
                'limit': per_page,
                'offset': (page - 1) * per_page,
                'attributesToRetrieve': SearchConfig.DEFAULT_ATTRIBUTES_TO_RETRIEVE,
            }
            
            if filter_string:
                search_params['filter'] = filter_string
            
            if sort:
                search_params['sort'] = sort
            
            if highlight:
                search_params['attributesToHighlight'] = SearchConfig.ATTRIBUTES_TO_HIGHLIGHT
            
            # Perform search
            results = self.index.search(query, search_params)
            
            # Extract product IDs from results
            product_ids = [hit['id'] for hit in results['hits']]
            
            return {
                'products': product_ids,
                'total': results['estimatedTotalHits'],
                'page': page,
                'per_page': per_page,
                'hits': results['hits'],
                'from_search_engine': True
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'products': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'from_search_engine': False,
                'error': str(e)
            }
    
    def search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions for auto-complete
        
        Args:
            query: Search query string
            limit: Maximum number of suggestions
        
        Returns:
            List of suggestion strings
        """
        if not self.is_available():
            return []
        
        try:
            # Use search with limit to get suggestions
            results = self.index.search(
                query,
                {
                    'limit': limit,
                    'attributesToRetrieve': ['name_fa', 'name', 'sku']
                }
            )
            
            suggestions = []
            seen = set()
            
            for hit in results['hits']:
                # Add name_fa to suggestions
                if 'name_fa' in hit and hit['name_fa'] and hit['name_fa'] not in seen:
                    suggestions.append(hit['name_fa'])
                    seen.add(hit['name_fa'])
                
                # Add name to suggestions
                if 'name' in hit and hit['name'] and hit['name'] not in seen:
                    suggestions.append(hit['name'])
                    seen.add(hit['name'])
                
                # Add SKU if it contains the query
                if 'sku' in hit and query.lower() in hit['sku'].lower() and hit['sku'] not in seen:
                    suggestions.append(hit['sku'])
                    seen.add(hit['sku'])
                
                if len(suggestions) >= limit:
                    break
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Search suggestions failed: {e}")
            return []
    
    def index_product(self, product: 'Product') -> bool:
        """
        Index a single product
        
        Args:
            product: Product model instance
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Ensure index exists
            if not self.index:
                self._ensure_index_exists()
            
            # Convert product to document
            document = self._product_to_document(product)
            
            # Index document
            self.index.add_documents([document], primary_key=SearchConfig.PRIMARY_KEY)
            
            logger.debug(f"Indexed product {product.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index product {product.id}: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product from index
        
        Args:
            product_id: Product ID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.index.delete_document(product_id)
            logger.debug(f"Deleted product {product_id} from index")
            return True
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            return False
    
    def bulk_index(self, products: List['Product']) -> bool:
        """
        Index multiple products in bulk
        
        Args:
            products: List of Product model instances
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Ensure index exists
            if not self.index:
                self._ensure_index_exists()
            
            # Convert products to documents
            documents = [self._product_to_document(p) for p in products]
            
            # Bulk index
            self.index.add_documents(documents, primary_key=SearchConfig.PRIMARY_KEY)
            
            logger.info(f"Bulk indexed {len(documents)} products")
            return True
            
        except Exception as e:
            logger.error(f"Bulk index failed: {e}")
            return False
    
    def _ensure_index_exists(self):
        """Ensure index exists and is configured"""
        try:
            from meilisearch.errors import MeilisearchApiError
            config = SearchConfig.get_config()
            
            if not self.client:
                raise Exception("Meilisearch client is not initialized")
            
            # Try to get index
            try:
                self.index = self.client.get_index(SearchConfig.INDEX_NAME)
                logger.info(f"Index {SearchConfig.INDEX_NAME} already exists")
            except MeilisearchApiError as e:
                if e.status_code == 404:
                    # Index doesn't exist, create it
                    logger.info(f"Creating index {SearchConfig.INDEX_NAME}...")
                    self.index = self.client.create_index(
                        uid=SearchConfig.INDEX_NAME,
                        primary_key=SearchConfig.PRIMARY_KEY
                    )
                    logger.info(f"Index {SearchConfig.INDEX_NAME} created successfully")
                else:
                    raise
            except Exception as e:
                # For other errors, try to create index
                logger.warning(f"Error getting index, trying to create: {e}")
                try:
                    self.index = self.client.create_index(
                        uid=SearchConfig.INDEX_NAME,
                        primary_key=SearchConfig.PRIMARY_KEY
                    )
                    logger.info(f"Index {SearchConfig.INDEX_NAME} created successfully")
                except Exception as create_error:
                    logger.error(f"Failed to create index: {create_error}")
                    raise
            
            if not self.index:
                raise Exception("Failed to get or create index")
            
            # Update index settings (these might take time, so do them in try-except)
            try:
                settings = SearchConfig.get_index_settings()
                
                # Update settings one by one with error handling
                try:
                    self.index.update_searchable_attributes(settings['searchableAttributes'])
                except Exception as e:
                    logger.warning(f"Failed to update searchable attributes: {e}")
                
                try:
                    self.index.update_filterable_attributes(settings['filterableAttributes'])
                except Exception as e:
                    logger.warning(f"Failed to update filterable attributes: {e}")
                
                try:
                    self.index.update_sortable_attributes(settings['sortableAttributes'])
                except Exception as e:
                    logger.warning(f"Failed to update sortable attributes: {e}")
                
                try:
                    self.index.update_ranking_rules(settings['rankingRules'])
                except Exception as e:
                    logger.warning(f"Failed to update ranking rules: {e}")
                
                try:
                    self.index.update_synonyms(settings['synonyms'])
                except Exception as e:
                    logger.warning(f"Failed to update synonyms: {e}")
                
                try:
                    self.index.update_typo_tolerance(settings['typoTolerance'])
                except Exception as e:
                    logger.warning(f"Failed to update typo tolerance: {e}")
                
                logger.info(f"Index {SearchConfig.INDEX_NAME} configured successfully")
            except Exception as e:
                logger.warning(f"Some index settings failed to update: {e}")
                # Don't raise, index is usable even if settings fail
            
        except Exception as e:
            logger.error(f"Failed to ensure index exists: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _product_to_document(self, product: 'Product') -> Dict:
        """Convert Product model to Meilisearch document"""
        # Get vehicle type IDs if available
        vehicle_type_ids = []
        try:
            # Try to get vehicle types through ProductVehicleType relationship
            if hasattr(product, 'vehicle_types'):
                vehicle_type_ids = [vt.vehicle_type_id for vt in product.vehicle_types]
        except Exception:
            # If relationship doesn't exist or error, use empty list
            vehicle_type_ids = []
        
        document = {
            'id': product.id,
            'sku': product.sku or '',
            'oem_code': product.oem_code or '',
            'name': product.name or '',
            'name_fa': product.name_fa or '',
            'description': product.description or '',
            'description_fa': getattr(product, 'description_fa', None) or '',
            'brand_id': product.brand_id,
            'category_id': product.category_id,
            'subcategory_id': getattr(product, 'subcategory_id', None),
            'stock_quantity': product.stock_quantity or 0,
            'is_active': product.is_active,
            'is_featured': product.is_featured,
            'is_isaco_wh15': getattr(product, 'is_isaco_wh15', False),
            'retail_price_cash': product.retail_price_cash or 0,
            'bulk_price_cash': product.bulk_price_cash or 0,
            'retail_price_check': product.retail_price_check or 0,
            'bulk_price_check': product.bulk_price_check or 0,
            'primary_image': product.primary_image or '',
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'vehicle_type_ids': vehicle_type_ids
        }
        
        return document
    
    def _build_filter_string(self, filters: Optional[Dict]) -> Optional[str]:
        """
        Build Meilisearch filter string from dictionary
        
        Args:
            filters: Dictionary of filters (e.g., {'brand_id': 1, 'stock_quantity': '> 0'})
        
        Returns:
            Filter string or None
        """
        if not filters:
            return None
        
        filter_parts = []
        
        for key, value in filters.items():
            if value is None:
                continue
            
            # Handle comparison operators (string format like "> 0")
            if isinstance(value, str) and value.strip().startswith(('>', '<', '>=', '<=')):
                filter_parts.append(f"{key} {value.strip()}")
            elif isinstance(value, list):
                # Multiple values (OR) - Meilisearch uses IN syntax
                if value:  # Only add if list is not empty
                    values_str = ', '.join(str(v) for v in value)
                    filter_parts.append(f"{key} IN [{values_str}]")
            elif isinstance(value, (int, float, bool)):
                filter_parts.append(f"{key} = {value}")
            elif isinstance(value, str):
                # String value
                filter_parts.append(f"{key} = {value}")
            else:
                filter_parts.append(f"{key} = {value}")
        
        return ' AND '.join(filter_parts) if filter_parts else None

# Singleton instance
_search_service = None

def get_search_service() -> SearchService:
    """Get singleton SearchService instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

