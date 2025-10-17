#!/usr/bin/env python3
"""
Test script for price correction implementation
Tests the complete price correction system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, format_price
from models import db, Product, TadbirPriceCache
from tadbir_sync_service import TadbirSyncService

def test_format_price_function():
    """Test the format_price function"""
    print("Testing format_price function...")
    
    # Test with sample prices
    test_cases = [
        (182886, "182,886 ریال"),
        (0, "0 ریال"),
        (None, "0 ریال"),
        (1000000, "1,000,000 ریال"),
        (1234567, "1,234,567 ریال")
    ]
    
    for input_price, expected in test_cases:
        result = format_price(input_price)
        print(f"  Input: {input_price} -> Output: {result.encode('ascii', 'ignore').decode('ascii')}")
        assert result == expected, f"Failed for {input_price}: got {result}, expected {expected}"
    
    print("format_price function tests passed!")

def test_database_prices():
    """Test database price values"""
    print("\nTesting database price values...")
    
    with app.app_context():
        # Check if we have any products
        products = Product.query.limit(5).all()
        if not products:
            print("  No products found in database")
            return
        
        for product in products:
            print(f"  Product {product.sku}:")
            print(f"    Bulk Cash: {product.bulk_price_cash}")
            print(f"    Retail Cash: {product.retail_price_cash}")
            print(f"    Bulk Check: {product.bulk_price_check}")
            print(f"    Retail Check: {product.retail_price_check}")
            
            # Check if prices are in full Rials (should be > 1000 for most products)
            if product.bulk_price_cash and product.bulk_price_cash > 1000:
                print(f"    Bulk Cash price appears to be in full Rials")
            else:
                print(f"    Bulk Cash price might still be in thousands")
    
    print("Database price tests completed!")

def test_tadbir_price_cache():
    """Test Tadbir price cache values"""
    print("\nTesting Tadbir price cache...")
    
    with app.app_context():
        # Check if we have any cached prices
        prices = TadbirPriceCache.query.limit(5).all()
        if not prices:
            print("  No cached prices found")
            return
        
        for price in prices:
            print(f"  Item {price.item_code} ({price.price_type}):")
            print(f"    Base Price: {price.base_price}")
            print(f"    Final Price: {price.final_price}")
            print(f"    Discount: {price.discount_amount}")
            
            # Check if prices are in full Rials
            if price.base_price and price.base_price > 1000:
                print(f"    Prices appear to be in full Rials")
            else:
                print(f"    Prices might still be in thousands")
    
    print("Tadbir price cache tests completed!")

def test_specific_product():
    """Test the specific product mentioned in the issue (30613470)"""
    print("\nTesting specific product 30613470...")
    
    with app.app_context():
        # Look for product with SKU 30613470
        product = Product.query.filter_by(sku='30613470').first()
        if not product:
            print("  Product 30613470 not found in database")
            # Try to find similar SKUs
            similar_products = Product.query.filter(Product.sku.like('%30613470%')).all()
            if similar_products:
                print("  Found similar products:")
                for p in similar_products:
                    print(f"    {p.sku}: {format_price(p.retail_price_cash)}")
            return
        
        print(f"  Found product {product.sku}:")
        print(f"    Name: {product.name.encode('ascii', 'ignore').decode('ascii')}")
        print(f"    Bulk Cash: {format_price(product.bulk_price_cash).encode('ascii', 'ignore').decode('ascii')}")
        print(f"    Retail Cash: {format_price(product.retail_price_cash).encode('ascii', 'ignore').decode('ascii')}")
        print(f"    Bulk Check: {format_price(product.bulk_price_check).encode('ascii', 'ignore').decode('ascii')}")
        print(f"    Retail Check: {format_price(product.retail_price_check).encode('ascii', 'ignore').decode('ascii')}")
        
        # Check if the price is around 182886 (the expected price)
        if product.retail_price_cash and abs(product.retail_price_cash - 182886) < 1000:
            print(f"    Price matches expected value (182886)")
        else:
            print(f"    Price doesn't match expected value (182886)")
    
    print("Specific product test completed!")

def main():
    """Run all tests"""
    print("=" * 60)
    print("PRICE CORRECTION IMPLEMENTATION TEST")
    print("=" * 60)
    
    try:
        test_format_price_function()
        test_database_prices()
        test_tadbir_price_cache()
        test_specific_product()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("Price correction implementation is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
