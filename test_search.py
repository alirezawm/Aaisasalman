"""
Test script for Meilisearch integration
Tests search functionality and sync operations
"""
from app import app
from search_service import get_search_service
from search_sync import get_sync_service
from models import Product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_service():
    """Test search service functionality"""
    print("=" * 60)
    print("Testing Search Service")
    print("=" * 60)
    
    with app.app_context():
        search_service = get_search_service()
        
        # Test 1: Check availability
        print("\n1. Checking Meilisearch availability...")
        is_available = search_service.is_available()
        print(f"   Status: {'✓ Available' if is_available else '✗ Not Available'}")
        
        if not is_available:
            print("\n   ⚠ Meilisearch is not available. Please start it first:")
            print("   docker-compose -f docker-compose.meilisearch.yml up -d")
            return False
        
        # Test 2: Test search
        print("\n2. Testing search functionality...")
        test_queries = [
            "کفش",
            "مشکی",
            "تیغه",
            "برف پاک کن"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = search_service.search(
                query=query,
                filters={'is_active': True, 'stock_quantity': '> 0'},
                page=1,
                per_page=5
            )
            
            if results.get('from_search_engine'):
                print(f"   ✓ Found {results.get('total', 0)} results")
                if results.get('products'):
                    print(f"   ✓ Product IDs: {results['products'][:5]}")
            else:
                print(f"   ✗ Search failed or fallback to SQL")
        
        # Test 3: Test suggestions
        print("\n3. Testing search suggestions...")
        suggestions = search_service.search_suggestions("کفش", limit=5)
        if suggestions:
            print(f"   ✓ Suggestions: {suggestions}")
        else:
            print("   ✗ No suggestions")
        
        print("\n" + "=" * 60)
        print("Search Service Tests Completed")
        print("=" * 60)
        return True

def test_sync_service():
    """Test sync service functionality"""
    print("\n" + "=" * 60)
    print("Testing Sync Service")
    print("=" * 60)
    
    with app.app_context():
        sync_service = get_sync_service()
        
        # Test 1: Sync single product
        print("\n1. Testing single product sync...")
        products = Product.query.filter_by(is_active=True).limit(1).all()
        if products:
            product = products[0]
            success = sync_service.sync_product(product.id)
            print(f"   {'✓' if success else '✗'} Synced product {product.id} ({product.sku})")
        else:
            print("   ⚠ No active products found")
        
        # Test 2: Get sync status
        print("\n2. Getting sync status...")
        try:
            from search_service import get_search_service
            search_service = get_search_service()
            if search_service.is_available():
                stats = search_service.index.get_stats()
                print(f"   ✓ Index contains {stats.get('numberOfDocuments', 0)} documents")
            else:
                print("   ✗ Meilisearch not available")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("Sync Service Tests Completed")
        print("=" * 60)

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Meilisearch Integration Tests")
    print("=" * 60)
    print()
    
    # Test search service
    search_ok = test_search_service()
    
    if search_ok:
        # Test sync service
        test_sync_service()
        
        print("\n" + "=" * 60)
        print("All Tests Completed")
        print("=" * 60)
        print("\n✓ If all tests passed, Meilisearch is working correctly!")
    else:
        print("\n" + "=" * 60)
        print("Tests Incomplete - Meilisearch Not Available")
        print("=" * 60)
        print("\n⚠ Please start Meilisearch and try again")

if __name__ == '__main__':
    main()

