from fastapi import Request
from typing import Optional
from datetime import datetime, timedelta
import json

class SessionConfig:
    SESSION_TIMEOUT = timedelta(minutes=30)
    REFRESH_TIMEOUT = timedelta(minutes=15)

class SessionData:
    def __init__(self, user_id: int, username: str, role: str):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        session = cls(
            user_id=data["user_id"],
            username=data["username"],
            role=data["role"]
        )
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_activity = datetime.fromisoformat(data["last_activity"])
        return session

def get_session_data(request: Request) -> Optional[SessionData]:
    if "session" not in request.session:
        return None
    return SessionData.from_dict(request.session["session"])

def set_session_data(request: Request, session_data: SessionData):
    request.session["session"] = session_data.to_dict()

def clear_session(request: Request):
    request.session.clear()

class FlashMessage:
    def __init__(self, text: str, category: str = "info"):
        self.text = text
        self.category = category

def flash(request: Request, message: str, category: str = "info"):
    if "flash_messages" not in request.session:
        request.session["flash_messages"] = []
    request.session["flash_messages"].append(
        {"text": message, "category": category}
    )

def get_flashed_messages(request: Request):
    messages = request.session.pop("flash_messages", [])
    return messages