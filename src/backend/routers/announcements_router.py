from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from orm_utils import orm_to_dict
from database import get_db
from routers.notifications import notify_all_users
from models import Announcement, User
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/announcements", tags=["公告管理"])


class AnnouncementOut(BaseModel):
    id: int; title: str; content: str; is_pinned: bool; is_published: bool
    created_by: str; created_at: str | None = None
    model_config = {"from_attributes": True}

class AnnouncementCreate(BaseModel):
    title: str; content: str; is_pinned: bool = False; is_published: bool = False


@router.get("", response_model=dict)
def list_announcements(page: int = Query(1, ge=1), page_size: int = Query(20), published_only: bool = Query(False), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    q = db.query(Announcement).order_by(Announcement.is_pinned.desc(), Announcement.id.desc())
    if published_only:
        q = q.filter(Announcement.is_published == True)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [AnnouncementOut.model_validate(orm_to_dict(a)) for a in items]}

@router.post("", response_model=AnnouncementOut)
def create_announcement(data: AnnouncementCreate, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "teacher"))):
    a = Announcement(**data.model_dump(), created_by=user.fullname or user.username)
    db.add(a); db.commit(); db.refresh(a)
    return a

@router.put("/{ann_id}", response_model=AnnouncementOut)
def update_announcement(ann_id: int, data: AnnouncementCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    a = db.query(Announcement).get(ann_id)
    if not a: raise HTTPException(404, "公告不存在")
    for k, v in data.model_dump().items(): setattr(a, k, v)
    db.commit(); db.refresh(a)
    return a

@router.delete("/{ann_id}")
def delete_announcement(ann_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    a = db.query(Announcement).get(ann_id)
    if not a: raise HTTPException(404, "公告不存在")
    db.delete(a); db.commit()
    return {"ok": True}
