# -*- coding: utf-8 -*-
"""Fix main.py to only seed admin user, not English data"""
import re

with open('F:/CodexWorkspace/Project004_考试系统/src/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'def _seed_defaults\(\):.*?finally:\s*db\.close\(\)'

replacement = """def _seed_defaults():
    from database import SessionLocal
    from models import User, Role
    from auth import hash_password

    db = SessionLocal()
    try:
        # Only seed admin user and basic roles - Chinese data comes from seed_cn.py
        if db.query(Role).count() == 0:
            db.add(Role(name="admin", description="System Admin", is_manager=True, is_system=True, sort_order=1))
            db.add(Role(name="teacher", description="Teacher/Manager", is_manager=True, is_system=True, sort_order=2))
            db.add(Role(name="student", description="Student", is_manager=False, is_system=True, sort_order=9))
            db.commit()

        if db.query(User).count() == 0:
            db.add(User(
                username="admin",
                hashed_password=hash_password("admin123"),
                fullname="System Admin",
                role="admin",
            ))
            db.commit()
    finally:
        db.close()"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('F:/CodexWorkspace/Project004_考试系统/src/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("main.py updated - only creates admin user and roles")
