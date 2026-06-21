import os, uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from orm_utils import orm_to_dict, sanitize_for_model
from database import get_db
from models import Resource, User
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/resources", tags=["学习资料"])

MAX_SIZES = {"xls":10*1024*1024,"xlsx":10*1024*1024,"pdf":50*1024*1024,"docx":50*1024*1024,"doc":50*1024*1024,"ppt":50*1024*1024,"pptx":50*1024*1024,"zip":50*1024*1024,"rar":50*1024*1024,"mp4":200*1024*1024,"avi":200*1024*1024,"mov":200*1024*1024,"jpg":50*1024*1024,"jpeg":50*1024*1024,"png":50*1024*1024,"webp":50*1024*1024,"gif":50*1024*1024}
UPLOAD_DIR = "uploads"
RESOURCE_DEFAULTS = {"file_type": "", "file_size": 0, "download_count": 0, "sort_order": 0, "is_published": True, "created_by": "", "created_at": ""}
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ResourceOut(BaseModel):
    id: int; title: str; description: str; subject_id: int | None = None
    file_url: str; file_type: str = ""; file_size: int | None = 0; download_count: int | None = 0
    sort_order: int | None = 0; is_published: bool | None = True; created_by: str = ""; created_at: str = ""
    model_config = {"from_attributes": True}

class ResourceCreate(BaseModel):
    title: str; description: str = ""; subject_id: int | None = None
    file_url: str; file_type: str = ""; file_size: int = 0; sort_order: int = 0


@router.get("", response_model=dict)
def list_resources(subject_id: int = Query(None), keyword: str = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    q = db.query(Resource).filter(Resource.is_published == True).order_by(Resource.sort_order, Resource.id.desc())
    if subject_id: q = q.filter(Resource.subject_id == subject_id)
    if keyword: q = q.filter(Resource.title.contains(keyword))
    total = q.count(); items = q.offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "items": [ResourceOut.model_validate(sanitize_for_model(orm_to_dict(r), RESOURCE_DEFAULTS)) for r in items]}


@router.get("/manage", response_model=dict)
def list_all_resources(page: int = Query(1, ge=1), page_size: int = Query(20), db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    q = db.query(Resource).order_by(Resource.sort_order, Resource.id.desc())
    total = q.count(); items = q.offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "items": [ResourceOut.model_validate(sanitize_for_model(orm_to_dict(r), RESOURCE_DEFAULTS)) for r in items]}


@router.post("/upload")
async def upload_resource(
    file: UploadFile = File(...),
    title: str = "", subject_id: int | None = None,
    db: Session = Depends(get_db), user: User = Depends(require_role("admin", "teacher")),
):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in MAX_SIZES:
        raise HTTPException(400, f"不支持的文件类型：.{ext}")
    contents = await file.read()
    if len(contents) > MAX_SIZES[ext]:
        max_mb = MAX_SIZES[ext] / 1048576
        raise HTTPException(400, f"文件超出最大限制 {max_mb:.0f}MB")
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    with open(filepath, "wb") as f: f.write(contents)
    r = Resource(
        title=title or file.filename, file_url=f"/uploads/{safe_name}",
        file_type=ext, file_size=len(contents), subject_id=subject_id,
        created_by=user.fullname or user.username,
    )
    db.add(r); db.commit(); db.refresh(r)
    return ResourceOut.model_validate(orm_to_dict(r))


@router.post("", response_model=ResourceOut)
def create_resource(data: ResourceCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    r = Resource(**data.model_dump(), created_by=_.fullname or _.username)
    db.add(r); db.commit(); db.refresh(r)
    return r


@router.put("/{res_id}", response_model=ResourceOut)
def update_resource(res_id: int, data: ResourceCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    r = db.query(Resource).get(res_id)
    if not r: raise HTTPException(404, "资料不存在")
    for k, v in data.model_dump().items(): setattr(r, k, v)
    db.commit(); db.refresh(r)
    return r


@router.delete("/{res_id}")
def delete_resource(res_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    r = db.query(Resource).get(res_id)
    if not r: raise HTTPException(404, "资料不存在")
    db.delete(r); db.commit()
    return {"ok": True}


@router.put("/{res_id}/publish")
def toggle_publish(res_id: int, is_published: bool = True, db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    r = db.query(Resource).get(res_id)
    if not r: raise HTTPException(404, "资料不存在")
    r.is_published = is_published; db.commit()
    return {"ok": True}


@router.post("/{res_id}/download")
def download_resource(res_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    r = db.query(Resource).get(res_id)
    if not r: raise HTTPException(404, "资料不存在")
    r.download_count += 1; db.commit()
    return {"file_url": r.file_url, "title": r.title, "file_type": r.file_type}
