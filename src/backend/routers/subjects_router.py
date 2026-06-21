from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from orm_utils import orm_to_dict
from database import get_db
from models import Subject, Chapter, User
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/subjects", tags=["科目管理"])


class SubjectOut(BaseModel):
    id: int; name: str; description: str; sort_order: int; question_count: int = 0; created_at: str | None = None
    model_config = {"from_attributes": True}

class SubjectCreate(BaseModel):
    name: str; description: str = ""; sort_order: int = 0

class ChapterOut(BaseModel):
    id: int; subject_id: int; name: str; description: str; sort_order: int; question_count: int = 0; subject_name: str = ""; created_at: str | None = None
    model_config = {"from_attributes": True}

class ChapterCreate(BaseModel):
    subject_id: int; name: str; description: str = ""; sort_order: int = 0


@router.get("", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    subjects = db.query(Subject).order_by(Subject.sort_order).all()
    return [_subject_out(s, db) for s in subjects]

@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    s = db.query(Subject).get(subject_id)
    if not s: raise HTTPException(404, "科目不存在")
    return _subject_out(s, db)

@router.post("", response_model=SubjectOut)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    if db.query(Subject).filter(Subject.name == data.name).first():
        raise HTTPException(400, "科目已存在")
    s = Subject(**data.model_dump())
    db.add(s); db.commit(); db.refresh(s)
    return _subject_out(s, db)

@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, data: SubjectCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    s = db.query(Subject).get(subject_id)
    if not s: raise HTTPException(404, "科目不存在")
    for k, v in data.model_dump().items(): setattr(s, k, v)
    db.commit(); db.refresh(s)
    return _subject_out(s, db)

@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    s = db.query(Subject).get(subject_id)
    if not s: raise HTTPException(404, "科目不存在")
    db.delete(s); db.commit()
    return {"ok": True}


# --- 章节 ---

@router.get("/{subject_id}/chapters", response_model=list[ChapterOut])
def list_chapters(subject_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    chapters = db.query(Chapter).filter(Chapter.subject_id == subject_id).order_by(Chapter.sort_order).all()
    return [_chapter_out(c, db) for c in chapters]

@router.post("/{subject_id}/chapters", response_model=ChapterOut)
def create_chapter(subject_id: int, data: ChapterCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    if not db.query(Subject).get(subject_id): raise HTTPException(404, "科目不存在")
    c = Chapter(subject_id=subject_id, name=data.name, description=data.description, sort_order=data.sort_order)
    db.add(c); db.commit(); db.refresh(c)
    return _chapter_out(c, db)

@router.put("/chapters/{chapter_id}", response_model=ChapterOut)
def update_chapter(chapter_id: int, data: ChapterCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    c = db.query(Chapter).get(chapter_id)
    if not c: raise HTTPException(404, "章节不存在")
    for k, v in data.model_dump().items(): setattr(c, k, v)
    db.commit(); db.refresh(c)
    return _chapter_out(c, db)

@router.delete("/chapters/{chapter_id}")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    c = db.query(Chapter).get(chapter_id)
    if not c: raise HTTPException(404, "章节不存在")
    db.delete(c); db.commit()
    return {"ok": True}



@router.get("/chapters/all", response_model=list[ChapterOut])
def list_all_chapters(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """返回所有章节（带科目名）"""
    chapters = db.query(Chapter).all()
    return [_chapter_out(c, db) for c in chapters]



def _subject_out(s: Subject, db: Session):
    out = SubjectOut.model_validate(orm_to_dict(s))
    out.question_count = len(s.questions) if hasattr(s, 'questions') and s.questions else 0
    return out

def _chapter_out(c: Chapter, db: Session):
    out = ChapterOut.model_validate(orm_to_dict(c))
    out.question_count = len(c.questions) if c.questions else 0
    if c.subject:
        out.subject_name = c.subject.name
    return out
