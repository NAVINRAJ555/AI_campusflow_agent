from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: UserRole
    department_id: Optional[int] = None

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT
    department_id: Optional[int] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    department_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
