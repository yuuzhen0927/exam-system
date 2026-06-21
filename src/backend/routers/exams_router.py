import json, random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from orm_utils import orm_to_dict
from routers.certificates_router import auto_check_after_exam
from models import Exam, ExamTemplate, ExamResult, Question, Certificate, UserCertificate, AbnormalReport, User, RetakeApplication
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/exams", tags=["考试管理"])


class ExamOut(BaseModel):
    id: int; title: str; description: str; mode: str; duration_minutes: int
    total_score: int; pass_score: int; question_count: int = 0
    is_published: bool; shuffle_questions: bool = True; shuffle_options: bool = True; max_tab_switches: int = 3
    start_time: str | None = None; end_time: str | None = None; created_at: str | None = None
    invite_code: str | None = None
    model_config = {"from_attributes": True}

class ExamCreate(BaseModel):
    title: str; description: str = ""; mode: str = "mock"
    duration_minutes: int = 60; total_score: int = 100; pass_score: int = 60
    question_ids: list[int] = []
    shuffle_questions: bool = True; shuffle_options: bool = True; max_tab_switches: int = 3
    start_time: str | None = None; end_time: str | None = None
    invite_code: str | None = None

class ExamGenerateRequest(BaseModel):
    title: str; description: str = ""; mode: str = "mock"
    duration_minutes: int = 60; total_score: int = 100; pass_score: int = 60
    subject_ids: list[int] = []
    chapter_ids: list[int] = []
    specialties: list[str] = []
    type_config: dict = {}
    difficulty_min: int = 1
    difficulty_max: int = 5
    shuffle_questions: bool = True; shuffle_options: bool = True
    max_tab_switches: int = 3
    start_time: str | None = None; end_time: str | None = None
    invite_code: str | None = None
    save_template: bool = False

class SubmitAnswer(BaseModel):
    answers: dict


@router.get("", response_model=dict)
def list_exams(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), mode: str = Query(None),
               db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    q = db.query(Exam).order_by(Exam.id.desc())
    if mode: q = q.filter(Exam.mode == mode)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": [_exam_out(e) for e in items]}

