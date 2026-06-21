import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import OperationLog, User
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/audit", tags=["操作日志"])


@router.get("")
def list_logs(action: str = Query(None), target_type: str = Query(None), username: str = Query(None),
              page: int = Query(1, ge=1), page_size: int = Query(50),
              db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    q = db.query(OperationLog).order_by(OperationLog.id.desc())
    if action: q = q.filter(OperationLog.action == action)
    if target_type: q = q.filter(OperationLog.target_type == target_type)
    if username: q = q.filter(OperationLog.username.contains(username))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [{
        "id": l.id, "user_id": l.user_id, "username": l.username,
        "action": l.action, "target_type": l.target_type, "target_id": l.target_id,
        "detail": l.detail, "ip_address": l.ip_address,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    } for l in items]}


# Helper to log operations from other routers
def log_operation(db: Session, user_id: int, username: str, action: str, target_type: str, target_id: int = None, detail: str = ""):
    log = OperationLog(
        user_id=user_id, username=username, action=action,
        target_type=target_type, target_id=target_id, detail=detail,
    )
    db.add(log)
    db.commit()
