"""Quick API test for key endpoints"""
import requests

BASE = "http://localhost:8003"
results = {"pass": 0, "fail": 0}

r = requests.post(f"{BASE}/api/auth/login", data={"username": "admin", "password": "admin123"})
if r.status_code != 200:
    print(f"Login FAIL: {r.status_code} {r.text[:200]}")
    exit(1)
token = r.json()["access_token"]
print("Login OK")

h = {"Authorization": f"Bearer {token}"}

# Login as student
r2 = requests.post(f"{BASE}/api/auth/login", data={"username": "zhangsan", "password": "123456"})
if r2.status_code == 200:
    student_token = r2.json()["access_token"]
    print("Student login OK")
else:
    student_token = None
    print(f"Student login FAIL: {r2.status_code}")

# Admin tests
admin_tests = [
    ("GET", "/api/subjects"),
    ("GET", "/api/questions?page=1&page_size=3"),
    ("GET", "/api/exams?page=1&page_size=3"),
    ("GET", "/api/users"),
    ("GET", "/api/roles"),
    ("GET", "/api/announcements"),
    ("GET", "/api/resources"),
    ("GET", "/api/video-courses"),
    ("GET", "/api/certificates/all"),
    ("GET", "/api/analytics/overview"),
    ("GET", "/api/retake-applications"),
    ("GET", "/api/abnormal-reports"),
    ("GET", "/api/question-feedbacks"),
    ("GET", "/api/exams/results?page=1&page_size=3"),
]

print("\n--- Admin APIs ---")
for method, path in admin_tests:
    r = requests.request(method, f"{BASE}{path}", headers=h)
    ok = str(r.status_code).startswith("2")
    results["pass" if ok else "fail"] += 1
    tag = "PASS" if ok else "FAIL"
    detail = str(r.json())[:80] if ok else r.text[:80]
    print(f"  {tag} [{r.status_code}] {path} -> {detail}")

# Student tests
print("\n--- Student APIs ---")
student_tests = [
    ("GET", "/api/subjects"),
    ("GET", "/api/questions?page=1&page_size=3"),
    ("GET", "/api/exams?page=1&page_size=3"),
    ("GET", "/api/exams/my-results"),
    ("GET", "/api/practice/records"),
    ("GET", "/api/wrongbook"),
    ("GET", "/api/favorites"),
    ("GET", "/api/notes"),
    ("GET", "/api/resources"),
    ("GET", "/api/video-courses"),
    ("GET", "/api/certificates"),
    ("GET", "/api/announcements"),
]
sh = {"Authorization": f"Bearer {student_token}"}
for method, path in student_tests:
    r = requests.request(method, f"{BASE}{path}", headers=sh)
    ok = str(r.status_code).startswith("2")
    results["pass" if ok else "fail"] += 1
    tag = "PASS" if ok else "FAIL"
    detail = str(r.json())[:80] if ok else r.text[:80]
    print(f"  {tag} [{r.status_code}] {path} -> {detail}")

print(f"\n===== {results['pass']} PASS, {results['fail']} FAIL =====")
