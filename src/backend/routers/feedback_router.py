from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import QuestionFeedback, Question, User
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/feedback", tags=["题目反馈"])


class FeedbackOut(BaseModel):
    id: int; user_id: int; username: str = ""
    question_id: int; question_content: str = ""
    type: str; content: str; images: str
    status: str; reply: str; replied_by: str
    created_at: str | None = None; updated_at: str | None = None
    model_config = {"from_attributes": True}

class FeedbackCreate(BaseModel):
    question_id: int; type: str = "doubt"; content: str; images: str = "[]"

class FeedbackReply(BaseModel):
    reply: str; status: str = "accepted"


@router.get("", response_model=dict)
def list_feedback(status: str = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20), db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    q = db.query(QuestionFeedback).order_by(QuestionFeedback.id.desc())
    if status: q = q.filter(QuestionFeedback.status == status)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [_fb_out(f) for f in items]}

@router.get("/my")
def my_feedback(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(QuestionFeedback).filter(QuestionFeedback.user_id == user.id).order_by(QuestionFeedback.id.desc()).all()
    return [_fb_out(f) for f in items]

@router.post("", response_model=FeedbackOut)
def create_feedback(data: FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Question).get(data.question_id)
    if not q: raise HTTPException(404, "题目不存在")
    f = QuestionFeedback(user_id=user.id, **data.model_dump())
    db.add(f); db.commit(); db.refresh(f)
    return _fb_out(f)

@router.put("/{fb_id}/reply")
def reply_feedback(fb_id: int, data: FeedbackReply, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "teacher"))):
    f = db.query(QuestionFeedback).get(fb_id)
    if not f: raise HTTPException(404, "反馈不存在")
    f.status = data.status
    f.reply = data.reply
    f.replied_by = user.fullname or user.username
    f.updated_at = datetime.now(timezone.utc)

    # If accepted error report, optionally update the question
    if data.status == "accepted" and f.type == "error_report":
        q = db.query(Question).get(f.question_id)
        if q:
            q.updated_at = datetime.now(timezone.utc)

    db.commit(); db.refresh(f)
    return _fb_out(f)


def _fb_out(f: QuestionFeedback):
    return {
        "id": f.id, "user_id": f.user_id,
        "username": f.user.fullname or f.user.username if f.user else "",
        "question_id": f.question_id,
        "question_content": f.question.content[:100] if f.question else "",
        "type": f.type, "content": f.content, "images": f.images,
        "status": f.status, "reply": f.reply, "replied_by": f.replied_by,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }
