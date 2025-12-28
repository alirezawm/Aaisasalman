import os, requests
base = os.getenv('TADBIR_API_URL') or 'http://5.202.90.240:8085'
candidates = [
    '/api/mobile/v1/products',
    '/api/products',
    '/api/v1/products',
    '/api/mobile/products',
    '/products',
    '/api/mobile/v1/products/search',
    '/api/mobile/v1/Products',
]
for c in candidates:
    url = base + c
    try:
        r = requests.get(url, timeout=10)
        print(c, r.status_code)
        if r.status_code == 200:
            print('sample:', r.text[:400])
    except Exception as e:
        print(c, 'error', e)
