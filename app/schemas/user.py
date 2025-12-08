from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    store_id: int | None
    is_admin: bool
    is_approved: bool
    is_active: bool   
    created_at: datetime

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
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_admin: bool
    is_approved: bool
    store_id: Optional[int] = None  