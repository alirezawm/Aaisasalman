#!/usr/bin/env python3
"""
Simple Inventory Diagnostic Tool
"""

from app import app
from models import db, TadbirSyncLog, TadbirInventoryCache
from tadbir_api_service import TadbirAPIService
from datetime import datetime, timedelta
import requests

def run_simple_diagnostic():
    """Simple inventory diagnostic"""
    
    with app.app_context():
        print("=" * 60)
        print("Inventory Diagnostic Report")
        print("=" * 60)
        
        # 1. Check current cache status
        print("\n1. Current Cache Status:")
        inventory_count = TadbirInventoryCache.query.count()
        latest_inventory = TadbirInventoryCache.query.order_by(TadbirInventoryCache.cached_at.desc()).first()
        
        print(f"   Total inventory records in cache: {inventory_count}")
        if latest_inventory:
            print(f"   Last update: {latest_inventory.cached_at}")
            print(f"   Sample record: {latest_inventory.item_code} - {latest_inventory.quantity}")
        else:
            print("   No inventory records in cache")
        
        # 2. Check recent sync logs
        print("\n2. Recent Sync Status:")
        recent_logs = TadbirSyncLog.query.filter_by(sync_type='inventory').order_by(
            TadbirSyncLog.started_at.desc()
        ).limit(5).all()
        
        for log in recent_logs:
            print(f"   {log.started_at}: {log.status} - {log.records_successful}/{log.records_processed} successful")
            if log.error_message:
                print(f"     Error: {log.error_message}")
        
        # 3. Test API connection
        print("\n3. API Connection Test:")
        try:
            api_service = TadbirAPIService()
            connection_test = api_service.test_connection()
            print(f"   Connection: {'Success' if connection_test.get('success') else 'Failed'}")
            if not connection_test.get('success'):
                print(f"   Error: {connection_test.get('message')}")
        except Exception as e:
            print(f"   Connection error: {e}")
        
        # 4. Test inventory endpoint
        print("\n4. Inventory Endpoint Test:")
        try:
            api_service = TadbirAPIService()
            inventory = api_service.get_inventory(stock_code='10', top=5)
            print(f"   Records received: {len(inventory)}")
            if inventory:
                print(f"   Sample record: {inventory[0]}")
            else:
                print("   No inventory records received")
        except Exception as e:
            print(f"   Inventory API error: {e}")
        
        # 5. Test alternative stock codes
        print("\n5. Alternative Stock Codes Test:")
        try:
            api_service = TadbirAPIService()
            token = api_service.authenticate()
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Test stock codes that might have data
            stock_codes = ['15', '20', '30', '35', '40', '50']
            for stock_code in stock_codes:
                try:
                    url = f'{api_service.base_url}/odata/GeneralDescs/Tadbir.GetRem(stock=\'{stock_code}\')'
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        records = data.get('value', [])
                        print(f"   Stock {stock_code}: {len(records)} records")
                        if records:
                            print(f"     Sample: {records[0]}")
                except:
                    pass
        except Exception as e:
            print(f"   Alternative stock test error: {e}")
        
        # 6. Recommendations
        print("\n6. Recommendations:")
        print("   - Check if stock code 10 is active in Tadbir")
        print("   - Check if inventory exists in Tadbir system")
        print("   - Consider using alternative stock code if available")
        print("   - Contact Tadbir system administrator")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    run_simple_diagnostic()

