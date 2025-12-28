"""Fetch a small sample of products and prices from Tadbir API and save as JSONL.

Usage: python scripts/tadbir_fetch_sample.py
"""
import os
import json
from datetime import datetime
from tadbir_api_service import TadbirAPIService

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'release', 'data')
os.makedirs(OUT_DIR, exist_ok=True)

PRODUCTS_FILE = os.path.join(OUT_DIR, 'tadbir_products_sample.jsonl')
PRICES_FILE = os.path.join(OUT_DIR, 'tadbir_prices_sample.jsonl')


def save_jsonl(path, items):
    with open(path, 'w', encoding='utf-8') as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')


def main():
    api = TadbirAPIService()

    print('Testing Tadbir API connection...')
    try:
        status = api.test_connection()
        print('Connection status:', status)
    except Exception as e:
        print('Connection test failed:', str(e))
        return

    # Fetch a small sample of products
    try:
        print('Fetching products (top=50)...')
        products = api.get_products(top=50)
        print(f'Fetched {len(products)} products')
        save_jsonl(PRODUCTS_FILE, products)
    except Exception as e:
        print('Failed to fetch products:', str(e))
        products = []

    # Fetch prices for a couple of price lists (13 and 14)
    prices = []
    for key in (13, 14):
        try:
            print(f'Fetching prices for price_list_key={key} (top=200)...')
            batch = api.get_prices(price_list_key=key, top=200)
            print(f'  Retrieved {len(batch)} prices for key {key}')
            prices.extend(batch)
        except Exception as e:
            print(f'Failed to fetch prices for key {key}:', str(e))

    if prices:
        save_jsonl(PRICES_FILE, prices)
        print(f'Saved {len(prices)} price records to {PRICES_FILE}')

    # Print a couple of sample entries
    print('\n--- Sample products (up to 3) ---')
    for p in products[:3]:
        print(json.dumps(p, ensure_ascii=False, indent=2)[:1000])

    print('\n--- Sample prices (up to 3) ---')
    for p in prices[:3]:
        print(json.dumps(p, ensure_ascii=False, indent=2)[:1000])

    print(f"\nOutputs written to: {PRODUCTS_FILE} and {PRICES_FILE}")


if __name__ == '__main__':
    main()
