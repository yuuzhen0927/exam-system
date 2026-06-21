import re
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import User
from auth import hash_password, verify_password, create_access_token, get_current_user
from routers.audit_router import log_operation

router = APIRouter(prefix="/api/auth", tags=["认证"])
def _validate_password(password: str):
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")
    if not re.search(r'[A-Za-z]', password):
        raise HTTPException(status_code=400, detail="密码必须包含字母")
    if not re.search(r'[0-9]', password):
        raise HTTPException(status_code=400, detail="密码必须包含数字")
    if re.search(r'^(.)\1+$', password):
        raise HTTPException(status_code=400, detail="密码不能全是相同字符")
    if password.lower() in ('123456', 'password', 'qwerty', 'abc123', '111111', 'aaaaaa'):
        raise HTTPException(status_code=400, detail="密码过于简单，请换一个")


class RegisterRequest(BaseModel):
    username: str
    password: str
    fullname: str = ""


class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.username or len(req.username) < 2:
        raise HTTPException(status_code=400, detail="用户名至少2个字符")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    _validate_password(req.password)
    user = User(
        username=req.username,
        hashed_password=hash_password(req.password),
        fullname=req.fullname,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        if user:
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            db.commit()
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.locked_until and user.locked_until.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        remaining = int((user.locked_until.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds() / 60)
        raise HTTPException(status_code=403, detail=f"账号已锁定，请{remaining}分钟后重试")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    user.login_attempts = 0
    user.locked_until = None
    db.commit()
    token = create_access_token({"sub": user.username})
    log_operation(db, user.id, user.username, "login", "user", user.id, detail="用户登录")
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
