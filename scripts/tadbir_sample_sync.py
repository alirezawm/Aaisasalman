#!/usr/bin/env python3
"""Simple Tadbir sample sync script.
Fetches up to 50 products from the Tadbir API (reads TADBIR_API_URL, TADBIR_USERNAME, TADBIR_PASSWORD from .env)
Saves newline-delimited JSON to release/data/tadbir_sample.jsonl
"""
import os
import sys
import time
import json
import re
from pathlib import Path

try:
    import requests
except Exception:
    print("Please install 'requests' (pip install requests) and re-run.")
    sys.exit(1)


def load_env(env_path: Path = Path('.env')):
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})


def parse_price(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value)
    # remove non-numeric except decimal separator and minus
    s = s.replace('\u200f', '')  # remove RTL mark if present
    s = s.replace(',', '')
    m = re.search(r"([0-9]+(\.[0-9]+)?)", s.replace('\u066B','.') )
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None


def normalize_product(raw):
    p = {}
    p['product_id'] = raw.get('id') or raw.get('item_code') or raw.get('tadbir_guid')
    p['title'] = raw.get('name') or raw.get('title') or raw.get('description')[:80] if raw.get('description') else ''
    p['url'] = raw.get('url') or ''
    p['images'] = raw.get('images') or raw.get('image_urls') or []
    # Tadbir often stores multiple price fields; normalize them
    prices = []
    # Known keys
    mapping = [
        ('retail_price_cash', 'cash'),
        ('retail_price_check', 'check'),
        ('bulk_price_cash', 'bulk_cash'),
        ('bulk_price_check', 'bulk_check'),
    ]
    for key, name in mapping:
        if key in raw and raw[key] is not None:
            val = parse_price(raw[key])
            prices.append({'price_type': name, 'price_value': val, 'price_raw': raw[key]})
    # fallback to any price fields in nested structures
    if not prices and raw.get('price') is not None:
        val = parse_price(raw.get('price'))
        prices.append({'price_type': 'default', 'price_value': val, 'price_raw': raw.get('price')})
    p['prices'] = prices
    p['categories'] = raw.get('categories') or []
    p['inventory'] = {
        'available_quantity': raw.get('available_quantity') or raw.get('stock') or None,
        'stock_code': raw.get('stock_code') or None,
    }
    p['scraped_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    p['source'] = os.getenv('TADBIR_API_URL') or ''
    p['raw'] = raw
    return p


def main():
    load_env()
    base = os.getenv('TADBIR_API_URL')
    if not base:
        print('TADBIR_API_URL not set in environment or .env')
        sys.exit(1)
    if base.endswith('/'):
        base = base[:-1]
    user = os.getenv('TADBIR_USERNAME')
    pwd = os.getenv('TADBIR_PASSWORD')
    auth = (user, pwd) if user and pwd else None

    headers = {'User-Agent': 'asiasalman-tadbir-sample/1.0'}

    out_dir = Path('release/data')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'tadbir_sample.jsonl'

    per_page = 50
    page = 1
    fetched = 0

    url = f"{base}/api/mobile/v1/products"
    params = {'page': page, 'per_page': per_page}
    print(f'Fetching products list: {url} params={params}')
    try:
        r = requests.get(url, params=params, headers=headers, auth=auth, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print('Failed to fetch products list:', str(e))
        sys.exit(1)

    data = r.json()
    products = data.get('products') if isinstance(data, dict) and 'products' in data else data
    if not isinstance(products, list):
        print('Unexpected products payload format; showing sample:')
        print(json.dumps(data, indent=2)[:2000])
        sys.exit(1)

    print(f'Got {len(products)} products from list. Normalizing and saving...')

    max_detail = 10
    saved = 0
    with out_file.open('w', encoding='utf-8') as fh:
        for i, raw in enumerate(products):
            norm = normalize_product(raw)
            fh.write(json.dumps(norm, ensure_ascii=False) + '\n')
            saved += 1
            fetched += 1
            # optionally fetch detail for first few
            if i < max_detail and norm.get('product_id'):
                pid = norm['product_id']
                detail_url = f"{base}/api/mobile/v1/products/{pid}"
                try:
                    rd = requests.get(detail_url, headers=headers, auth=auth, timeout=30)
                    if rd.ok:
                        detail = rd.json()
                        nd = normalize_product(detail if isinstance(detail, dict) else detail)
                        fh.write(json.dumps({'detail_of': pid, 'detail': nd}, ensure_ascii=False) + '\n')
                        time.sleep(0.4)
                except Exception as e:
                    print('detail fetch failed for', pid, str(e))
            time.sleep(0.02)  # light throttle

    print(f'Done. Saved {saved} product records to {out_file.resolve()}')

    # print 3 sample records
    print('\nSample records (first 3):')
    with out_file.open('r', encoding='utf-8') as fh:
        for i, line in enumerate(fh):
            if i >= 3:
                break
            try:
                js = json.loads(line)
                print(json.dumps(js if isinstance(js, dict) else js, ensure_ascii=False)[:1000])
            except Exception:
                print(line[:400])


if __name__ == '__main__':
    main()
