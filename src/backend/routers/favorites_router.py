from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Favorite, Question, User
from auth import get_current_user
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/favorites", tags=["收藏"])


class FavoriteCreate(BaseModel):
    question_id: int; tags: str = "[]"


@router.get("")
def my_favorites(subject_id: int = Query(None), page: int = Query(1, ge=1), page_size: int = Query(50), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.id.desc())
    if subject_id:
        q = q.join(Question).filter(Question.subject_id == subject_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    qids = [f.question_id for f in items]
    q_map = {q.id: q for q in db.query(Question).filter(Question.id.in_(qids)).all()} if qids else {}
    result = []
    for f in items:
        qst = q_map.get(f.question_id)
        result.append({
            "id": f.id, "question_id": f.question_id, "tags": f.tags,
            "question_content": qst.content[:120] if qst else "",
            "question_type": qst.type if qst else "",
            "question_answer": qst.answer if qst else "",
            "question_options": qst.options if qst else "",
            "explanation": qst.explanation if qst else "",
            "difficulty": qst.difficulty if qst else 0,
            "subject_name": qst.subject.name if qst and qst.subject else "",
            "created_at": f.created_at.isoformat() if f.created_at else None,
        })
    return {"total": total, "items": result}

@router.get("/check/{question_id}")
def check_favorite(question_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.question_id == question_id).first()
    return {"is_favorited": f is not None, "id": f.id if f else None, "tags": f.tags if f else "[]"}

@router.post("/toggle/{question_id}")
def toggle_favorite(question_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.question_id == question_id).first()
    if f:
        db.delete(f); db.commit()
        return {"is_favorited": False}
    f = Favorite(user_id=user.id, question_id=question_id)
    db.add(f); db.commit()
    return {"is_favorited": True, "id": f.id}

@router.put("/{fav_id}/tags")
def update_tags(fav_id: int, tags: str = "[]", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(Favorite).filter(Favorite.id == fav_id, Favorite.user_id == user.id).first()
    if not f: raise HTTPException(404, "收藏不存在")
    f.tags = tags; db.commit()
    return {"ok": True}

@router.delete("/{fav_id}")
def delete_favorite(fav_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(Favorite).filter(Favorite.id == fav_id, Favorite.user_id == user.id).first()
    if not f: raise HTTPException(404, "收藏不存在")
    db.delete(f); db.commit()
    return {"ok": True}
