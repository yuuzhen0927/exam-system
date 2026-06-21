"""通知系统路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, require_role
from models import Notification, User

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("")
def get_notifications(
    page: int = 1, page_size: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取当前用户的通知列表"""
    total = db.query(Notification).filter(
        Notification.user_id == user.id
    ).count()
    items = db.query(Notification).filter(
        Notification.user_id == user.id
    ).order_by(Notification.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    unread = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False
    ).count()
    return {
        "items": [{
            "id": n.id, "type": n.type, "title": n.title,
            "content": n.content, "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None
        } for n in items],
        "total": total, "unread": unread
    }


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id
    ).first()
    if not n:
        raise HTTPException(404, "通知不存在")
    n.is_read = True
    db.commit()
    return {"ok": True}


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}


def notify_user(user_id: int, type: str, title: str, content: str = "", link: str = "", db: Session = None):
    """给指定用户发送通知（工具函数）"""
    if db is None:
        return
    n = Notification(
        user_id=user_id, type=type, title=title,
        content=content, link=link
    )
    db.add(n)
    db.commit()


def notify_all_users(type: str, title: str, content: str = "", link: str = "", db: Session = None):
    """给所有用户发送通知"""
    if db is None:
        return
    from models import User
    users = db.query(User.id).all()
    for (uid,) in users:
        n = Notification(
            user_id=uid, type=type, title=title,
            content=content, link=link
        )
        db.add(n)
    db.commit()
