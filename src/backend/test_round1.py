import requests, json, sys

BASE = 'http://localhost:8003/api'
results = []

# Test auth
try:
    login = requests.post(f'{BASE}/auth/login', json={'username':'admin','password':'admin123'}, timeout=5)
    print(f'LOGIN: {login.status_code}')
    data = login.json()
    token = data.get('data',{}).get('token','') or data.get('token','')
    results.append(('POST', '/auth/login', login.status_code, 'PASS' if login.status_code==200 else 'FAIL'))
except Exception as e:
    print(f'LOGIN ERROR: {e}')
    sys.exit(1)

headers = {'Authorization': f'Bearer {token}'}

endpoints = [
    ('GET', '/subjects'),
    ('GET', '/questions?page=1&page_size=5'),
    ('GET', '/exams?page=1&page_size=5'),
    ('GET', '/exams/my-results'),
    ('GET', '/practice/stats'),
    ('GET', '/wrongbook'),
    ('GET', '/favorites'),
    ('GET', '/notes'),
    ('GET', '/certificates'),
    ('GET', '/certificates/practice-eligibility'),
    ('GET', '/videos'),
    ('GET', '/resources'),
    ('GET', '/announcements'),
    ('GET', '/analytics/overview'),
    ('GET', '/users'),
    ('GET', '/feedback'),
    ('GET', '/abnormal'),
    ('GET', '/profile'),
    ('GET', '/roles'),
]

for method, path in endpoints:
    try:
        r = requests.get(f'{BASE}{path}', headers=headers, timeout=5)
        status = r.status_code
        ok = 'PASS' if status < 400 else 'FAIL'
        results.append((method, path, status, ok))
    except Exception as e:
        results.append((method, path, 0, f'ERROR:{e}'))

# Print summary
passed = sum(1 for r in results if r[3]=='PASS')
failed = sum(1 for r in results if r[3]!='PASS')
print(f'\n=== Round 1 Results: {passed}/{len(results)} passed ===')
for m, p, s, ok in results:
    flag = 'OK' if ok=='PASS' else 'XX'
    print(f'  [{flag}] {m} {p} -> {s}')
print(f'\nPASS: {passed}, FAIL: {failed}')
