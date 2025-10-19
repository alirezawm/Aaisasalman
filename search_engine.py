"""
Intelligent Search Engine for Asia Salman Automotive Parts
Implements multi-layer search strategy with auto-suggestions and analytics
"""

from flask import current_app
from sqlalchemy import or_, and_, func, text
from sqlalchemy.orm import joinedload
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import models

class IntelligentSearchEngine:
    """Multi-layer search engine with intelligent ranking and suggestions"""
    
    def __init__(self):
        self.search_layers = [
            'exact_match',      # Exact SKU/OEM code match
            'brand_model',      # Brand + Model specific search
            'category_search',  # Category-based search
            'fuzzy_search',     # Fuzzy matching for typos
            'semantic_search'   # AI-powered semantic search
        ]
    
    def search(self, query: str, filters: Dict = None, user_preferences: Dict = None, 
               limit: int = 50) -> List[Dict]:
        """
        Main search method implementing multi-layer strategy
        
        Args:
            query: Search query string
            filters: Dictionary of filters (brand_id, category_id, etc.)
            user_preferences: User's search preferences
            limit: Maximum number of results
            
        Returns:
            List of ranked search results
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        results = []
        
        # Layer 1: Exact Match (Highest Priority)
        exact_results = self._exact_match_search(query)
        if exact_results:
            return self._rank_results(exact_results, user_preferences)[:limit]
        
        # Layer 2: Brand-Model Context Search
        brand_model_results = self._brand_model_search(query, filters)
        results.extend(brand_model_results)
        
        # Layer 3: Category-Based Search
        category_results = self._category_search(query, filters)
        results.extend(category_results)
        
        # Layer 4: Fuzzy Search for Typos
        fuzzy_results = self._fuzzy_search(query, filters)
        results.extend(fuzzy_results)
        
        # Layer 5: Semantic Search
        semantic_results = self._semantic_search(query, filters)
        results.extend(semantic_results)
        
        # Rank and deduplicate results
        ranked_results = self._rank_and_deduplicate(results, user_preferences)
        
        # Apply additional filters
        if filters:
            ranked_results = self._apply_filters(ranked_results, filters)
        
        return ranked_results[:limit]
    
    def _exact_match_search(self, query: str) -> List[Dict]:
        """Exact match search for SKU and OEM codes"""
        try:
            products = models.Product.query.filter(
                or_(
                    models.Product.sku.ilike(f'%{query}%'),
                    models.Product.oem_code.ilike(f'%{query}%'),
                    models.Product.code.ilike(f'%{query}%')  # Legacy code field
                ),
                models.Product.is_active == True
            ).options(
                joinedload(models.Product.brand),
                joinedload(models.Product.category),
                joinedload(models.Product.subcategory)
            ).all()
            
            return [self._product_to_dict(p) for p in products]
        except Exception as e:
            current_app.logger.error(f"Exact match search error: {e}")
            return []
    
    def _brand_model_search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search within specific brand/model context"""
        try:
            # Extract brand and model from query
            brand_name = self._extract_brand_from_query(query)
            model_name = self._extract_model_from_query(query)
            vehicle_type_name = self._extract_vehicle_type_from_query(query)
            
            query_obj = models.Product.query.filter(models.Product.is_active == True)
            
            # Build search conditions
            search_conditions = []
            
            # Brand search
            if brand_name:
                search_conditions.append(
                    models.Product.brand.has(
                        or_(
                            models.Brand.name.ilike(f'%{brand_name}%'),
                            models.Brand.name_fa.ilike(f'%{brand_name}%')
                        )
                    )
                )
            
            # Model search
            if model_name:
                search_conditions.append(
                    models.Product.compatible_models.ilike(f'%{model_name}%')
                )
            
            # Vehicle type search
            if vehicle_type_name:
                search_conditions.append(
                    models.Product.vehicle_types.any(
                        models.VehicleType.name.ilike(f'%{vehicle_type_name}%')
                    )
                )
            
            # General product search
            search_conditions.extend([
                models.Product.name.ilike(f'%{query}%'),
                models.Product.name_fa.ilike(f'%{query}%'),
                models.Product.description.ilike(f'%{query}%'),
                models.Product.description_fa.ilike(f'%{query}%')
            ])
            
            # Apply search conditions
            if search_conditions:
                query_obj = query_obj.filter(or_(*search_conditions))
            
            products = query_obj.options(
                joinedload(models.Product.brand),
                joinedload(models.Product.category),
                joinedload(models.Product.subcategory)
            ).limit(20).all()
            
            return [self._product_to_dict(p) for p in products]
        except Exception as e:
            current_app.logger.error(f"Brand model search error: {e}")
            return []
    
    def _category_search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search within categories and subcategories"""
        try:
            # Search in category names
            categories = models.PartCategory.query.filter(
                or_(
                    models.PartCategory.category_name.ilike(f'%{query}%'),
                    models.PartCategory.category_name_fa.ilike(f'%{query}%')
                ),
                models.PartCategory.is_active == True
            ).all()
            
            category_ids = [c.id for c in categories]
            
            # Search in subcategories
            subcategories = models.PartSubcategory.query.filter(
                or_(
                    models.PartSubcategory.subcategory_name.ilike(f'%{query}%'),
                    models.PartSubcategory.subcategory_name_fa.ilike(f'%{query}%')
                ),
                models.PartSubcategory.is_active == True
            ).all()
            
            subcategory_ids = [s.id for s in subcategories]
            
            # Get products from matching categories
            query_obj = models.Product.query.filter(models.Product.is_active == True)
            
            if category_ids or subcategory_ids:
                conditions = []
                if category_ids:
                    conditions.append(models.Product.category_id.in_(category_ids))
                if subcategory_ids:
                    conditions.append(models.Product.subcategory_id.in_(subcategory_ids))
                
                query_obj = query_obj.filter(or_(*conditions))
            
            # Also search in product names and descriptions
            query_obj = query_obj.filter(
                or_(
                    models.Product.name.ilike(f'%{query}%'),
                    models.Product.name_fa.ilike(f'%{query}%'),
                    models.Product.description.ilike(f'%{query}%'),
                    models.Product.description_fa.ilike(f'%{query}%')
                )
            )
            
            products = query_obj.options(
                joinedload(models.Product.brand),
                joinedload(models.Product.category),
                joinedload(models.Product.subcategory)
            ).limit(30).all()
            
            return [self._product_to_dict(p) for p in products]
        except Exception as e:
            current_app.logger.error(f"Category search error: {e}")
            return []
    
    def _fuzzy_search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Fuzzy search for handling typos and variations"""
        try:
            # Simple fuzzy matching using LIKE with wildcards
            fuzzy_patterns = self._generate_fuzzy_patterns(query)
            
            conditions = []
            for pattern in fuzzy_patterns:
                conditions.extend([
                    models.Product.name.ilike(pattern),
                    models.Product.name_fa.ilike(pattern),
                    models.Product.description.ilike(pattern),
                    models.Product.description_fa.ilike(pattern)
                ])
            
            products = models.Product.query.filter(
                or_(*conditions),
                models.Product.is_active == True
            ).options(
                joinedload(models.Product.brand),
                joinedload(models.Product.category),
                joinedload(models.Product.subcategory)
            ).limit(20).all()
            
            return [self._product_to_dict(p) for p in products]
        except Exception as e:
            current_app.logger.error(f"Fuzzy search error: {e}")
            return []
    
    def _semantic_search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Semantic search using tags and keywords"""
        try:
            # Search in tags and technical specs
            products = models.Product.query.filter(
                or_(
                    models.Product.tags.ilike(f'%{query}%'),
                    models.Product.technical_specs.ilike(f'%{query}%')
                ),
                models.Product.is_active == True
            ).options(
                joinedload(models.Product.brand),
                joinedload(models.Product.category),
                joinedload(models.Product.subcategory)
            ).limit(15).all()
            
            return [self._product_to_dict(p) for p in products]
        except Exception as e:
            current_app.logger.error(f"Semantic search error: {e}")
            return []
    
    def _extract_brand_from_query(self, query: str) -> Optional[str]:
        """Extract brand name from search query"""
        brands = models.Brand.query.filter(models.Brand.is_active == True).all()
        
        for brand in brands:
            if (brand.name.lower() in query.lower() or 
                brand.name_fa in query):
                return brand.name
        
        return None
    
    def _extract_model_from_query(self, query: str) -> Optional[str]:
        """Extract model name from search query"""
        # Common model patterns
        model_patterns = [
            r'\b(corolla|camry|prius|rav4|highlander)\b',
            r'\b(elantra|sonata|tucson|santa fe)\b',
            r'\b(optima|sportage|sorento|cerato)\b'
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1).title()
        
        return None
    
    def _extract_vehicle_type_from_query(self, query: str) -> Optional[str]:
        """Extract vehicle type from search query"""
        try:
            # Get all vehicle types from database
            vehicle_types = models.VehicleType.query.all()
            
            query_lower = query.lower()
            for vehicle_type in vehicle_types:
                if vehicle_type.name.lower() in query_lower:
                    return vehicle_type.name
            
            return None
        except Exception as e:
            current_app.logger.error(f"Vehicle type extraction error: {e}")
            return None
    
    def _generate_fuzzy_patterns(self, query: str) -> List[str]:
        """Generate fuzzy search patterns for typo tolerance"""
        patterns = []
        
        # Original query
        patterns.append(f'%{query}%')
        
        # Remove vowels for Persian text
        if any('\u0600' <= char <= '\u06FF' for char in query):
            no_vowels = re.sub(r'[اُِوآی]', '', query)
            if no_vowels != query:
                patterns.append(f'%{no_vowels}%')
        
        # Common typos
        typos = {
            'brake': ['break', 'brak'],
            'filter': ['filtre', 'filtr'],
            'engine': ['engin', 'engne'],
            'toyota': ['toyta', 'toyot'],
            'hyundai': ['hyundae', 'hyundai']
        }
        
        for correct, variations in typos.items():
            if correct in query.lower():
                for variation in variations:
                    patterns.append(f'%{query.lower().replace(correct, variation)}%')
        
        return patterns[:5]  # Limit to 5 patterns
    
    def _rank_results(self, results: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """Rank search results based on relevance and user preferences"""
        if not results:
            return results
        
        for result in results:
            score = 0
            
            # Base score from search layer
            score += result.get('search_score', 0)
            
            # Stock availability bonus
            if result.get('stock_quantity', 0) > 0:
                score += 10
            
            # Featured products bonus
            if result.get('is_featured', False):
                score += 5
            
            # User preferences bonus
            if user_preferences:
                preferred_brands = user_preferences.get('preferred_brands', [])
                if result.get('brand_id') in preferred_brands:
                    score += 15
            
            result['relevance_score'] = score
        
        # Sort by relevance score
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _rank_and_deduplicate(self, results: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """Remove duplicates and rank results"""
        # Remove duplicates based on product ID
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        return self._rank_results(unique_results, user_preferences)
    
    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply additional filters to search results"""
        filtered_results = []
        
        for result in results:
            include = True
            
            # Brand filter
            if 'brand_id' in filters and result.get('brand_id') != filters['brand_id']:
                include = False
            
            # Category filter
            if 'category_id' in filters and result.get('category_id') != filters['category_id']:
                include = False
            
            # Price range filter
            if 'price_min' in filters and result.get('price', 0) < filters['price_min']:
                include = False
            
            if 'price_max' in filters and result.get('price', 0) > filters['price_max']:
                include = False
            
            # Stock filter
            if filters.get('in_stock_only', False) and result.get('stock_quantity', 0) <= 0:
                include = False
            
            if include:
                filtered_results.append(result)
        
        return filtered_results
    
    def _product_to_dict(self, product) -> Dict:
        """Convert Product model to dictionary"""
        return {
            'id': product.id,
            'sku': product.sku,
            'oem_code': product.oem_code,
            'name': product.name,
            'name_fa': product.name_fa,
            'description': product.description,
            'description_fa': product.description_fa,
            'brand_id': product.brand_id,
            'brand_name': product.brand.name if product.brand else None,
            'brand_name_fa': product.brand.name_fa if product.brand else None,
            'category_id': product.category_id,
            'category_name': product.category.category_name if product.category else None,
            'category_name_fa': product.category.category_name_fa if product.category else None,
            'subcategory_id': product.subcategory_id,
            'subcategory_name': product.subcategory.subcategory_name if product.subcategory else None,
            'subcategory_name_fa': product.subcategory.subcategory_name_fa if product.subcategory else None,
            'bulk_price_cash': product.bulk_price_cash,
            'retail_price_cash': product.retail_price_cash,
            'bulk_price_check': product.bulk_price_check,
            'retail_price_check': product.retail_price_check,
            'stock_quantity': product.stock_quantity,
            'min_order_quantity': product.min_order_quantity,
            'primary_image': product.primary_image,
            'is_featured': product.is_featured,
            'compatible_models': product.get_compatible_models(),
            'tags': product.get_tags(),
            'search_score': 0  # Will be set by individual search methods
        }
    
    def get_suggestions(self, query: str, context: Dict = None) -> List[Dict]:
        """Get search suggestions based on query"""
        if not query or len(query.strip()) < 2:
            return []
        
        suggestions = []
        query = query.strip()
        
        # Brand suggestions
        # Use simple ILIKE for better performance and to avoid SQLite stack overflow
        from routes import normalize_fa_text
        norm_q = normalize_fa_text(query)
        brands = models.Brand.query.filter(
            or_(
                models.Brand.name.ilike(f'%{norm_q}%'),
                models.Brand.name_fa.ilike(f'%{norm_q}%')
            ),
            models.Brand.is_active == True
        ).limit(5).all()
        
        for brand in brands:
            suggestions.append({
                'type': 'brand',
                'text': brand.name,
                'text_fa': brand.name_fa,
                'id': brand.id,
                'icon': 'fas fa-car'
            })
        
        # Model suggestions (if brand context exists)
        if context and 'brand_id' in context:
            models_query = models.VehicleModel.query.filter(
                models.VehicleModel.brand_id == context['brand_id'],
                or_(
                    models.VehicleModel.model_name.ilike(f'%{norm_q}%'),
                    models.VehicleModel.model_name_fa.ilike(f'%{norm_q}%')
                ),
                models.VehicleModel.is_active == True
            ).limit(5).all()
            
            for model in models_query:
                suggestions.append({
                    'type': 'model',
                    'text': model.model_name,
                    'text_fa': model.model_name_fa,
                    'id': model.id,
                    'icon': 'fas fa-car-side'
                })
        
        # Category suggestions
        categories = models.PartCategory.query.filter(
            or_(
                models.PartCategory.category_name.ilike(f'%{query}%'),
                models.PartCategory.category_name_fa.ilike(f'%{query}%')
            ),
            models.PartCategory.is_active == True
        ).limit(5).all()
        
        for category in categories:
            suggestions.append({
                'type': 'category',
                'text': category.category_name,
                'text_fa': category.category_name_fa,
                'id': category.id,
                'icon': category.icon_class or 'fas fa-cog'
            })
        
        # Product suggestions
        products = models.Product.query.filter(
            or_(
                models.Product.name.ilike(f'%{norm_q}%'),
                models.Product.name_fa.ilike(f'%{norm_q}%')
            ),
            models.Product.is_active == True
        ).limit(5).all()
        
        for product in products:
            suggestions.append({
                'type': 'product',
                'text': product.name,
                'text_fa': product.name_fa,
                'id': product.id,
                'sku': product.sku,
                'icon': 'fas fa-box'
            })
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def track_search(self, user_id: int, query: str, filters: Dict, results_count: int):
        """Track search for analytics"""
        try:
            search_history = models.UserSearchHistory(
                user_id=user_id,
                search_query=query,
                search_filters=json.dumps(filters) if filters else None,
                results_count=results_count
            )
            models.db.session.add(search_history)
            models.db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Search tracking error: {e}")
    
    def track_click(self, user_id: int, product_id: int, search_context: Dict):
        """Track product clicks for analytics"""
        try:
            # Update the most recent search history with clicked product
            recent_search = models.UserSearchHistory.query.filter(
                models.UserSearchHistory.user_id == user_id,
                models.UserSearchHistory.search_query == search_context.get('query', ''),
                models.UserSearchHistory.clicked_product_id.is_(None)
            ).order_by(models.UserSearchHistory.created_at.desc()).first()
            
            if recent_search:
                recent_search.clicked_product_id = product_id
                models.db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Click tracking error: {e}")


