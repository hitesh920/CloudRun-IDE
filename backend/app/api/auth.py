"""
CloudRun IDE - Auth Routes
User registration, login, and profile endpoints.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
import hashlib
import hmac
import json
import base64
import re
import os

from app.core.database import get_db, User
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ─── Request/Response models ─────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = ""

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 30:
            raise ValueError('Username must be 3-30 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username: letters, numbers, underscores only')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email')
        return v.lower()


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    created_at: str


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


# ─── Password hashing ───────────────────────────────────

def _hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return f"{salt}${key}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, key = stored_hash.split('$')
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


# ─── JWT ─────────────────────────────────────────────────

def _create_token(user_id: int, username: str) -> str:
    secret = settings.JWT_SECRET
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def _verify_token(token: str) -> Optional[dict]:
    try:
        secret = settings.JWT_SECRET
        payload_b64, sig = token.rsplit('.', 1)
        expected_sig = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        exp = datetime.fromisoformat(payload["exp"])
        if datetime.now(timezone.utc) > exp:
            return None
        return payload
    except Exception:
        return None


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name or user.username,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


# ─── Auth dependency ─────────────────────────────────────

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = _verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ─── Routes ──────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        username=req.username,
        email=req.email,
        password_hash=_hash_password(req.password),
        display_name=req.display_name or req.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ New user registered: {user.username}")
    token = _create_token(user.id, user.username)
    return TokenResponse(token=token, user=_user_to_response(user))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == req.username.lower()) | (User.email == req.username.lower())
    ).first()
    if not user or not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    print(f"✅ User logged in: {user.username}")
    token = _create_token(user.id, user.username)
    return TokenResponse(token=token, user=_user_to_response(user))


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return _user_to_response(user)


@router.post("/verify")
async def verify_token(user: User = Depends(get_current_user)):
    return {"valid": True, "user": _user_to_response(user)}
