from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import User
from auth import hash_password, get_current_user, require_role
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/users", tags=["用户管理"])


class UserOut(BaseModel):
    id: int
    username: str
    fullname: str
    role: str
    is_active: bool
    last_active_at: str | None = None
    created_at: str | None = None
    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_obj(cls, u):
        return cls(
            id=u.id, username=u.username, fullname=u.fullname,
            role=u.role, is_active=u.is_active,
            last_active_at=u.last_active_at.isoformat() if u.last_active_at else None,
            created_at=u.created_at.isoformat() if u.created_at else None,
        )


class UserUpdate(BaseModel):
    fullname: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None


@router.get("")
def list_users(role: str = Query(None), db: Session = Depends(get_db), _: User = Depends(require_role("admin", "teacher"))):
    q = db.query(User)
    if role: q = q.filter(User.role == role)
    return [UserOut.from_orm_obj(u) for u in q.all()]


@router.put("/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    user = db.query(User).get(user_id)
    if not user: raise HTTPException(404, "用户不存在")
    if data.fullname is not None: user.fullname = data.fullname
    if data.role is not None: user.role = data.role
    if data.is_active is not None:
        if not data.is_active and user.username == "admin":
            raise HTTPException(403, "admin 用户不可被禁用")
        user.is_active = data.is_active
    if data.password: user.hashed_password = hash_password(data.password)
    db.commit(); db.refresh(user)
    return UserOut.from_orm_obj(user)
