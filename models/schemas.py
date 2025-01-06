from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    last_login: Optional[datetime]
    
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class Token(BaseModel):
    access_token: str
    token_type: str