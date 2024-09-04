from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.crud.user import (
    get_user_by_email, create_user, get_user, get_users,
    get_user_by_mobile, delete_user,
    authenticate_user
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.security import create_access_token, TokenData, get_current_user

router = APIRouter()


def serialize_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "mobile": user.mobile,
        "registered_on": user.registered_on
    }

@router.post("/signin", response_model=dict)
def signin(user_login: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user_login.email_or_mobile, user_login.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": db_user.email})
    user_data = serialize_user(db_user)
    user_out = UserOut(**user_data)
    return {
        "user": user_out,
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.post("/signup/", response_model=UserOut)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if get_user_by_mobile(db, mobile=user.mobile):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number already registered")
    db_user = create_user(db=db, user=user)
    return db_user

@router.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.get("/users/", response_model=List[UserOut])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/by-mobile/{mobile}", response_model=UserOut)
def read_user_by_mobile(mobile: str, db: Session = Depends(get_db)):
    db_user = get_user_by_mobile(db, mobile=mobile)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

# @router.put("/users/{user_id}", response_model=UserOut)
# def update_existing_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
#     db_user = update_user(db=db, user_id=user_id, user_update=user_update)
#     if db_user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return db_user

@router.delete("/users/{user_id}", response_model=UserOut)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    db_user = delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.post("/refresh-token")
def refresh_token(current_user: TokenData = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}