from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers.notifications import router as notifications_router
from routers.profile_router import router as profile_router
from routers.search_router import router as search_router
from routers import (
    auth_router, subjects_router, questions_router, exams_router,
    certificates_router, announcements_router, users_router,
    feedback_router, notes_router, favorites_router,
    wrongbook_router, practice_router, video_router,
    analytics_router, abnormal_router,
    resources_router, audit_router, roles_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_defaults()
    yield


def _seed_defaults():
    from database import SessionLocal
    from models import User, Role
    from auth import hash_password

    db = SessionLocal()
    try:
        # Only seed admin user and basic roles - Chinese data comes from seed_cn.py
        if db.query(Role).count() == 0:
            db.add(Role(name="admin", description="System Admin", is_manager=True, is_system=True, sort_order=1))
            db.add(Role(name="teacher", description="Teacher/Manager", is_manager=True, is_system=True, sort_order=2))
            db.add(Role(name="student", description="Student", is_manager=False, is_system=True, sort_order=9))
            db.commit()

        if db.query(User).count() == 0:
            db.add(User(
                username="admin",
                hashed_password=hash_password("admin123"),
                fullname="System Admin",
                role="admin",
            ))
            db.commit()
    finally:
        db.close()


app = FastAPI(title="Exam System API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(subjects_router.router)
app.include_router(questions_router.router)
app.include_router(exams_router.router)
app.include_router(certificates_router.router)
app.include_router(announcements_router.router)
app.include_router(feedback_router.router)
app.include_router(notes_router.router)
app.include_router(favorites_router.router)
app.include_router(wrongbook_router.router)
app.include_router(practice_router.router)
app.include_router(video_router.router)
app.include_router(analytics_router.router)
app.include_router(abnormal_router.router)
app.include_router(resources_router.router)
app.include_router(audit_router.router)
app.include_router(roles_router.router)
app.include_router(notifications_router)
app.include_router(profile_router)
app.include_router(search_router)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [ws for ws in self.active_connections[user_id] if ws != websocket]

    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.post("/api/notify")
async def send_notification(user_id: int, message: str):
    await manager.send_to_user(user_id, {"type": "notification", "message": message})
    return {"ok": True}
