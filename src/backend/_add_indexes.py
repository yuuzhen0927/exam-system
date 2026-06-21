import sqlite3
conn = sqlite3.connect(r'F:\CodexWorkspace\Project004_考试系统\src\backend\exam.db')
c = conn.cursor()

indexes = [
    ("ix_exams_is_published", "exams", "is_published"),
    ("ix_exams_mode", "exams", "mode"),
    ("ix_announcements_is_pinned", "announcements", "is_pinned"),
    ("ix_announcements_is_published", "announcements", "is_published"),
    ("ix_certificates_issue_rule", "certificates", "issue_rule"),
    ("ix_questions_type", "questions", "type"),
    ("ix_questions_is_active", "questions", "is_active"),
    ("ix_practice_records_created_at", "practice_records", "created_at"),
    ("ix_practice_records_subject_id", "practice_records", "subject_id"),
    ("ix_exam_results_status", "exam_results", "status"),
    ("ix_wrong_answers_is_mastered", "wrong_answers", "is_mastered"),
    ("ix_favorites_created_at", "favorites", "created_at"),
]

for name, table, col in indexes:
    try:
        c.execute(f'CREATE INDEX IF NOT EXISTS {name} ON "{table}" ("{col}")')
        print(f"OK: {name}")
    except Exception as e:
        print(f"SKIP: {name} - {e}")

conn.commit()
conn.close()
print("Done")
