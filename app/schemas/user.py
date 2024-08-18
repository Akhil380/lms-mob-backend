from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    mobile: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    mobile: str
    joined_at: datetime

    class Config:
        from_attributes = True
