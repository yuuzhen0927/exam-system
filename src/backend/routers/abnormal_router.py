from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import AbnormalReport, ExamResult, User
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/abnormal", tags=["异常报告"])


@router.get("")
def list_abnormal(page: int = Query(1, ge=1), page_size: int = Query(20),
                  db: Session = Depends(get_db), _=Depends(require_role("admin", "teacher"))):
    q = db.query(AbnormalReport).order_by(AbnormalReport.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [{
        "id": a.id, "exam_result_id": a.exam_result_id,
        "user_id": a.user_id, "username": a.user.username if a.user else "",
        "fullname": a.user.fullname if a.user else "",
        "reason": a.reason, "detail": a.detail,
        "is_judged": a.is_judged, "judgment": a.judgment, "judged_by": a.judged_by,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in items]}


@router.post("/{report_id}/judge")
def judge_report(report_id: int, judgment: str = Query(...),
                  db: Session = Depends(get_db), user: User = Depends(require_role("admin", "teacher"))):
    from fastapi import HTTPException
    if judgment not in ("valid", "invalid"):
        raise HTTPException(400, "judgment must be 'valid' or 'invalid'")
    a = db.query(AbnormalReport).get(report_id)
    if not a: raise HTTPException(404, "报告不存在")
    a.is_judged = True
    a.judgment = judgment
    a.judged_by = user.fullname or user.username
    result = db.query(ExamResult).get(a.exam_result_id)
    if result:
        if judgment == "invalid":
            result.is_cheating = True
        else:
            result.is_cheating = False
    db.commit()
    return {"ok": True, "judgment": judgment, "is_cheating": result.is_cheating if result else None}
