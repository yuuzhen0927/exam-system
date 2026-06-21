import requests

# Login as admin (uses OAuth2PasswordRequestForm)
r = requests.post('http://localhost:8003/api/auth/login', data={'username':'admin','password':'admin123'})
if r.ok:
    data = r.json()
    token = data['access_token']
    print('Login OK')
    h = {'Authorization': f'Bearer {token}'}
    
    r2 = requests.get('http://localhost:8003/api/subjects', headers=h)
    print(f'Subjects: {r2.status_code} - {len(r2.json())} items')
    
    r3 = requests.get('http://localhost:8003/api/questions?page_size=5', headers=h)
    qdata = r3.json()
    print(f'Questions: {r3.status_code} - total {qdata.get("total","?")}')
    
    r4 = requests.get('http://localhost:8003/api/exams?page_size=5', headers=h)
    edata = r4.json()
    print(f'Exams: {r4.status_code} - total {edata.get("total","?")}')
    
    r5 = requests.get('http://localhost:8003/api/users?page_size=5', headers=h)
    print(f'Users: {r5.status_code}')
    
    r6 = requests.get('http://localhost:8003/api/analytics/overview', headers=h)
    print(f'Analytics: {r6.status_code}')
else:
    print('Login failed:', r.status_code, r.text[:200])
