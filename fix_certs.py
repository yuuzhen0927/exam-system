"""Fix certificates_router.py - add missing imports and fix eligibility logic"""
import re

path = r'F:\CodexWorkspace\Project004_考试系统\src\backend\routers\certificates_router.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Update import line
content = content.replace(
    "from models import Certificate, UserCertificate, ExamResult, User",
    "from models import Certificate, UserCertificate, ExamResult, Exam, User, PracticeRecord, Chapter, Subject"
)

# Fix 2: Replace apply_for_cert practice check
old1 = '''    if cert.cert_type == "practice" and cert.chapter_id:
        from models import PracticeRecord
        records = db.query(PracticeRecord).filter(
            PracticeRecord.user_id == user.id,
            PracticeRecord.chapter_id == cert.chapter_id
        ).all()
        if not records:
            raise HTTPException(400, "No practice records for this chapter")
        total_q = sum(r.total_count or 0 for r in records)
        correct_q = sum(r.correct_count or 0 for r in records)
        if total_q < 10:
            raise HTTPException(400, "At least 10 practice questions required")
        rate = correct_q / total_q * 100 if total_q > 0 else 0
        if rate < 60:
            raise HTTPException(400, f"Pass rate {rate:.1f}% below 60%")'''

new1 = '''    if cert.cert_type == "practice":
        # Try chapter-level match first, then fall back to subject-level
        records = []
        if cert.chapter_id:
            records = db.query(PracticeRecord).filter(
                PracticeRecord.user_id == user.id,
                PracticeRecord.chapter_id == cert.chapter_id
            ).all()
        # Fallback: match by subject (chapter records often have chapter_id=None)
        if not records:
            chapter = db.query(Chapter).get(cert.chapter_id) if cert.chapter_id else None
            if chapter:
                records = db.query(PracticeRecord).filter(
                    PracticeRecord.user_id == user.id,
                    PracticeRecord.subject_id == chapter.subject_id
                ).all()
        if not records:
            raise HTTPException(400, "\u8be5\u79d1\u76ee\u6682\u65e0\u7ec3\u4e60\u8bb0\u5f55\uff0c\u8bf7\u5148\u5b8c\u6210\u7ec3\u4e60")
        total_q = sum(r.total_count or 0 for r in records)
        correct_q = sum(r.correct_count or 0 for r in records)
        if total_q < 10:
            raise HTTPException(400, "\u7ec3\u4e60\u9898\u6570\u4e0d\u8db310\u9053\uff0c\u8bf7\u7ee7\u7eed\u7ec3\u4e60")
        rate = correct_q / total_q * 100 if total_q > 0 else 0
        if rate < 60:
            raise HTTPException(400, f"\u6b63\u786e\u7387 {rate:.1f}% \u672a\u8fbe\u523060%\u7533\u8bf7\u6807\u51c6\uff0c\u8bf7\u7ee7\u7eed\u7ec3\u4e60")'''

if old1 in content:
    content = content.replace(old1, new1)
    print('Fixed apply_for_cert practice check')
else:
    print('ERROR: Could not find old apply_for_cert practice check')

# Fix 3: Replace practice-eligibility check
old2 = '''        # Count practice records for this chapter
        from models import PracticeRecord, Chapter, Subject
        records = db.query(PracticeRecord).filter(
            PracticeRecord.user_id == user.id,
            PracticeRecord.chapter_id == cert.chapter_id
        ).all()
        
        if not records:
            continue'''

new2 = '''        # Count practice records for this chapter (fallback to subject-level)
        records = db.query(PracticeRecord).filter(
            PracticeRecord.user_id == user.id,
            PracticeRecord.chapter_id == cert.chapter_id
        ).all()
        # Fallback: match by subject since many records have chapter_id=None
        if not records and cert.chapter_id:
            chapter_fb = db.query(Chapter).get(cert.chapter_id)
            if chapter_fb:
                records = db.query(PracticeRecord).filter(
                    PracticeRecord.user_id == user.id,
                    PracticeRecord.subject_id == chapter_fb.subject_id
                ).all()
        
        if not records:
            continue'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Fixed practice-eligibility check')
else:
    print('ERROR: Could not find old practice-eligibility check')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved')