@router.get("/my-results")
def my_results(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    results = db.query(ExamResult).filter(ExamResult.user_id == user.id).order_by(ExamResult.id.desc()).all()
    return [{"id": r.id, "exam_id": r.exam_id, "exam_title": r.exam.title if r.exam else "", "auto_score": r.auto_score, "manual_score": r.manual_score, "total_score": r.total_score, "passed": r.passed, "mode": r.exam.mode if r.exam else "", "finished_at": r.finished_at.isoformat() if r.finished_at else None} for r in results]


@router.get("/retake-applications")
def list_retake_applications(db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    """管理员查看所有重考申请"""
    apps = db.query(RetakeApplication).order_by(RetakeApplication.id.desc()).all()
    return [{
        "id": a.id, "exam_id": a.exam_id, "user_id": a.user_id,
        "username": a.user.username, "fullname": a.user.fullname,
        "exam_title": a.exam.title if a.exam else "",
        "reason": a.reason, "status": a.status,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in apps]

@router.post("/retake-applications/{app_id}/approve")
def approve_retake(app_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    """批准重考申请"""
    app = db.query(RetakeApplication).get(app_id)
    if not app:
        raise HTTPException(404, "申请不存在")
    app.status = "approved"
    # Delete old result to allow retake
    db.query(ExamResult).filter(
        ExamResult.exam_id == app.exam_id,
        ExamResult.user_id == app.user_id
    ).delete()
    db.commit()
    return {"message": "已批准重考"}

@router.post("/retake-applications/{app_id}/reject")
def reject_retake(app_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    """拒绝重考申请"""
    app = db.query(RetakeApplication).get(app_id)
    if not app:
        raise HTTPException(404, "申请不存在")
    app.status = "rejected"
    db.commit()
    return {"message": "已拒绝重考"}
@router.get("/pending-grading")
def pending_grading(page: int = Query(1, ge=1), page_size: int = Query(20), db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    results = db.query(ExamResult).filter(ExamResult.manual_score.is_(None)).order_by(ExamResult.id.desc()).all()
    items = []
    for r in results:
        try: qids = json.loads(r.exam.question_ids)
        except Exception: continue
        has_composite = db.query(Question).filter(Question.id.in_(qids), Question.type == "composite").count() > 0
        if has_composite:
            per_q = r.exam.total_score / len(qids) if qids and r.exam else 0
            items.append({
                "id": r.id, "exam_id": r.exam_id, "exam_title": r.exam.title if r.exam else "",
                "user_id": r.user_id, "username": r.user.username, "fullname": r.user.fullname,
                "auto_score": r.auto_score, "total_score": r.total_score,
                "per_question_score": round(per_q, 1),
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            })

    total = len(items)
    start = (page - 1) * page_size
    return {"total": total, "page": page, "page_size": page_size, "items": items[start:start + page_size]}

@router.get("/results/{result_id}/detail")
def grading_detail(result_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    r = db.query(ExamResult).get(result_id)
    if not r: raise HTTPException(404, "结果不存在")

    try:
        qids = json.loads(r.exam.question_ids)
        answers = json.loads(r.answers)
    except Exception:
        raise HTTPException(500, "数据异常")

    questions = db.query(Question).filter(Question.id.in_(qids)).all()
    detail = []
    for q in questions:
        if q.type != "composite": continue
        detail.append({
            "question_id": q.id, "type": q.type, "content": q.content,
            "reference_answer": _parse_answer(q.answer), "explanation": q.explanation,
            "user_answer": answers.get(str(q.id), ""),
            "score": None,
        })
    return {"result_id": result_id, "auto_score": r.auto_score, "questions": detail}


@router.post("/results/{result_id}/grade")
def submit_grading(result_id: int, scores: dict, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    r = db.query(ExamResult).get(result_id)
    if not r: raise HTTPException(404, "结果不存在")

    manual_total = sum(float(v) for v in scores.values())
    r.manual_score = round(manual_total, 1)
    r.passed = (r.auto_score + r.manual_score) >= (r.exam.pass_score if r.exam else 0)
    db.commit()
    return {"ok": True, "auto_score": r.auto_score, "manual_score": r.manual_score, "passed": r.passed}

@router.get("/results/{result_id}/review")
def review_exam(result_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.query(ExamResult).get(result_id)
    if not r: raise HTTPException(404, "结果不存在")
    if r.user_id != user.id and user.role not in ("admin", "teacher"):
        raise HTTPException(403, "无权查看")
    try: qids = json.loads(r.exam.question_ids); user_answers = json.loads(r.answers)
    except Exception: raise HTTPException(500, "数据异常")
    questions = db.query(Question).filter(Question.id.in_(qids)).all()
    qmap = {q.id: q for q in questions}
    review = []
    for qid in qids:
        q = qmap.get(qid)
        if not q: continue
        ua = user_answers.get(str(qid), "")
        review.append({
            "question_id": q.id, "type": q.type, "content": q.content,
            "options": json.loads(q.options) if q.options else [],
            "user_answer": ua, "correct_answer": q.answer,
            "explanation": q.explanation,
            "is_correct": _judge(q.type, q.answer, ua) if q.type != "composite" else None,
        })
    return {
        "result_id": r.id, "exam_title": r.exam.title if r.exam else "",
        "auto_score": r.auto_score, "manual_score": r.manual_score,
        "total_score": r.total_score, "passed": r.passed,
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        "questions": review,
    }
@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")
    return _exam_out(e)

@router.post("", response_model=ExamOut)
def create_exam(data: ExamCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    e = Exam(**data.model_dump())
    e.question_ids = json.dumps(data.question_ids, ensure_ascii=False)
    if data.start_time: e.start_time = datetime.fromisoformat(data.start_time)
    if data.end_time: e.end_time = datetime.fromisoformat(data.end_time)
    db.add(e); db.commit(); db.refresh(e)
    return _exam_out(e)

@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, data: ExamCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")
    for k, v in data.model_dump(exclude={"question_ids", "start_time", "end_time"}).items():
        setattr(e, k, v)
    e.question_ids = json.dumps(data.question_ids, ensure_ascii=False)
    e.start_time = datetime.fromisoformat(data.start_time) if data.start_time else None
    e.end_time = datetime.fromisoformat(data.end_time) if data.end_time else None
    db.commit(); db.refresh(e)
    return _exam_out(e)

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")
    db.delete(e); db.commit()
    return {"ok": True}

@router.put("/{exam_id}/publish")
def toggle_publish(exam_id: int, is_published: bool = Query(True), db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")
    e.is_published = is_published; db.commit()
    return {"ok": True, "is_published": is_published}


@router.post("/generate", response_model=ExamOut)
def generate_exam(data: ExamGenerateRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin", "teacher"))):
    q = db.query(Question).filter(Question.is_active == True)
    if data.subject_ids: q = q.filter(Question.subject_id.in_(data.subject_ids))
    if data.chapter_ids: q = q.filter(Question.chapter_id.in_(data.chapter_ids))
    if data.specialties: q = q.filter(Question.specialty.in_(data.specialties))
    q = q.filter(Question.difficulty >= data.difficulty_min, Question.difficulty <= data.difficulty_max)

    selected_ids = []
    used_ids = set()
    for qtype, count in data.type_config.items():
        if count <= 0:
            continue
        pool = [r for r in q.filter(Question.type == qtype).all() if r.id not in used_ids]
        if not pool:
            continue
        take = min(count, len(pool))
        chosen = random.sample(pool, take)
        for c in chosen:
            selected_ids.append(c.id)
            used_ids.add(c.id)

    if len(selected_ids) == 0:
        raise HTTPException(400, "所选范围内没有可用题目，请调整筛选条件")

    exam = Exam(
        title=data.title, description=data.description, mode=data.mode,
        duration_minutes=data.duration_minutes, total_score=data.total_score,
        pass_score=data.pass_score, question_ids=json.dumps(selected_ids, ensure_ascii=False),
        shuffle_questions=data.shuffle_questions, shuffle_options=data.shuffle_options,
        max_tab_switches=data.max_tab_switches,
        start_time=datetime.fromisoformat(data.start_time) if data.start_time else None,
        end_time=datetime.fromisoformat(data.end_time) if data.end_time else None,
        invite_code=data.invite_code or None,
    )
    db.add(exam); db.commit(); db.refresh(exam)
    log_operation(db, user.id, user.username, "create", "exam", exam.id, detail=f"创建试卷: {exam.title}")

    if data.save_template:
        tmpl = ExamTemplate(
            exam_id=exam.id,
            subject_ids=json.dumps(data.subject_ids), chapter_ids=json.dumps(data.chapter_ids),
            specialties=json.dumps(data.specialties), type_config=json.dumps(data.type_config),
            difficulty_range=json.dumps([data.difficulty_min, data.difficulty_max]),
        )
        db.add(tmpl); db.commit()

    return _exam_out(exam)


@router.get("/{exam_id}/take")
def take_exam(exam_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")
    if not e.is_published: raise HTTPException(400, "考试未发布")

    existing = db.query(ExamResult).filter(ExamResult.exam_id == exam_id, ExamResult.user_id == user.id, ExamResult.finished_at.isnot(None)).first()
    if existing and e.mode == "formal":
        # Check if user has an approved retake application
        retake = db.query(RetakeApplication).filter(
            RetakeApplication.exam_id == exam_id,
            RetakeApplication.user_id == user.id,
            RetakeApplication.status == "approved"
        ).first()
        if not retake:
            raise HTTPException(400, "你已参加过此正式考试，需申请重考方可再次参加")
        # Delete old result to allow retake
        db.query(ExamResult).filter(ExamResult.exam_id == exam_id, ExamResult.user_id == user.id).delete()
        db.commit()


    try:
        qids = json.loads(e.question_ids)
        if e.shuffle_questions: random.shuffle(qids)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(500, "考试题目数据异常")

    questions = db.query(Question).filter(Question.id.in_(qids), Question.is_active == True).all()
    qmap = {q.id: q for q in questions}
    ordered = [qmap[qid] for qid in qids if qid in qmap]

    questions_data = []
    for q in ordered:
        opts = json.loads(q.options) if q.options else []
        if e.shuffle_options and q.type in ("single", "multi", "blank"): random.shuffle(opts)
        questions_data.append({
            "id": q.id, "type": q.type, "content": q.content,
            "options": opts, "difficulty": q.difficulty,
            "images": json.loads(q.images) if q.images else [],
        })

    return {
        "id": e.id, "title": e.title, "description": e.description,
        "mode": e.mode, "duration_minutes": e.duration_minutes,
        "total_score": e.total_score, "pass_score": e.pass_score,
        "max_tab_switches": e.max_tab_switches, "questions": questions_data,
    }


@router.post("/{exam_id}/submit")
def submit_exam(exam_id: int, data: SubmitAnswer, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")

    existing = db.query(ExamResult).filter(ExamResult.exam_id == exam_id, ExamResult.user_id == user.id, ExamResult.finished_at.isnot(None)).first()
    if existing:
        if e.mode == "formal":
            raise HTTPException(400, "你已提交过此正式考试")
        else:
            # Mock exam: delete old result to allow retake
            db.query(ExamResult).filter(ExamResult.exam_id == exam_id, ExamResult.user_id == user.id).delete()
            db.commit()

    try: qids = json.loads(e.question_ids)
    except Exception: raise HTTPException(500, "考试题目数据异常")

    questions = db.query(Question).filter(Question.id.in_(qids)).all()
    auto_score = 0.0
    per_q = e.total_score / len(qids) if qids else 0
    has_composite = False

    for q in questions:
        if q.type == "composite":
            has_composite = True
            continue
        user_ans = data.answers.get(str(q.id), "")
        if _judge(q.type, q.answer, user_ans):
            auto_score += per_q

    result = db.query(ExamResult).filter(ExamResult.exam_id == exam_id, ExamResult.user_id == user.id, ExamResult.finished_at.is_(None)).order_by(ExamResult.id.desc()).first()
    if result:
        result.answers = json.dumps(data.answers, ensure_ascii=False)
        result.auto_score = round(auto_score, 1)
        result.total_score = e.total_score
        result.passed = auto_score >= e.pass_score if not has_composite else False
        result.finished_at = datetime.now(timezone.utc)
        if not has_composite:
            result.manual_score = 0
    else:
        result = ExamResult(
            exam_id=exam_id, user_id=user.id,
            answers=json.dumps(data.answers, ensure_ascii=False),
            auto_score=round(auto_score, 1), total_score=e.total_score,
            manual_score=0 if not has_composite else None,
            passed=auto_score >= e.pass_score if not has_composite else False,
            finished_at=datetime.now(timezone.utc),
        )
        db.add(result)
    db.commit(); db.refresh(result)
    # Auto-issue certificate via auto_check
    if e.mode == "formal" and result.passed:
        try:
            auto_check_after_exam(result.id, db)
        except Exception:
            pass  # Don't block exam submission on cert failure
    


    return {
        "ok": True,
        "auto_score": result.auto_score,
        "manual_score": result.manual_score,
        "total_score": result.total_score,
        "passed": result.passed,
        "tab_switches": result.tab_switches,
        "is_cheating": result.is_cheating,
    }


@router.post("/apply-certificate")
def apply_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Client applies for a certificate - system checks eligibility"""
    cert = db.query(Certificate).get(certificate_id)
    if not cert:
        raise HTTPException(404, "证书不存在")

    # Check already issued
    already = db.query(UserCertificate).filter(
        UserCertificate.certificate_id == certificate_id,
        UserCertificate.user_id == user.id,
        UserCertificate.is_revoked == False
    ).first()
    if already:
        return {"ok": True, "message": "已拥有此证书", "certificate_no": already.certificate_no}

    if cert.cert_type == "practice" and cert.chapter_id:
        # Practice certificate: check chapter pass rate
        from models import PracticeRecord
        records = db.query(PracticeRecord).filter(
            PracticeRecord.user_id == user.id,
            PracticeRecord.chapter_id == cert.chapter_id
        ).all()
        if not records:
            raise HTTPException(400, "您尚未练习过此章节")
        total_q = sum(r.total_count or 0 for r in records)
        correct_q = sum(r.correct_count or 0 for r in records)
        if total_q < 10:
            raise HTTPException(400, "练习数量不足（至少10题）")
        rate = correct_q / total_q * 100 if total_q > 0 else 0
        if rate < 60:
            raise HTTPException(400, f"正确率{rate:.1f}%不足60%，暂不可申请")

    elif cert.cert_type == "exam":
        # Exam certificate: check if passed any formal exam
        passed = db.query(ExamResult).join(Exam).filter(
            ExamResult.user_id == user.id,
            ExamResult.passed == True,
            Exam.mode == "formal"
        ).first()
        if not passed:
            raise HTTPException(400, "您尚未通过任何正式考试")

    import uuid
    uc = UserCertificate(
        certificate_id=certificate_id,
        user_id=user.id,
        certificate_no=f"CERT-{uuid.uuid4().hex[:12].upper()}"
    )
    db.add(uc)
    db.commit()
    db.refresh(uc)
    return {"ok": True, "certificate_no": uc.certificate_no, "message": "证书申请成功！"}

@router.post("/{exam_id}/report-tab-switch")
def report_tab_switch(exam_id: int, count: int = Query(1), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(Exam).get(exam_id)
    if not e: raise HTTPException(404, "考试不存在")

    result = db.query(ExamResult).filter(ExamResult.exam_id == exam_id, ExamResult.user_id == user.id, ExamResult.finished_at.is_(None)).order_by(ExamResult.id.desc()).first()
    if not result:
        result = ExamResult(exam_id=exam_id, user_id=user.id, answers="{}", auto_score=0, total_score=e.total_score, tab_switches=count, started_at=datetime.now(timezone.utc))
        db.add(result)
    else:
        result.tab_switches += count
    if result.tab_switches >= e.max_tab_switches:
        result.is_cheating = True
        db.add(AbnormalReport(exam_result_id=result.id, user_id=user.id, reason="tab_switch", detail=f"切屏{result.tab_switches}次"))
    db.commit()
    return {"ok": True, "total_switches": result.tab_switches, "is_cheating": result.is_cheating}




@router.get("/{exam_id}/results")
def get_results(exam_id: int, page: int = Query(1, ge=1), page_size: int = Query(50), db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    q = db.query(ExamResult).filter(ExamResult.exam_id == exam_id).order_by(ExamResult.auto_score.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [{"id": r.id, "user_id": r.user_id, "username": r.user.username if r.user else "", "fullname": r.user.fullname if r.user else "", "auto_score": r.auto_score, "manual_score": r.manual_score, "total_score": r.total_score, "passed": r.passed, "is_cheating": r.is_cheating, "finished_at": r.finished_at.isoformat() if r.finished_at else None} for r in items]}





def _exam_out(e: Exam) -> ExamOut:
    d = orm_to_dict(e)
    for k, v in [("shuffle_questions", True), ("shuffle_options", True), ("max_tab_switches", 3)]:
        if d.get(k) is None: d[k] = v
    out = ExamOut.model_validate(d)
    try: out.question_count = len(json.loads(e.question_ids))
    except Exception: out.question_count = 0
    return out

def _parse_answer(raw: str) -> str:
    if not raw: return ''
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return chr(10).join(str(item) for item in parsed)
        return str(parsed)
    except (json.JSONDecodeError, TypeError):
        return raw

def _judge(qtype: str, correct: str, user_answer: str) -> bool:
    try:
        ua = user_answer.strip()
        ca = correct.strip()
        if qtype in ("single", "truefalse"): return ua.upper() == ca.upper()
        if qtype == "multi":
            us = set(sorted(ua.upper().replace(",", "").replace(" ", "")))
            cs = set(sorted(ca.upper().replace(",", "").replace(" ", "")))
            return us == cs
        if qtype == "blank":
            # Normalize: remove spaces, lowercase, handle multiple accepted answers separated by |
            ua_norm = ua.replace(" ", "").lower()
            for accepted in ca.split("|"):
                if accepted.strip().replace(" ", "").lower() == ua_norm:
                    return True
            return False
        return False
    except Exception:
        return False


# --- 重考申请 ---
class RetakeRequest(BaseModel):
    reason: str = ""

@router.post("/{exam_id}/apply-retake")
def apply_retake(exam_id: int, data: RetakeRequest = RetakeRequest(), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """申请重考正式考试"""
    exam = db.query(Exam).get(exam_id)
    if not exam:
        raise HTTPException(404, "试卷不存在")
    if exam.mode != "formal":
        raise HTTPException(400, "仅正式考试支持重考申请")
    
    # Check if user has already taken this exam
    existing = db.query(ExamResult).filter(
        ExamResult.exam_id == exam_id,
        ExamResult.user_id == user.id
    ).first()
    if not existing:
        raise HTTPException(400, "你尚未参加此考试")
    
    # Check if there's already a pending retake application
    existing_request = db.query(RetakeApplication).filter(
        RetakeApplication.exam_id == exam_id,
        RetakeApplication.user_id == user.id,
        RetakeApplication.status == "pending"
    ).first()
    if existing_request:
        raise HTTPException(400, "已有待审核的重考申请")
    
    app = RetakeApplication(
        exam_id=exam_id, user_id=user.id,
        reason=data.reason, status="pending"
    )
    db.add(app); db.commit()
    return {"code": 200, "message": "重考申请已提交"}


# 考试邀请码验证
@router.post("/verify-invite-code")
def verify_invite_code(code: str = Query(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(Exam).filter(Exam.invite_code == code, Exam.is_published == True).first()
    if not e: return {"code": 404, "message": "邀请码无效或考试未发布"}
    # Check time validity
    now = datetime.now(timezone.utc)
    if e.start_time and now < e.start_time: return {"code": 403, "message": "考试尚未开始"}
    if e.end_time and now > e.end_time: return {"code": 403, "message": "考试已结束"}
    # Check if user already took this exam (formal only)
    if e.mode == "formal":
        existing = db.query(ExamResult).filter(ExamResult.exam_id == e.id, ExamResult.user_id == user.id).first()
        if existing: return {"code": 400, "message": "你已参加过该考试，需申请重考"}
    return {"code": 200, "data": _exam_out(e)}
    return {"message": "重考申请已提交"}
