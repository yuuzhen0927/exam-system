"""Debug certificates eligibility"""
import requests, json
import sqlite3

# Check DB directly
db = sqlite3.connect(r'F:\CodexWorkspace\Project004_考试系统\src\backend\exam.db')
cur = db.cursor()

# Practice certs
cur.execute('SELECT id, name, cert_type, chapter_id FROM certificates WHERE cert_type = "practice"')
practice_certs = cur.fetchall()
print('Practice certificates:')
for c in practice_certs:
    print(f'  id={c[0]} name={c[1]} chapter_id={c[2]}')

# Chapters
cur.execute('SELECT id, name, subject_id FROM chapters')
chapters = cur.fetchall()
print(f'\nChapters ({len(chapters)}):')
for ch in chapters[:10]:
    print(f'  id={ch[0]} name={ch[1]} subject_id={ch[2]}')

# Practice records for zhangsan (user_id=2)
cur.execute('SELECT id, subject_id, chapter_id, total_count, correct_count FROM practice_records WHERE user_id = 2')
records = cur.fetchall()
print(f'\nZhangsan practice records ({len(records)}):')
for r in records:
    print(f'  id={r[0]} subject_id={r[1]} chapter_id={r[2]} total={r[3]} correct={r[4]}')

# Aggregate by subject
from collections import defaultdict
subject_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'count': 0})
for r in records:
    sid = r[1]
    if sid:
        subject_stats[sid]['total'] += r[3] or 0
        subject_stats[sid]['correct'] += r[4] or 0
        subject_stats[sid]['count'] += 1

print('\nSubject-level stats:')
for sid, stats in subject_stats.items():
    rate = round(stats['correct'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
    print(f'  subject_id={sid}: {stats["correct"]}/{stats["total"]} = {rate}% ({stats["count"]} records)')

db.close()
