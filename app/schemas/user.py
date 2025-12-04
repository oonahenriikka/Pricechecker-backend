from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserAdminResponse(BaseModel):
    id: int
    email: str
    store_id: int | None
    is_admin: bool
    is_approved: bool
    is_active: bool   
    created_at: datetime

    class Config:
        from_attributes = True

class UserToggleActive(BaseModel):
    is_active: bool

class UserMakeAdmin(BaseModel):
    make_admin: bool

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    store_name: str  


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(UserBase):
    id: int
    is_admin: bool
    is_approved: bool
    store_id: Optional[int] = None  

    class Config:
        from_attributes = True  