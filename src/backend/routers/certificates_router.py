from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from orm_utils import orm_to_dict
from database import get_db
from models import Certificate, UserCertificate, ExamResult, Exam, User, PracticeRecord, Chapter, Subject
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/certificates", tags=["证书管理"])


class CertOut(BaseModel):
    id: int; name: str; description: str; template_image: str | None = ""; issue_rule: str = "{}"; cert_type: str = "exam"; chapter_id: int | None = None; created_at: str | None = None
    model_config = {"from_attributes": True}

class CertCreate(BaseModel):
    name: str; description: str = ""; template_image: str | None = ""; issue_rule: str = "{}"; cert_type: str = "exam"; chapter_id: int | None = None

class UserCertOut(BaseModel):
    id: int; certificate_id: int; certificate_name: str = ""
    user_id: int; username: str = ""; fullname: str = ""
    exam_result_id: int | None = None; certificate_no: str
    is_revoked: bool; issued_at: str | None = None; revoked_at: str | None = None
    model_config = {"from_attributes": True}


# --- 证书模板 CRUD ---

@router.get("", response_model=list[CertOut])
def list_certs(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    result = []
    for c in db.query(Certificate).all():
        d = orm_to_dict(c)
        if d.get("template_image") is None: d["template_image"] = ""
        if d.get("issue_rule") is None: d["issue_rule"] = "{}"
        result.append(d)
    return result

@router.post("", response_model=CertOut)
def create_cert(data: CertCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = Certificate(**data.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return orm_to_dict(c)

@router.put("/{cert_id}", response_model=CertOut)
def update_cert(cert_id: int, data: CertCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = db.query(Certificate).get(cert_id)
    if not c: raise HTTPException(404, "证书不存在")
    for k, v in data.model_dump().items(): setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c

@router.delete("/{cert_id}")
def delete_cert(cert_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = db.query(Certificate).get(cert_id)
    if not c: raise HTTPException(404, "证书不存在")
    db.delete(c); db.commit()
    return {"ok": True}


# --- 用户证书 ---

@router.get("/user/{user_id}", response_model=list[UserCertOut])
def user_certs(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    certs = db.query(UserCertificate).filter(UserCertificate.user_id == user_id, UserCertificate.is_revoked == False).all()
    return [_uc_out(uc) for uc in certs]

@router.get("/my")
def my_certs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    certs = db.query(UserCertificate).filter(UserCertificate.user_id == user.id, UserCertificate.is_revoked == False).all()
    return [_uc_out(uc) for uc in certs]

@router.post("/apply")
def apply_for_cert(certificate_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Client applies for certificate - system checks eligibility"""
    cert = db.query(Certificate).get(certificate_id)
    if not cert:
        raise HTTPException(404, "Certificate not found")
    
    already = db.query(UserCertificate).filter(
        UserCertificate.certificate_id == certificate_id,
        UserCertificate.user_id == user.id,
        UserCertificate.is_revoked == False
    ).first()
    if already:
        return {"ok": True, "message": "Already have this cert", "certificate_no": already.certificate_no}
    
    if cert.cert_type == "practice":
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
            raise HTTPException(400, "该科目暂无练习记录，请先完成练习")
        total_q = sum(r.total_count or 0 for r in records)
        correct_q = sum(r.correct_count or 0 for r in records)
        if total_q < 10:
            raise HTTPException(400, "练习题数不足10道，请继续练习")
        rate = correct_q / total_q * 100 if total_q > 0 else 0
        if rate < 60:
            raise HTTPException(400, f"正确率 {rate:.1f}% 未达到60%申请标准，请继续练习")
    elif cert.cert_type == "exam":
        passed = db.query(ExamResult).join(Exam).filter(
            ExamResult.user_id == user.id,
            ExamResult.passed == True,
            Exam.mode == "formal"
        ).first()
        if not passed:
            raise HTTPException(400, "No passed formal exam")
    
    import uuid
    uc = UserCertificate(
        certificate_id=certificate_id,
        user_id=user.id,
        certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}",
        auto_issued=True,
        issue_reason="apply"
    )
    db.add(uc)
    db.commit()
    db.refresh(uc)
    return {"ok": True, "certificate_no": uc.certificate_no, "message": "Certificate issued!"}

@router.post("/issue")
def issue_cert(certificate_id: int, user_id: int, exam_result_id: int | None = None, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    import uuid
    uc = UserCertificate(
        certificate_id=certificate_id, user_id=user_id,
        exam_result_id=exam_result_id,
        certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}",
    )
    db.add(uc); db.commit(); db.refresh(uc)
    log_operation(db, _.id, _.username, "issue", "certificate", uc.id, detail=f"颁发证书给用户ID:{user_id}")
    return _uc_out(uc)

@router.post("/{user_cert_id}/revoke")
def revoke_cert(user_cert_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    uc = db.query(UserCertificate).get(user_cert_id)
    if not uc: raise HTTPException(404, "证书记录不存在")
    uc.is_revoked = True
    from datetime import datetime, timezone
    uc.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@router.get("/all-issued", response_model=dict)
def all_issued(page: int = Query(1, ge=1), page_size: int = Query(20), db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    q = db.query(UserCertificate).order_by(UserCertificate.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [_uc_out(uc) for uc in items]}


def _uc_out(uc: UserCertificate):
    return {
        "id": uc.id, "certificate_id": uc.certificate_id,
        "certificate_name": uc.certificate.name if uc.certificate else "",
        "user_id": uc.user_id, "username": uc.user.username if uc.user else "",
        "fullname": uc.user.fullname if uc.user else "",
        "exam_result_id": uc.exam_result_id, "certificate_no": uc.certificate_no,
        "is_revoked": uc.is_revoked,
        "issued_at": uc.issued_at.isoformat() if uc.issued_at else None,
        "revoked_at": uc.revoked_at.isoformat() if uc.revoked_at else None,
    }


# --- 练习证书资格检查 ---

def auto_check_after_exam(exam_result_id: int, db: Session = Depends(get_db)):
    """考试提交后自动检查并颁发证书（内部调用）"""
    result = db.query(ExamResult).filter(ExamResult.id == exam_result_id).first()
    if not result or not result.total_score or result.total_score == 0:
        return {"ok": False, "message": "成绩无效"}
    
    pass_rate = result.auto_score / result.total_score if result.total_score else 0
    exam = db.query(Exam).get(result.exam_id)
    exam_pass_rate = (exam.pass_score if exam and exam.pass_score else 60) / (exam.total_score if exam and exam.total_score else 100)
    if pass_rate < exam_pass_rate:
        return {"ok": True, "message": "未达颁发标准(80%)", "passed": False}
    
    # Find certificates matching this exam
    certs = db.query(Certificate).filter(Certificate.cert_type == "exam").all()
    issued = []
    for cert in certs:
        already = db.query(UserCertificate).filter(
            UserCertificate.certificate_id == cert.id,
            UserCertificate.user_id == result.user_id,
            UserCertificate.is_revoked == False
        ).first()
        if already:
            continue
        import uuid
        uc = UserCertificate(
            certificate_id=cert.id,
            user_id=result.user_id,
            exam_result_id=result.id,
            certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}",
            auto_issued=True,
            issue_reason="exam_pass"
        )
        db.add(uc)
        issued.append(cert.name)
    
    db.commit()
    return {"ok": True, "message": f"自动颁发了{len(issued)}个证书", "certificates": issued}



@router.get("/exam-eligibility")
def check_exam_eligibility(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Check passed formal exams and return applyable exam certificates"""
    exam_certs = db.query(Certificate).filter(Certificate.cert_type == "exam").all()
    eligible = []
    for cert in exam_certs:
        already = db.query(UserCertificate).filter(
            UserCertificate.user_id == user.id,
            UserCertificate.certificate_id == cert.id,
            UserCertificate.is_revoked == False
        ).first()
        best = db.query(ExamResult).join(Exam).filter(
            ExamResult.user_id == user.id,
            ExamResult.passed == True,
            Exam.mode == "formal"
        ).order_by(ExamResult.auto_score.desc()).first()
        eligible.append({
            "certificate_id": cert.id,
            "certificate_name": cert.name,
            "description": cert.description,
            "already_issued": already is not None,
            "certificate_no": already.certificate_no if already else None,
            "best_score": round(best.auto_score, 1) if best else None,
            "best_exam": best.exam.title if best and best.exam else None,
            "can_apply": best is not None and already is None,
        })
    return eligible

@router.get("/practice-eligibility")
def check_practice_eligibility(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """检查用户各章节的练习通过率，返回可申请的练习证书"""
    # Get all practice certificates
    practice_certs = db.query(Certificate).filter(Certificate.cert_type == "practice").all()
    
    eligible = []
    for cert in practice_certs:
        if not cert.chapter_id:
            continue
        
        # Count practice records for this chapter (fallback to subject-level)
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
            continue
        
        total_q = sum(r.total_count or 0 for r in records)
        correct_q = sum(r.correct_count or 0 for r in records)
        if total_q < 10:
            continue
        
        rate = round(correct_q / total_q * 100, 1)
        
        # Get chapter and subject info
        chapter = db.query(Chapter).get(cert.chapter_id)
        subject_name = ""
        chapter_name = chapter.name if chapter else ""
        if chapter:
            subj = db.query(Subject).get(chapter.subject_id)
            if subj:
                subject_name = subj.name
        
        # Check if already issued
        already = db.query(UserCertificate).filter(
            UserCertificate.user_id == user.id,
            UserCertificate.certificate_id == cert.id,
            UserCertificate.is_revoked == False
        ).first()
        
        eligible.append({
            "certificate_id": cert.id,
            "certificate_name": cert.name,
            "description": cert.description,
            "chapter_name": chapter_name,
            "subject_name": subject_name,
            "total_questions": total_q,
            "correct_questions": correct_q,
            "pass_rate": rate,
            "already_issued": already is not None,
            "certificate_no": already.certificate_no if already else None,
        })
    
    return eligible
