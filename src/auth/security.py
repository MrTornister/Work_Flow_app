from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from typing import Optional, Dict
import hashlib
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from functools import wraps
from models.user import UserPermission, User, UserRole, ROLE_PERMISSIONS
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from models import crud
from src.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(username: str, db: Session = Depends(get_db)) -> Optional[User]:
    return crud.get_user_by_username(db, username)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username, db)
    if user is None:
        raise credentials_exception
    return user

async def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = crud.get_user_by_username(db, username)
    if not user:
        return None
    if not SecurityUtils.verify_password(password, user.hashed_password):
        return None
    return user

class CSRFTokenGenerator:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, request: Request) -> str:
        token = secrets.token_urlsafe(32)
        request.session['csrf_token'] = token
        return token
        
    def validate_token(self, request: Request, token: str) -> bool:
        stored_token = request.session.get('csrf_token')
        if not stored_token or not token:
            return False
        return secrets.compare_digest(stored_token, token)

class SecurityHeaders:
    @staticmethod
    def get_security_headers():
        return {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'"
        }

class SecurityConfig:
    SECRET_KEY = secrets.token_urlsafe(32)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    CORS_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

    SECURITY_HEADERS = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    @staticmethod
    def get_security_headers():
        return SecurityConfig.SECURITY_HEADERS

class SecurityUtils:
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        if not salt:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return hashlib.hexdigest(hash_obj), salt

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
        
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
        
    @staticmethod
    def generate_reset_token() -> str:
        return secrets.token_urlsafe(32)
        
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True

def require_permission(permission: UserPermission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
            if permission.value not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def create_test_token(role: UserRole) -> str:
    """Creates a JWT token for testing purposes"""
    token_data = {
        "sub": "testuser",
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(token_data, SecurityConfig.SECRET_KEY, algorithm="HS256")