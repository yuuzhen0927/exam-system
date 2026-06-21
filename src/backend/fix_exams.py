import re

path = r"F:\CodexWorkspace\Project004_考试系统\src\backend\routers\exams_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the malformed auto-issue block (line 361 - all on one line)
old = '# Auto-issue certificate for formal exam passed without composite    if e.mode == "formal" and not has_composite and result.passed:        from models import Certificate, UserCertificate        import uuid        cert = db.query(Certificate).filter(Certificate.cert_type == "exam").first()        if cert:            already = db.query(UserCertificate).filter(                UserCertificate.certificate_id == cert.id,                UserCertificate.user_id == user.id,                UserCertificate.is_revoked == False            ).first()            if not already:                uc = UserCertificate(                    certificate_id=cert.id, user_id=user.id,                    exam_result_id=result.id,                    certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}"                )                db.add(uc)                db.commit()'

new = '''    # Auto-issue certificate for formal exams passed without composite questions
    if e.mode == "formal" and not has_composite and result.passed:
        cert = db.query(Certificate).filter(Certificate.cert_type == "exam").first()
        if cert:
            already = db.query(UserCertificate).filter(
                UserCertificate.certificate_id == cert.id,
                UserCertificate.user_id == user.id,
                UserCertificate.is_revoked == False
            ).first()
            if not already:
                import uuid
                uc = UserCertificate(
                    certificate_id=cert.id, user_id=user.id,
                    exam_result_id=result.id,
                    certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}"
                )
                db.add(uc)
                db.commit()'''

content = content.replace(old, new)

# Also add the Certificate import at the top of the file
# Insert after the last existing import
import_line = 'from models import '
if 'from models import Certificate' not in content:
    content = content.replace(
        'from models import Exam, ExamTemplate, ExamResult, Question',
        'from models import Exam, ExamTemplate, ExamResult, Question, Certificate, UserCertificate'
    )

# Add apply-certificate endpoint before the report-tab-switch route
apply_endpoint = '''
@router.post("/apply-certificate")
def apply_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Client applies for a certificate - system checks eligibility"""
    cert = db.query(Certificate).get(certificate_id)
    if not cert:
        raise HTTPException(404, "证书不存在")

    # Check already issued
    already = db.query(UserCertificate).filter(
        UserCertificate.certificate_id == certificate_id,
        UserCertificate.user_id == user.id,
        UserCertificate.is_revoked == False
    ).first()
    if already:
        return {"ok": True, "message": "已拥有此证书", "certificate_no": already.certificate_no}

    if cert.cert_type == "practice" and cert.chapter_id:
        # Practice certificate: check chapter pass rate
        from models import PracticeRecord
        records = db.query(PracticeRecord).filter(
            PracticeRecord.user_id == user.id,
            PracticeRecord.chapter_id == cert.chapter_id
        ).all()
        if not records:
            raise HTTPException(400, "您尚未练习过此章节")
        total_q = sum(r.total_count or 0 for r in records)
        correct_q = sum(r.correct_count or 0 for r in records)
        if total_q < 10:
            raise HTTPException(400, "练习数量不足（至少10题）")
        rate = correct_q / total_q * 100 if total_q > 0 else 0
        if rate < 60:
            raise HTTPException(400, f"正确率{rate:.1f}%不足60%，暂不可申请")

    elif cert.cert_type == "exam":
        # Exam certificate: check if passed any formal exam
        passed = db.query(ExamResult).join(Exam).filter(
            ExamResult.user_id == user.id,
            ExamResult.passed == True,
            Exam.mode == "formal"
        ).first()
        if not passed:
            raise HTTPException(400, "您尚未通过任何正式考试")

    import uuid
    uc = UserCertificate(
        certificate_id=certificate_id,
        user_id=user.id,
        certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}"
    )
    db.add(uc)
    db.commit()
    db.refresh(uc)
    return {"ok": True, "certificate_no": uc.certificate_no, "message": "证书申请成功！"}
'''

# Insert before @router.post("/{exam_id}/report-tab-switch")
content = content.replace(
    '@router.post("/{exam_id}/report-tab-switch")',
    apply_endpoint + '\n@router.post("/{exam_id}/report-tab-switch")'
)

# Also need to import HTTPException if not already imported
if 'from fastapi import' in content and 'HTTPException' not in content[:500]:
    content = content.replace(
        'from fastapi import APIRouter, Depends, Query',
        'from fastapi import APIRouter, Depends, HTTPException, Query'
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed exams_router.py")
