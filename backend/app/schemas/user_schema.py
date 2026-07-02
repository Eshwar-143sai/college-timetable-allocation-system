from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "faculty"
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v2 from_attributes replaces orm_mode = True
