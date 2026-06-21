import requests, sys
B = "http://localhost:8003"

def t(n, m, p, d=None):
    try:
        r = requests.request(m, B+p, headers=h, json=d, timeout=10)
        ok = 200 <= r.status_code < 300
        print(f"  {'PASS' if ok else 'FAIL'} [{r.status_code}] {n}")
        if not ok: print(f"    {r.text[:150]}")
    except Exception as e:
        print(f"  FAIL [ERR] {n}: {e}")

r = requests.post(f"{B}/api/auth/login", data={"username":"admin","password":"admin123"}, timeout=10)
if r.status_code != 200:
    print(f"Login FAIL: {r.status_code}")
    sys.exit(1)
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}
print(f"Admin login OK")

r2 = requests.post(f"{B}/api/auth/login", data={"username":"zhangsan","password":"123456"}, timeout=10)
st = r2.json()["access_token"] if r2.status_code == 200 else None
sh = {"Authorization": f"Bearer {st}"} if st else None
print(f"Student login {'OK' if st else 'FAIL'}")

print("\n--- Admin ---")
t("subjects","GET","/api/subjects")
t("questions","GET","/api/questions?page_size=3")
t("exams","GET","/api/exams?page_size=3")
t("users","GET","/api/users")
t("roles","GET","/api/roles")
t("announcements","GET","/api/announcements")
t("resources","GET","/api/resources")
t("videos","GET","/api/video-courses")
t("certificates","GET","/api/certificates/all")
t("analytics","GET","/api/analytics/overview")
t("retake","GET","/api/retake-applications")
t("abnormal","GET","/api/abnormal-reports")
t("feedbacks","GET","/api/question-feedbacks")
t("exam_results","GET","/api/exams/results?page_size=3")

print("\n--- Student ---")
t("s_subjects","GET","/api/subjects")
t("s_questions","GET","/api/questions?page_size=3")
t("s_exams","GET","/api/exams?page_size=3")
t("s_results","GET","/api/exams/my-results")
t("s_practice","GET","/api/practice/records")
t("s_wrongbook","GET","/api/wrongbook")
t("s_favorites","GET","/api/favorites")
t("s_notes","GET","/api/notes")
t("s_resources","GET","/api/resources")
t("s_videos","GET","/api/video-courses")
t("s_certs","GET","/api/certificates")
t("s_announcements","GET","/api/announcements")

print("\nDone.")
