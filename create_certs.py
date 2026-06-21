"""Create practice certificates for all subjects"""
import sqlite3

db = sqlite3.connect(r'F:\CodexWorkspace\Project004_考试系统\src\backend\exam.db')
cur = db.cursor()

# Get existing practice certs
cur.execute('SELECT id, chapter_id FROM certificates WHERE cert_type="practice"')
existing = {r[1] for r in cur.fetchall()}
print(f'Existing practice cert chapter_ids: {existing}')

# Get all chapters grouped by subject
cur.execute('SELECT id, name, subject_id FROM chapters ORDER BY subject_id, id')
chapters = cur.fetchall()

# Group by subject
from collections import defaultdict
subject_chapters = defaultdict(list)
for ch_id, ch_name, subj_id in chapters:
    subject_chapters[subj_id].append((ch_id, ch_name))

# Get subject names
cur.execute('SELECT id, name FROM subjects')
subject_names = {r[0]: r[1] for r in cur.fetchall()}

# Create one practice cert per subject (linked to first chapter of that subject)
created = 0
for subj_id, chs in sorted(subject_chapters.items()):
    first_ch_id = chs[0][0]
    if first_ch_id in existing:
        print(f'Subject {subj_id} ({subject_names.get(subj_id, "")}): already has cert for chapter {first_ch_id}')
        continue
    
    subj_name = subject_names.get(subj_id, f'Subject {subj_id}')
    cert_name = f'{subj_name}练习合格证'
    desc = f'完成{subj_name}相关章节练习，正确率达到60%即可申请'
    
    cur.execute(
        'INSERT INTO certificates (name, description, cert_type, chapter_id) VALUES (?, ?, ?, ?)',
        (cert_name, desc, 'practice', first_ch_id)
    )
    created += 1
    print(f'Created: {cert_name} (chapter_id={first_ch_id})')

db.commit()
print(f'\nTotal created: {created}')

# Verify all certs
cur.execute('SELECT id, name, cert_type, chapter_id FROM certificates')
print('\nAll certificates:')
for r in cur.fetchall():
    print(f'  id={r[0]} type={r[2]} chapter_id={r[3]} name={r[1]}')

db.close()
