import os, requests
base = os.getenv('TADBIR_API_URL') or 'http://5.202.90.240:8085'
print('base:', base)
try:
    r = requests.get(base, timeout=10)
    print('status', r.status_code)
    print('headers:', r.headers.get('content-type'))
    print('body sample:\n', r.text[:2000])
except Exception as e:
    print('error', e)
