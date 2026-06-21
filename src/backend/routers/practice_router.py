import json, random
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import PracticeRecord, Question, WrongAnswer, User, Subject, Favorite
from auth import get_current_user
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/practice", tags=["练习"])

class PracticeStartRequest(BaseModel):
    mode: str = "random"
    subject_id: int | None = None
    chapter_id: int | None = None
    specialty: str = ""
    question_type: str = ""
    count: int = 20
    difficulty_min: int = 1
    difficulty_max: int = 5
    question_ids: list[int] = []

def _normalize_answer(answer_str: str) -> str:
    """Normalize JSON answer from DB: ["B"] -> B, ["A","C","D"] -> ACD"""
    try:
        if not answer_str: return ""
        arr = json.loads(answer_str) if isinstance(answer_str, str) else answer_str
        return "".join(sorted([str(x).strip().upper() for x in arr]))
    except Exception:
        return answer_str.strip().upper() if answer_str else ""

@router.post("/start")
def start_practice(data: PracticeStartRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.mode == "wrongbook" and data.question_ids:
        pool = db.query(Question).filter(Question.id.in_(data.question_ids), Question.is_active == True).all()
    else:
        q = db.query(Question).filter(Question.is_active == True)
        if data.mode == "specialty" and data.specialty:
            q = q.filter(Question.specialty == data.specialty)
        elif data.mode == "chapter" and data.chapter_id:
            q = q.filter(Question.chapter_id == data.chapter_id)
        if data.subject_id:
            q = q.filter(Question.subject_id == data.subject_id)
        if data.question_type:
            q = q.filter(Question.type == data.question_type)
        q = q.filter(Question.difficulty >= data.difficulty_min, Question.difficulty <= data.difficulty_max)
        pool = q.all()

    if len(pool) < data.count:
        data.count = len(pool)
    if data.count == 0:
        raise HTTPException(400, "没有符合条件的题目")

    chosen = random.sample(pool, data.count)
    questions = [{
        "id": c.id, "type": c.type, "content": c.content,
        "options": json.loads(c.options) if c.options else [],
        "difficulty": c.difficulty, "images": json.loads(c.images) if c.images else [],
        "answer": _normalize_answer(c.answer), "explanation": c.explanation or "",
    } for c in chosen]

    record = PracticeRecord(
        user_id=user.id, mode=data.mode,
        subject_id=data.subject_id, chapter_id=data.chapter_id,
        specialty=data.specialty, question_type=data.question_type,
        total_count=data.count,
    )
    db.add(record); db.commit(); db.refresh(record)
    return {"record_id": record.id, "total": data.count, "questions": questions}

@router.post("/{record_id}/submit")
def submit_practice(record_id: int, answers: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(PracticeRecord).filter(PracticeRecord.id == record_id, PracticeRecord.user_id == user.id).first()
    if not record: raise HTTPException(404, "练习记录不存在")

    correct = 0; wrong = 0; results = []
    for qid_str, user_ans in answers.items():
        qid = int(qid_str)
        qst = db.query(Question).get(qid)
        if not qst: continue
        is_correct = _judge(qst.type, qst.answer, str(user_ans))
        if is_correct: correct += 1
        else:
            wrong += 1
            _record_wrong(user.id, qid, db)
        results.append({"question_id": qid, "is_correct": is_correct, "correct_answer": _normalize_answer(qst.answer), "explanation": qst.explanation})

    record.correct_count = correct; record.wrong_count = wrong; record.answers = json.dumps(results)
    db.commit()
    return {"record_id": record.id, "total": record.total_count, "correct": correct, "wrong": wrong, "results": results}

@router.get("/records")
def my_records(page: int = Query(1, ge=1), page_size: int = Query(20), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(PracticeRecord).filter(PracticeRecord.user_id == user.id).order_by(PracticeRecord.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    smap = {s.id: s.name for s in db.query(Subject).all()}
    return {"total": total, "items": [{"id": r.id, "mode": r.mode, "subject_id": r.subject_id, "subject_name": smap.get(r.subject_id, ""), "chapter_id": r.chapter_id, "specialty": r.specialty, "question_type": r.question_type, "total_count": r.total_count, "correct_count": r.correct_count, "wrong_count": r.wrong_count, "duration_seconds": r.duration_seconds, "created_at": r.created_at.isoformat() if r.created_at else None} for r in items]}

@router.get("/stats")
def practice_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records = db.query(PracticeRecord).filter(PracticeRecord.user_id == user.id).all()
    total_questions = sum(r.total_count for r in records)
    total_correct = sum(r.correct_count for r in records)
    total_wrong = sum(r.wrong_count for r in records)
    accuracy = round(total_correct / total_questions * 100, 1) if total_questions > 0 else 0
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    daily = {}
    for i in range(30):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        daily[day] = 0
    for r in records:
        if not r.created_at: continue
        day = r.created_at.strftime("%Y-%m-%d")
        if day in daily: daily[day] += r.total_count
    return {"total_questions": total_questions, "total_correct": total_correct, "total_wrong": total_wrong, "accuracy": accuracy, "daily_activity": [{"date": k, "count": v} for k, v in sorted(daily.items())]}

@router.get("/records/{record_id}/wrong-questions")
def record_wrong_questions(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(PracticeRecord).filter(PracticeRecord.id == record_id, PracticeRecord.user_id == user.id).first()
    if not record: raise HTTPException(404, "记录不存在")
    wa = db.query(WrongAnswer).filter(WrongAnswer.user_id == user.id, WrongAnswer.is_mastered == False).order_by(WrongAnswer.last_wrong_at.desc()).limit(50).all()
    qids = [w.question_id for w in wa]
    questions = db.query(Question).filter(Question.id.in_(qids), Question.is_active == True).all()
    return [{"id": q.id, "type": q.type, "content": q.content, "options": json.loads(q.options) if q.options else [], "difficulty": q.difficulty, "images": json.loads(q.images) if q.images else []} for q in questions]

def _judge(qtype: str, correct: str, user_answer: str) -> bool:
    try:
        ua = user_answer.strip().upper()
        ca = _normalize_answer(correct)
        if qtype in ("single", "truefalse"): return ua == ca
        if qtype == "multi": return set(sorted(ua.replace(",", "").replace(" ", ""))) == set(ca)
        return False
    except Exception: return False

def _record_wrong(user_id: int, question_id: int, db: Session):
    wa = db.query(WrongAnswer).filter(WrongAnswer.user_id == user_id, WrongAnswer.question_id == question_id).first()
    if wa:
        wa.wrong_count += 1; wa.last_wrong_at = datetime.now(timezone.utc); wa.is_mastered = False
    else:
        wa = WrongAnswer(user_id=user_id, question_id=question_id); db.add(wa)

@router.post("/review")
def start_review(data: PracticeStartRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Combined review: wrongbook (unmastered) + favorites, deduplicated"""
    # Get wrongbook question IDs (unmastered)
    wrong_records = db.query(WrongAnswer).filter(
        WrongAnswer.user_id == user.id,
        WrongAnswer.is_mastered == False
    ).all()
    wrong_qids = [w.question_id for w in wrong_records]
    
    # Get favorites question IDs
    fav_records = db.query(Favorite).filter(
        Favorite.user_id == user.id
    ).all()
    fav_qids = [f.question_id for f in fav_records]
    
    # Combine and deduplicate
    all_qids = list(set(wrong_qids + fav_qids))
    if not all_qids:
        raise HTTPException(400, "没有需要复习的题目，错题本和收藏夹均为空")
    
    # Build query
    q = db.query(Question).filter(Question.id.in_(all_qids), Question.is_active == True)
    if data.subject_id:
        q = q.filter(Question.subject_id == data.subject_id)
    if data.question_type:
        q = q.filter(Question.type == data.question_type)
    
    pool = q.all()
    if not pool:
        raise HTTPException(400, "没有符合筛选条件的复习题目")
    
    count = min(data.count, len(pool))
    chosen = random.sample(pool, count)
    
    questions = [{
        "id": c.id, "type": c.type, "content": c.content,
        "options": json.loads(c.options) if c.options else [],
        "difficulty": c.difficulty,
        "images": json.loads(c.images) if c.images else [],
        "answer": _normalize_answer(c.answer),
        "explanation": c.explanation,
    } for c in chosen]
    
    record = PracticeRecord(
        user_id=user.id, mode="review",
        subject_id=data.subject_id,
        question_type=data.question_type,
        total_count=count,
    )
    db.add(record); db.commit(); db.refresh(record)
    return {"record_id": record.id, "total": count, "questions": questions}

@router.get("/records/{record_id}/detail")
def record_detail(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(PracticeRecord).filter(PracticeRecord.id == record_id, PracticeRecord.user_id == user.id).first()
    if not record:
        raise HTTPException(404, "记录不存在")
    
    # Parse stored answers
    answers_data = []
    try:
        parsed = json.loads(record.answers or "[]")
        if isinstance(parsed, list):
            answers_data = parsed
        elif isinstance(parsed, dict):
            answers_data = [{"question_id": int(k), "user_answer": v, "is_correct": False} for k, v in parsed.items()]
    except Exception:
        pass

    # Build question details
    details = []
    if answers_data:
        for ans in answers_data:
            q = db.query(Question).get(ans.get("question_id"))
            if not q:
                continue
            details.append({
                "question_id": q.id,
                "content": q.content,
                "type": q.type,
                "options": json.loads(q.options) if q.options else [],
                "answer": _normalize_answer(q.answer),
                "explanation": q.explanation or "",
                "user_answer": ans.get("user_answer", ""),
                "is_correct": ans.get("is_correct", False),
            })
    else:
        # Fallback: show questions from subject/chapter
        qf = db.query(Question).filter(Question.is_active == True)
        if record.subject_id:
            qf = qf.filter(Question.subject_id == record.subject_id)
        if record.chapter_id:
            qf = qf.filter(Question.chapter_id == record.chapter_id)
        if record.question_type:
            qf = qf.filter(Question.type == record.question_type)
        questions = qf.limit(record.total_count or 20).all()
        for qn in questions:
            details.append({
                "question_id": qn.id,
                "content": qn.content,
                "type": qn.type,
                "options": json.loads(qn.options) if qn.options else [],
                "answer": _normalize_answer(qn.answer),
                "explanation": qn.explanation or "",
                "user_answer": "",
                "is_correct": False,
            })
    
    # Get subject name
    subject_name = ""
    if record.subject_id:
        s = db.query(Subject).get(record.subject_id)
        if s: subject_name = s.name
    
    return {
        "id": record.id,
        "subject_name": subject_name,
        "mode": record.mode,
        "question_type": record.question_type,
        "total_count": record.total_count,
        "correct_count": record.correct_count,
        "wrong_count": record.wrong_count,
        "duration_seconds": record.duration_seconds,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "details": details,
    }