class AutoSuggestionEngine:
    """Real-time auto-suggestion engine"""
    
    def __init__(self):
        self.suggestion_types = {
            'brands': self._get_brand_suggestions,
            'models': self._get_model_suggestions,
            'parts': self._get_part_suggestions,
            'categories': self._get_category_suggestions
        }
    
    async def get_suggestions(self, query: str, context: Dict = None) -> List[Dict]:
        """Get comprehensive suggestions"""
        suggestions = []
        
        # Brand suggestions
        if query.length >= 2:
            suggestions.extend(await self._get_brand_suggestions(query))
        
        # Model suggestions (if brand context exists)
        if context and 'brand_id' in context:
            suggestions.extend(await self._get_model_suggestions(query, context['brand_id']))
        
        # Part suggestions
        if len(query) >= 3:
            suggestions.extend(await self._get_part_suggestions(query, context))
        
        return self._rank_suggestions(suggestions, query)
    
    async def _get_brand_suggestions(self, query: str) -> List[Dict]:
        """Get brand suggestions"""
        brands = models.Brand.query.filter(
            or_(
                models.Brand.name.ilike(f'%{query}%'),
                models.Brand.name_fa.ilike(f'%{query}%')
            ),
            models.Brand.is_active == True
        ).limit(5).all()
        
        return [{
            'type': 'brand',
            'text': brand.name,
            'text_fa': brand.name_fa,
            'id': brand.id,
            'icon': 'fas fa-car',
            'relevance': self._calculate_relevance(brand.name, query)
        } for brand in brands]
    
    async def _get_model_suggestions(self, query: str, brand_id: int) -> List[Dict]:
        """Get model suggestions for specific brand"""
        models_query = models.VehicleModel.query.filter(
            models.VehicleModel.brand_id == brand_id,
            or_(
                models.VehicleModel.model_name.ilike(f'%{query}%'),
                models.VehicleModel.model_name_fa.ilike(f'%{query}%')
            ),
            models.VehicleModel.is_active == True
        ).limit(5).all()
        
        return [{
            'type': 'model',
            'text': model.model_name,
            'text_fa': model.model_name_fa,
            'id': model.id,
            'icon': 'fas fa-car-side',
            'relevance': self._calculate_relevance(model.model_name, query)
        } for model in models_query]
    
    async def _get_part_suggestions(self, query: str, context: Dict = None) -> List[Dict]:
        """Get part suggestions"""
        products = models.Product.query.filter(
            or_(
                models.Product.name.ilike(f'%{query}%'),
                models.Product.name_fa.ilike(f'%{query}%')
            ),
            models.Product.is_active == True
        ).limit(5).all()
        
        return [{
            'type': 'product',
            'text': product.name,
            'text_fa': product.name_fa,
            'id': product.id,
            'sku': product.sku,
            'icon': 'fas fa-box',
            'relevance': self._calculate_relevance(product.name, query)
        } for product in products]
    
    async def _get_category_suggestions(self, query: str) -> List[Dict]:
        """Get category suggestions"""
        categories = models.PartCategory.query.filter(
            or_(
                models.PartCategory.category_name.ilike(f'%{query}%'),
                models.PartCategory.category_name_fa.ilike(f'%{query}%')
            ),
            models.PartCategory.is_active == True
        ).limit(5).all()
        
        return [{
            'type': 'category',
            'text': category.category_name,
            'text_fa': category.category_name_fa,
            'id': category.id,
            'icon': category.icon_class or 'fas fa-cog',
            'relevance': self._calculate_relevance(category.category_name, query)
        } for category in categories]
    
    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate relevance score for suggestions"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Exact match gets highest score
        if text_lower == query_lower:
            return 1.0
        
        # Starts with query gets high score
        if text_lower.startswith(query_lower):
            return 0.9
        
        # Contains query gets medium score
        if query_lower in text_lower:
            return 0.7
        
        # Fuzzy match gets low score
        return 0.5
    
    def _rank_suggestions(self, suggestions: List[Dict], query: str) -> List[Dict]:
        """Rank suggestions by relevance"""
        return sorted(suggestions, key=lambda x: x.get('relevance', 0), reverse=True)


# Global search engine instance
search_engine = IntelligentSearchEngine()
auto_suggestion_engine = AutoSuggestionEngine()
