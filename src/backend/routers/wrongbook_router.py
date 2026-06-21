from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import WrongAnswer, Question, User
from auth import get_current_user
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/wrongbook", tags=["错题本"])


@router.get("")
def my_wrongbook(subject_id: int = Query(None), chapter_id: int = Query(None), is_mastered: bool = Query(None), page: int = Query(1, ge=1), page_size: int = Query(50), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(WrongAnswer).filter(WrongAnswer.user_id == user.id)
    if is_mastered is not None:
        q = q.filter(WrongAnswer.is_mastered == is_mastered)
    q = q.join(Question)
    if subject_id:
        q = q.filter(Question.subject_id == subject_id)
    if chapter_id:
        q = q.filter(Question.chapter_id == chapter_id)
    q = q.order_by(WrongAnswer.last_wrong_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for wa in items:
        qst = db.query(Question).get(wa.question_id)
        result.append({
            "id": wa.id, "question_id": wa.question_id, "wrong_count": wa.wrong_count,
            "is_mastered": wa.is_mastered,
            "question_content": qst.content[:120] if qst else "",
            "question_type": qst.type if qst else "",
            "subject_name": qst.subject.name if qst and qst.subject else "",
            "chapter_name": qst.chapter.name if qst and qst.chapter else "",
            "last_wrong_at": wa.last_wrong_at.isoformat() if wa.last_wrong_at else None,
        })
    return {"total": total, "items": result}

@router.post("/mark-mastered/{wrong_id}")
def mark_mastered(wrong_id: int, mastered: bool = True, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wa = db.query(WrongAnswer).filter(WrongAnswer.id == wrong_id, WrongAnswer.user_id == user.id).first()
    if not wa: raise HTTPException(404, "记录不存在")
    wa.is_mastered = mastered; db.commit()
    return {"ok": True}

@router.delete("/{wrong_id}")
def delete_wrong(wrong_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wa = db.query(WrongAnswer).filter(WrongAnswer.id == wrong_id, WrongAnswer.user_id == user.id).first()
    if not wa: raise HTTPException(404, "记录不存在")
    db.delete(wa); db.commit()
    return {"ok": True}

@router.post("/clear-mastered")
def clear_mastered(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(WrongAnswer).filter(WrongAnswer.user_id == user.id, WrongAnswer.is_mastered == True).delete()
    db.commit()
    return {"ok": True}


# Internal helper - record wrong answer (called from practice/exam submit)
def record_wrong(user_id: int, question_id: int, db: Session):
    wa = db.query(WrongAnswer).filter(WrongAnswer.user_id == user_id, WrongAnswer.question_id == question_id).first()
    if wa:
        wa.wrong_count += 1
        wa.last_wrong_at = datetime.now(timezone.utc)
        wa.is_mastered = False
    else:
        wa = WrongAnswer(user_id=user_id, question_id=question_id)
        db.add(wa)
    db.commit()
