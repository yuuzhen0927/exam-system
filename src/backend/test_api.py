# -*- coding: utf-8 -*-
import urllib.request, json, urllib.parse

# Login with form data
login_data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8003/api/auth/login', data=login_data)
resp = urllib.request.urlopen(req)
token = json.loads(resp.read())['access_token']

# Get subjects with auth
req = urllib.request.Request('http://localhost:8003/api/subjects', headers={'Authorization': f'Bearer {token}'})
resp = urllib.request.urlopen(req)
subjects = json.loads(resp.read())

print('=== Subjects from API ===')
for s in subjects:
    print(f"  {s['id']}: {s['name']}")

# Get questions
req = urllib.request.Request('http://localhost:8003/api/questions?limit=3', headers={'Authorization': f'Bearer {token}'})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
questions = data if isinstance(data, list) else data.get('items', data.get('questions', []))

print('\n=== Questions from API ===')
for q in questions[:3]:
    print(f"  Content: {q.get('content', q.get('question_text', ''))[:60]}")
    print(f"  Answer: {q.get('answer', '')}")
