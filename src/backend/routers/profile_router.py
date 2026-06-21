import re
"""个人中心路由"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, hash_password, verify_password
from models import User, PracticeRecord, UserCertificate

router = APIRouter(prefix="/api/profile", tags=["个人中心"])


def _validate_password(password: str):
    if len(password) < 6:
        raise HTTPException(400, "密码长度至少6位")
    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(400, "密码必须包含字母")
    if not re.search(r"[0-9]", password):
        raise HTTPException(400, "密码必须包含数字")
    if re.search(r"^(.)\1+$", password):
        raise HTTPException(400, "密码不能全是相同字符")
    if password.lower() in ("123456", "password", "qwerty", "abc123", "111111", "aaaaaa"):
        raise HTTPException(400, "密码过于简单，请换一个")


class PasswordChangeReq(BaseModel):
    old_password: str
    new_password: str


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """获取个人学习统计"""
    total_practice = db.query(PracticeRecord).filter(
        PracticeRecord.user_id == user.id
    ).count()

    # 正确率
    correct_rate = 0
    try:
        records = db.query(PracticeRecord).filter(
            PracticeRecord.user_id == user.id
        ).all()
        if records:
            total_q = sum(r.total_count or 0 for r in records)
            correct_q = sum(r.correct_count or 0 for r in records)
            correct_rate = round(correct_q / total_q * 100, 1) if total_q > 0 else 0
    except Exception:
        pass

    # 学习天数
    study_days = total_practice  # fallback
    try:
        dates = db.query(PracticeRecord.created_at).filter(
            PracticeRecord.user_id == user.id
        ).all()
        if dates:
            study_days = len(set(d[0].strftime('%Y-%m-%d') for d in dates if d[0]))
    except Exception:
        pass

    # 证书数
    certs = 0
    try:
        certs = db.query(UserCertificate).filter(
            UserCertificate.user_id == user.id,
            UserCertificate.is_revoked == False
        ).count()
    except Exception:
        pass

    return {
        "total_practice": total_practice,
        "correct_rate": correct_rate,
        "study_days": study_days,
        "certs": certs
    }


@router.put("/password")
def change_password(
    req: PasswordChangeReq,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """修改密码"""
    if not verify_password(req.old_password, user.hashed_password):
        raise HTTPException(403, "旧密码错误")
    _validate_password(req.new_password)
    user.hashed_password = hash_password(req.new_password)
    db.commit()
    return {"ok": True}
