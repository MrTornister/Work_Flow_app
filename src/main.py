from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from pathlib import Path
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, List
from functools import wraps
from enum import Enum
from sqlalchemy.orm import Session
from models.user import User, UserRole
from models import crud, schemas
from src.database import get_db
from src.auth.session import (
    SessionData, 
    flash, 
    get_flashed_messages, 
    set_session_data
)
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.auth.security import (
    SecurityConfig, 
    get_current_user, 
    SecurityUtils,
    authenticate_user
)
from src.auth.session import SessionConfig
from src.auth.logging import AuthLogger
from src.middleware import (
    security_middleware,
    rate_limit_middleware
)

# Update paths to be relative to the project root
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

app = FastAPI(title="WorkFlowSystem")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add these constants at the top of the file
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Update static files and templates setup with proper paths
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Security middleware
app.add_middleware(security_middleware)
app.add_middleware(SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session",
    max_age=int(SessionConfig.SESSION_TIMEOUT.total_seconds()),
    same_site="lax",
    https_only=True
)
app.add_middleware(rate_limit_middleware, requests_per_minute=60)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=SecurityConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=SecurityConfig.ALLOWED_HOSTS
)

# Add session middleware with timeout
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session",
    max_age=int(SessionConfig.SESSION_TIMEOUT.total_seconds()),
    same_site="lax",
    https_only=True
)

auth_logger = AuthLogger()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    
    if auth_logger.is_account_locked(form_data.username):
        flash(request, "Account temporarily locked due to multiple failed attempts", "error")
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            auth_logger.log_failed_attempt(form_data.username, client_ip)
            flash(request, "Invalid username or password", "error")
            return RedirectResponse(url="/login", status_code=303)
        
        access_token = create_access_token(data={"sub": user.username})
        session_data = SessionData(user.id, user.username, user.role)
        set_session_data(request, session_data)
        
        flash(request, "Successfully logged in", "success")
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        flash(request, "An error occurred during login", "error")
        return RedirectResponse(url="/login", status_code=303)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

def get_user(username: str, db: Session = Depends(get_db)):
    return crud.get_user_by_username(db, username)

@app.get("/users/me")
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@app.get("/profile", response_model=schemas.UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/profile/password")
async def change_password(
    password_data: schemas.PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
        
    current_user.hashed_password = User.get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

def check_role(allowed_roles: list[Role]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not permitted"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@app.post("/users/", response_model=schemas.User)
@check_role([Role.ADMIN])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
@check_role([Role.ADMIN])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
@check_role([Role.ADMIN])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
@check_role([Role.ADMIN])
async def update_user(
    user_id: int,
    user_update: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict().items():
        if field == "password":
            setattr(db_user, "hashed_password", User.get_password_hash(value))
        else:
            setattr(db_user, field, value)
            
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/password-reset-request")
async def request_password_reset(
    request_data: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, request_data.email)
    if user:
        reset_token = SecurityUtils.generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        
        # Here you would typically send an email with the reset token
        # For development, we'll just return it
        return {"message": "Reset token generated", "token": reset_token}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/password-reset")
async def reset_password(
    reset_data: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    if not SecurityUtils.validate_password_strength(reset_data.new_password):
        raise HTTPException(
            status_code=400, 
            detail="Password must be at least 8 characters and contain uppercase, lowercase, and numbers"
        )
        
    user = crud.get_user_by_reset_token(db, reset_data.token)
    if not user or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    user.hashed_password = SecurityUtils.get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password successfully reset"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

@app.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Protected endpoint requiring authentication"""
    return {"message": "This is a protected endpoint"}

@app.post("/users/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return crud.create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Additional routes can be defined here