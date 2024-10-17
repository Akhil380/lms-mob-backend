# app/schemas/user.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    mobile: str

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    confirmPassword: str

    class Config:
        orm_mode = True

    def validate_passwords(self):
        if self.password != self.confirmPassword:
            raise ValueError("Passwords do not match")

class UserLogin(BaseModel):
    email_or_mobile: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    mobile: str
    registered_on: datetime

    class Config:
        orm_mode = True

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


class UpdatePasswordResponse(BaseModel):
    message: str