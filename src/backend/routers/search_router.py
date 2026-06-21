"""全局搜索路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import Question, Resource, Announcement, Subject

router = APIRouter(prefix="/api/search", tags=["搜索"])

@router.get("")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db), _=Depends(get_current_user)):
    """全局搜索题目、资料、公告"""
    questions = db.query(Question).filter(
        Question.content.contains(q)
    ).limit(5).all()
    resources = db.query(Resource).filter(
        Resource.title.contains(q)
    ).limit(3).all()
    announcements = db.query(Announcement).filter(
        Announcement.title.contains(q)
    ).limit(3).all()
    
    # Get subject names for questions
    q_results = []
    for quest in questions:
        subject = db.query(Subject).get(quest.subject_id) if quest.subject_id else None
        q_results.append({
            "id": quest.id,
            "content": (quest.content or "")[:80],
            "type": quest.type,
            "subject_name": subject.name if subject else ""
        })
    
    r_results = []
    for res in resources:
        r_results.append({
            "id": res.id,
            "title": res.title,
            "file_type": res.file_type or "",
            "file_url": res.file_url or ""
        })
    
    a_results = []
    for ann in announcements:
        a_results.append({
            "id": ann.id,
            "title": ann.title,
            "content": (ann.content or "")[:80],
            "created_at": ann.created_at.isoformat() if ann.created_at else None
        })
    
    return {
        "questions": q_results,
        "resources": r_results,
        "announcements": a_results,
    }
