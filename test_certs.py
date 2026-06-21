"""Test certificates API"""
import requests, json

# Login as zhangsan (OAuth2 form data)
r = requests.post('http://localhost:8003/api/auth/login', data={'username': 'zhangsan', 'password': '123456'})
if r.status_code != 200:
    print('Login failed:', r.status_code, r.text)
else:
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test practice-eligibility
    r2 = requests.get('http://localhost:8003/api/certificates/practice-eligibility', headers=headers)
    print('Eligibility status:', r2.status_code)
    if r2.status_code == 200:
        data = r2.json()
        print(f'Found {len(data)} eligible certificates')
        for item in data:
            name = item.get('certificate_name', '')
            rate = item.get('pass_rate', 0)
            issued = item.get('already_issued', False)
            total = item.get('total_questions', 0)
            correct = item.get('correct_questions', 0)
            subj = item.get('subject_name', '')
            ch = item.get('chapter_name', '')
            print(f'  [{subj}] {name} ({ch}): {correct}/{total} = {rate}% issued={issued}')
    else:
        print('Error:', r2.text[:500])
    
    # Test my certs
    r3 = requests.get('http://localhost:8003/api/certificates/my', headers=headers)
    print(f'\nMy certs status: {r3.status_code}')
    if r3.status_code == 200:
        my = r3.json()
        print(f'Found {len(my)} certificates')
        for c in my:
            print(f'  {c.get("certificate_name", "")} - {c.get("certificate_no", "")}')
