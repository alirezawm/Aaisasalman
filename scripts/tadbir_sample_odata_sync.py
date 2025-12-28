#!/usr/bin/env python3
"""Sample Tadbir OData sync using /token and /odata endpoints.
Fetches up to 50 items from /odata/GeneralDescs and saves newline-delimited JSON to release/data/tadbir_sample_odata.jsonl
"""
import os, sys, json, time, re
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
    s = s.replace('\u200f', '')
    s = s.replace(',', '')
    m = re.search(r"([0-9]+(\.[0-9]+)?)", s.replace('\u066B', '.'))
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None


def normalize_product_odata(raw):
    p = {}
    p['product_id'] = raw.get('TADDIR_ID') or raw.get('Id') or raw.get('Itemcode') or raw.get('id')
    p['title'] = raw.get('Name') or raw.get('FullName') or raw.get('Descr') or raw.get('name') or ''
    p['url'] = ''
    # images unlikely in OData so keep empty
    p['images'] = []
    # prices: try common fields
    prices = []
    for key in ['Price', 'RetailPrice', 'SalePrice', 'Price1', 'Price2']:
        if key in raw and raw[key] is not None:
            val = parse_price(raw[key])
            prices.append({'price_type': key.lower(), 'price_value': val, 'price_raw': raw[key]})
    p['prices'] = prices
    p['categories'] = [raw.get('Group1'), raw.get('Group2')] if raw.get('Group1') or raw.get('Group2') else []
    p['inventory'] = {'available_quantity': raw.get('Rem') or raw.get('Stock') or None}
    p['scraped_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    p['source'] = os.getenv('TADBIR_API_URL') or ''
    p['raw'] = raw
    return p


def get_token(base, username, password, timeout=15):
    url = base.rstrip('/') + '/token'
    data = {'grant_type': 'password', 'username': username, 'password': password}
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    r = requests.post(url, data=data, headers=headers, timeout=timeout)
    r.raise_for_status()
    try:
        js = r.json()
        token = js.get('access_token') or js.get('token')
        return token or js
    except Exception:
        return r.text.strip()


def main():
    load_env()
    base = os.getenv('TADBIR_API_URL')
    if not base:
        print('TADBIR_API_URL not set')
        sys.exit(1)
    user = os.getenv('TADBIR_USERNAME')
    pwd = os.getenv('TADBIR_PASSWORD')

    token = None
    if user and pwd:
        try:
            token = get_token(base, user, pwd)
            print('Got token (length):', len(token) if isinstance(token, str) else 'obj')
        except Exception as e:
            print('Token fetch failed:', e)

    headers = {'Accept': 'application/json'}
    if token and isinstance(token, str):
        headers['Authorization'] = f'Bearer {token}'

    params = {'$top': 50}
    url = base.rstrip('/') + '/odata/GeneralDescs'
    print('Fetching OData GeneralDescs:', url, params)
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    products = data.get('value', []) if isinstance(data, dict) else data
    if not isinstance(products, list):
        print('Unexpected payload; preview:', json.dumps(data, ensure_ascii=False)[:2000])
        sys.exit(1)

    out_dir = Path('release/data')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'tadbir_sample_odata.jsonl'
    saved = 0
    with out_file.open('w', encoding='utf-8') as fh:
        for raw in products:
            norm = normalize_product_odata(raw if isinstance(raw, dict) else {})
            fh.write(json.dumps(norm, ensure_ascii=False) + '\n')
            saved += 1

    print('Saved', saved, 'records to', out_file.resolve())
    print('\nSample (first 3):')
    with out_file.open('r', encoding='utf-8') as fh:
        for i, line in enumerate(fh):
            if i >= 3:
                break
            print(line[:1000])


if __name__ == '__main__':
    main()
