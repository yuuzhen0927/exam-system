from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Note, User
from auth import get_current_user
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/notes", tags=["笔记"])


class NoteCreate(BaseModel):
    question_id: int | None = None
    title: str = ""
    content: str

class NoteUpdate(BaseModel):
    content: str
    title: str | None = None


@router.get("/{question_id}")
def get_note(question_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.user_id == user.id, Note.question_id == question_id).first()
    if not note: return {"id": None, "content": ""}
    return {"id": note.id, "question_id": note.question_id, "content": note.content, "created_at": note.created_at.isoformat() if note.created_at else None, "updated_at": note.updated_at.isoformat() if note.updated_at else None}

@router.post("")
def create_note(data: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.question_id:
        existing = db.query(Note).filter(Note.user_id == user.id, Note.question_id == data.question_id).first()
        if existing:
            existing.content = data.content
            existing.title = data.title or existing.title
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            return {"ok": True, "id": existing.id}
    note = Note(user_id=user.id, question_id=data.question_id, title=data.title or "", content=data.content)
    db.add(note); db.commit(); db.refresh(note)
    return {"ok": True, "id": note.id}

@router.put("/{note_id}")
def update_note(note_id: int, data: NoteUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not n: raise HTTPException(404, "笔记不存在")
    n.content = data.content
    if data.title is not None:
        n.title = data.title
    n.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not n: raise HTTPException(404, "笔记不存在")
    db.delete(n); db.commit()
    return {"ok": True}

@router.get("")
def my_notes(page: int = 1, page_size: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Note).filter(Note.user_id == user.id).order_by(Note.updated_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for n in items:
        item = {"id": n.id, "question_id": n.question_id, "title": n.title or "", "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "updated_at": n.updated_at.isoformat() if n.updated_at else None}
        if n.question and n.question.subject_id:
            from models import Subject
            subj = db.query(Subject).get(n.question.subject_id)
            item["subject_name"] = subj.name if subj else ""
        result.append(item)
    return {"total": total, "items": result}
