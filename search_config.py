"""
Configuration for Meilisearch integration
"""
import os
from flask import current_app

class SearchConfig:
    """Configuration class for Meilisearch"""
    
    # Meilisearch connection settings
    HOST = os.environ.get('MEILISEARCH_HOST', 'http://localhost:7700')
    MASTER_KEY = os.environ.get('MEILISEARCH_MASTER_KEY', None)  # Optional for development
    TIMEOUT = int(os.environ.get('MEILISEARCH_TIMEOUT', '5'))
    
    # Index settings
    INDEX_NAME = 'products'
    PRIMARY_KEY = 'id'
    
    # Search settings
    DEFAULT_LIMIT = 12
    MAX_LIMIT = 100
    DEFAULT_OFFSET = 0
    
    # Index configuration
    SEARCHABLE_ATTRIBUTES = [
        'name',
        'name_fa', 
        'sku',
        'oem_code',
        'description',
        'description_fa'
    ]
    
    FILTERABLE_ATTRIBUTES = [
        'brand_id',
        'category_id',
        'subcategory_id',
        'vehicle_type_id',
        'vehicle_type_ids',  # Array field for multiple vehicle types
        'stock_quantity',
        'is_active',
        'is_featured',
        'is_isaco_wh15'
    ]
    
    SORTABLE_ATTRIBUTES = [
        'created_at',
        'stock_quantity',
        'retail_price_cash',
        'bulk_price_cash',
        'retail_price_check',
        'bulk_price_check'
    ]
    
    RANKING_RULES = [
        'words',
        'typo',
        'proximity',
        'attribute',
        'sort',
        'exactness'
    ]
    
    # Typo tolerance settings
    TYPO_TOLERANCE_ENABLED = True
    MIN_WORD_SIZE_FOR_TYPO = 4
    TYPO_TOLERANCE_MAX_TYPOS = 2
    
    # Synonyms (Persian/Farsi)
    SYNONYMS = {
        'خودرو': ['ماشین', 'اتومبیل', 'vehicle'],
        'قطعه': ['لوازم', 'اجزا', 'part'],
        'کفش': ['shoes'],
        'مشکی': ['سیاه', 'black'],
        'مردانه': ['men', 'male']
    }
    
    # Attributes to retrieve in search results
    DEFAULT_ATTRIBUTES_TO_RETRIEVE = [
        'id',
        'sku',
        'name',
        'name_fa',
        'primary_image',
        'brand_id',
        'category_id',
        'stock_quantity',
        'is_active',
        'is_featured'
    ]
    
    # Attributes to highlight in search results
    ATTRIBUTES_TO_HIGHLIGHT = [
        'name',
        'name_fa',
        'description',
        'description_fa'
    ]
    
    @staticmethod
    def get_config():
        """Get configuration dictionary"""
        return {
            'host': SearchConfig.HOST,
            'master_key': SearchConfig.MASTER_KEY,
            'timeout': SearchConfig.TIMEOUT,
            'index_name': SearchConfig.INDEX_NAME,
            'primary_key': SearchConfig.PRIMARY_KEY
        }
    
    @staticmethod
    def get_index_settings():
        """Get index settings for Meilisearch"""
        return {
            'searchableAttributes': SearchConfig.SEARCHABLE_ATTRIBUTES,
            'filterableAttributes': SearchConfig.FILTERABLE_ATTRIBUTES,
            'sortableAttributes': SearchConfig.SORTABLE_ATTRIBUTES,
            'rankingRules': SearchConfig.RANKING_RULES,
            'synonyms': SearchConfig.SYNONYMS,
            'typoTolerance': {
                'enabled': SearchConfig.TYPO_TOLERANCE_ENABLED,
                'minWordSizeForTypos': {
                    'oneTypo': SearchConfig.MIN_WORD_SIZE_FOR_TYPO,
                    'twoTypos': SearchConfig.MIN_WORD_SIZE_FOR_TYPO + 2
                },
                'disableOnAttributes': [],
                'disableOnWords': []
            }
        }

