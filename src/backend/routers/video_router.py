from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from orm_utils import orm_to_dict
from database import get_db
from models import VideoCourse, User, VideoProgress
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/videos", tags=["视频课程"])


class VideoOut(BaseModel):
    id: int; title: str; description: str; subject_id: int | None = None
    chapter_id: int | None = None; video_url: str; cover_url: str | None = ""
    duration_seconds: int; sort_order: int; is_published: bool; created_at: str | None = None
    model_config = {"from_attributes": True}

class VideoCreate(BaseModel):
    title: str; description: str = ""; subject_id: int | None = None
    chapter_id: int | None = None; video_url: str; cover_url: str | None = ""
    duration_seconds: int = 0; sort_order: int = 0

class ProgressUpdate(BaseModel):
    current_time: int = 0
    duration: int = 0


@router.get("", response_model=dict)
def list_videos(subject_id: int = Query(None), chapter_id: int = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20), published_only: bool = Query(False), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    q = db.query(VideoCourse).order_by(VideoCourse.sort_order, VideoCourse.id.desc())
    if subject_id: q = q.filter(VideoCourse.subject_id == subject_id)
    if chapter_id: q = q.filter(VideoCourse.chapter_id == chapter_id)
    if published_only: q = q.filter(VideoCourse.is_published == True)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    result_list = []
    for v in items:
        d = orm_to_dict(v)
        if d.get("cover_url") is None: d["cover_url"] = ""
        result_list.append(VideoOut.model_validate(d))
    return {"total": total, "items": result_list}

@router.post("", response_model=VideoOut)
@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = "", subject_id: int | None = None,
    db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher")),
):
    import os, uuid
    ALLOWED = {"mp4","webm","ogg","avi","mov","mkv"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        raise HTTPException(400, f"不支持的格式：.{ext}")
    contents = await file.read()
    if len(contents) > 200 * 1024 * 1024:
        raise HTTPException(400, "文件超过200MB限制")
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = "uploads/videos"
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, safe_name)
    with open(filepath, "wb") as f: f.write(contents)
    v = VideoCourse(
        title=title or file.filename, video_url=f"/{upload_dir}/{safe_name}",
        subject_id=subject_id,
    )
    db.add(v); db.commit(); db.refresh(v)
    return VideoOut.model_validate(orm_to_dict(v))

def create_video(data: VideoCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    v = VideoCourse(**data.model_dump())
    db.add(v); db.commit(); db.refresh(v)
    return v

@router.put("/{video_id}", response_model=VideoOut)
def update_video(video_id: int, data: VideoCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    v = db.query(VideoCourse).get(video_id)
    if not v: raise HTTPException(404, "视频不存在")
    for k, val in data.model_dump().items(): setattr(v, k, val)
    db.commit(); db.refresh(v)
    return v

@router.delete("/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    v = db.query(VideoCourse).get(video_id)
    if not v: raise HTTPException(404, "视频不存在")
    db.delete(v); db.commit()
    return {"ok": True}

@router.put("/{video_id}/publish")
def toggle_publish(video_id: int, is_published: bool = True, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    v = db.query(VideoCourse).get(video_id)
    if not v: raise HTTPException(404, "视频不存在")
    v.is_published = is_published; db.commit()
    return {"ok": True}


# --- 播放进度 ---

@router.get("/{video_id}/progress")
def get_progress(video_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vp = db.query(VideoProgress).filter(VideoProgress.user_id == user.id, VideoProgress.video_id == video_id).first()
    if not vp: return {"current_time": 0, "duration": 0, "is_finished": False}
    return {"current_time": vp.current_time, "duration": vp.duration, "is_finished": vp.is_finished, "updated_at": vp.updated_at.isoformat() if vp.updated_at else None}

@router.post("/{video_id}/progress")
def save_progress(video_id: int, data: ProgressUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vp = db.query(VideoProgress).filter(VideoProgress.user_id == user.id, VideoProgress.video_id == video_id).first()
    if not vp:
        vp = VideoProgress(user_id=user.id, video_id=video_id, current_time=data.current_time, duration=data.duration)
        db.add(vp)
    else:
        vp.current_time = data.current_time
        vp.duration = data.duration
        vp.is_finished = data.current_time >= data.duration - 5 if data.duration > 0 else False
        vp.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
