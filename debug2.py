import sqlite3
db = sqlite3.connect(r'F:\CodexWorkspace\Project004_考试系统\src\backend\exam.db')
cur = db.cursor()
cur.execute('SELECT c.id, c.name, c.chapter_id, ch.name, ch.subject_id FROM certificates c LEFT JOIN chapters ch ON c.chapter_id=ch.id WHERE c.cert_type="practice"')
for r in cur.fetchall():
    print(f'cert_id={r[0]} cert={r[1]} chapter_id={r[2]} chapter={r[3]} subj_id={r[4]}')
db.close()
