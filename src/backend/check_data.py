import requests, json

BASE = 'http://localhost:8003/api'
r = requests.post(f'{BASE}/auth/login', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

checks = [
    ('subjects', f'{BASE}/subjects'),
    ('questions', f'{BASE}/questions?page=1&page_size=3'),
    ('exams', f'{BASE}/exams?page=1&page_size=3'),
    ('users', f'{BASE}/users?page=1&page_size=3'),
    ('announcements', f'{BASE}/announcements'),
    ('analytics', f'{BASE}/analytics/overview'),
    ('certificates', f'{BASE}/certificates'),
    ('videos', f'{BASE}/videos'),
    ('resources', f'{BASE}/resources'),
]

for name, url in checks:
    try:
        r = requests.get(url, headers=headers)
        d = r.json()
        if isinstance(d, list):
            print(f'{name}: list of {len(d)} items')
        elif isinstance(d, dict):
            if 'total' in d:
                print(f'{name}: {d["total"]} items')
            elif 'data' in d:
                data = d['data']
                if isinstance(data, list):
                    print(f'{name}: {len(data)} items')
                elif isinstance(data, dict) and 'total' in data:
                    print(f'{name}: {data["total"]} items')
                else:
                    print(f'{name}: data={type(data).__name__}')
            else:
                keys = list(d.keys())[:5]
                print(f'{name}: dict keys={keys}')
        else:
            print(f'{name}: {type(d).__name__}')
    except Exception as e:
        print(f'{name}: ERROR - {e}')
