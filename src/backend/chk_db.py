import sqlite3
conn = sqlite3.connect(r'F:\CodexWorkspace\Project004_考试系统\src\backend\exam.db')
c = conn.cursor()
tables = [
    'subjects','chapters','questions','exams','exam_results','users',
    'certificates','user_certificates','practice_records','wrong_answers',
    'favorites','notes','announcements','video_courses','resources',
    'abnormal_reports','question_feedbacks','operation_logs','video_progress',
    'retake_applications','roles','notifications','exam_templates','question_versions'
]
for t in tables:
    try:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t}: {c.fetchone()[0]} rows")
    except Exception as e:
        print(f"  {t}: MISSING - {e}")
conn.close()
