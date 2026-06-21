import sqlite3
conn = sqlite3.connect(r'F:\CodexWorkspace\Project004_考试系统\src\backend\exam.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print(f"Tables: {len(tables)}")
for t in tables:
    c.execute(f'PRAGMA index_list("{t}")')
    idx = c.fetchall()
    c.execute(f'PRAGMA table_info("{t}")')
    cols = [r[1] for r in c.fetchall()]
    c.execute(f'SELECT COUNT(*) FROM "{t}"')
    count = c.fetchone()[0]
    print(f"  {t}: {count} rows, {len(idx)} indexes, cols: {', '.join(cols[:5])}...")
    for i in idx:
        print(f"    idx: {i[1]} (unique={i[2]})")
conn.close()
