from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Question, ExamResult, PracticeRecord, WrongAnswer, Subject, QuestionFeedback, AbnormalReport
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/analytics", tags=["数据分析"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), _=Depends(require_role("admin", "teacher"))):
    """整体数据概览"""
    total_users = db.query(User).count()
    active_users_today = db.query(User).filter(User.last_active_at.isnot(None)).count()
    total_questions = db.query(Question).filter(Question.is_active == True).count()
    total_exams = db.query(ExamResult).count()
    total_practices = db.query(PracticeRecord).count()
    total_feedbacks_pending = db.query(QuestionFeedback).filter(QuestionFeedback.status == "pending").count()
    total_abnormal = db.query(AbnormalReport).count()

    return {
        "total_users": total_users, "active_users_today": active_users_today,
        "total_questions": total_questions, "total_exams": total_exams,
        "total_practices": total_practices,
        "total_feedbacks_pending": total_feedbacks_pending,
        "total_abnormal": total_abnormal,
    }


@router.get("/subjects")
def subject_analytics(db: Session = Depends(get_db), _=Depends(require_role("admin", "teacher"))):
    """各科目题目统计"""
    subjects = db.query(Subject).all()
    result = []
    for s in subjects:
        q_count = db.query(Question).filter(Question.subject_id == s.id, Question.is_active == True).count()
        result.append({"id": s.id, "name": s.name, "question_count": q_count})
    return result


@router.get("/question-accuracy")
def question_accuracy(limit: int = Query(20), db: Session = Depends(get_db), _=Depends(require_role("admin", "teacher"))):
    """题目正确率排行（最低的在前）"""
    wrongs = db.query(
        WrongAnswer.question_id,
        func.count(WrongAnswer.id).label("wrong_count"),
        func.sum(WrongAnswer.wrong_count).label("total_wrongs"),
    ).group_by(WrongAnswer.question_id).order_by(func.sum(WrongAnswer.wrong_count).desc()).limit(limit).all()

    result = []
    for w in wrongs:
        qst = db.query(Question).get(w.question_id)
        if not qst: continue
        result.append({
            "question_id": w.question_id,
            "content": qst.content[:100],
            "type": qst.type,
            "subject_name": qst.subject.name if qst.subject else "",
            "wrong_count": w.wrong_count,
            "total_wrongs": w.total_wrongs,
        })
    return result


@router.get("/user-activity")
def user_activity(page: int = Query(1, ge=1), page_size: int = Query(50), db: Session = Depends(get_db), _=Depends(require_role("admin", "teacher"))):
    """用户活跃度"""
    q = db.query(User).order_by(User.last_active_at.desc().nullslast())
    total = q.count()
    users = q.offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for u in users:
        practice_count = db.query(PracticeRecord).filter(PracticeRecord.user_id == u.id).count()
        exam_count = db.query(ExamResult).filter(ExamResult.user_id == u.id).count()
        result.append({
            "id": u.id, "username": u.username, "fullname": u.fullname, "role": u.role,
            "is_active": u.is_active, "last_active_at": u.last_active_at.isoformat() if u.last_active_at else None,
            "practice_count": practice_count, "exam_count": exam_count,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return {"total": total, "items": result}



@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Return daily practice counts for the last 365 days as a list of {date, count}."""
    from datetime import datetime, timedelta, timezone
    from models import PracticeRecord
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=365)
    rows = (
        db.query(
            func.date(PracticeRecord.created_at).label("date"),
            func.count(PracticeRecord.id).label("count")
        )
        .filter(PracticeRecord.created_at >= start)
        .group_by(func.date(PracticeRecord.created_at))
        .order_by("date")
        .all()
    )
    result = [{"date": str(row.date), "count": row.count} for row in rows]
    return result
@router.get("/weak-points")
def weak_points(db: Session = Depends(get_db), _=Depends(require_role("admin", "teacher"))):
    """知识点薄弱点分析（按章节聚合错题）"""
    wrongs = db.query(
        WrongAnswer.question_id,
        func.count(WrongAnswer.id).label("count"),
    ).group_by(WrongAnswer.question_id).order_by(func.count(WrongAnswer.id).desc()).limit(30).all()

    chapter_stats = {}
    for w in wrongs:
        qst = db.query(Question).get(w.question_id)
        if not qst or not qst.chapter_id: continue
        key = f"{qst.subject.name if qst.subject else ''} > {qst.chapter.name if qst.chapter else ''}"
        if key not in chapter_stats:
            chapter_stats[key] = {"chapter": key, "wrong_total": 0, "question_count": 0}
        chapter_stats[key]["wrong_total"] += w.count
        chapter_stats[key]["question_count"] += 1

    return sorted(chapter_stats.values(), key=lambda x: x["wrong_total"], reverse=True)

@router.get("/leaderboard")
def get_leaderboard(limit: int = 20, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from sqlalchemy import func
    results = db.query(
        ExamResult.user_id,
        func.max(ExamResult.auto_score + func.coalesce(ExamResult.manual_score, 0)).label('best_score'),
        func.count(ExamResult.id).label('exam_count'),
        func.avg(ExamResult.auto_score + func.coalesce(ExamResult.manual_score, 0)).label('avg_score'),
    ).filter(ExamResult.finished_at.isnot(None)).group_by(ExamResult.user_id).order_by(func.max(ExamResult.auto_score + func.coalesce(ExamResult.manual_score, 0)).desc()).limit(limit).all()

    board = []
    for i, r in enumerate(results):
        user = db.query(User).get(r.user_id)
        board.append({
            'rank': i + 1,
            'username': user.username if user else '',
            'fullname': user.fullname if user else '',
            'best_score': round(r.best_score, 1),
            'avg_score': round(r.avg_score, 1) if r.avg_score else 0,
            'exam_count': r.exam_count,
        })
    return board

@router.get("/score-distribution")
def score_distribution(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    results = db.query(ExamResult).filter(ExamResult.finished_at.isnot(None)).all()
    buckets = {f"{i}-{i+10}": 0 for i in range(0, 100, 10)}
    for r in results:
        score = (r.auto_score or 0) + (r.manual_score or 0)
        total = r.total_score or 100
        pct = score / total * 100
        bucket = int(pct // 10) * 10
        if bucket >= 100: bucket = 90
        key = f"{bucket}-{bucket+10}"
        if key in buckets:
            buckets[key] += 1
    return [{"range": k, "count": v} for k, v in buckets.items()]
