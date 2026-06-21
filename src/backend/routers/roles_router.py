from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from database import get_db
from models import Role, User
from auth import get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/roles", tags=["role-management"])


class RoleOut(BaseModel):
    id: int
    name: str
    description: str
    is_manager: bool
    is_system: bool
    sort_order: int
    created_at: str | None = None
    model_config = {"from_attributes": True}

    @field_validator("created_at", mode="before")
    @classmethod
    def dt_to_str(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)


class RoleCreate(BaseModel):
    name: str
    description: str = ""
    is_manager: bool = False
    sort_order: int = 0


@router.get("")
def list_roles(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    roles = db.query(Role).order_by(Role.sort_order, Role.id).all()
    return [RoleOut.model_validate(r) for r in roles]


@router.post("", response_model=RoleOut)
def create_role(data: RoleCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    if db.query(Role).filter(Role.name == data.name).first():
        raise HTTPException(400, "Role name already exists")
    r = Role(**data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: int, data: RoleCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    r = db.query(Role).get(role_id)
    if not r:
        raise HTTPException(404, "Role not found")
    if r.is_system:
        raise HTTPException(400, "System roles cannot be edited")
    existing = db.query(Role).filter(Role.name == data.name, Role.id != role_id).first()
    if existing:
        raise HTTPException(400, "Role name already exists")
    for k, v in data.model_dump().items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    r = db.query(Role).get(role_id)
    if not r:
        raise HTTPException(404, "Role not found")
    if r.is_system:
        raise HTTPException(400, "System roles cannot be deleted")
    # Reassign users with this role to student
    users = db.query(User).filter(User.role == r.name).all()
    for u in users:
        u.role = "student"
    db.delete(r)
    db.commit()
    return {"ok": True}
