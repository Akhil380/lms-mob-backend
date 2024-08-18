
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud.user import get_user_by_email, create_user, get_user, get_users, get_user_by_mobile, update_user,delete_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, UserUpdate


router = APIRouter()

@router.post("/users/", response_model=UserOut)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_email = get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_mobile = get_user_by_mobile(db, mobile=user.mobile)
    if db_user_mobile:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    return create_user(db=db, user=user)

@router.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=List[UserOut])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/by-mobile/{mobile}", response_model=UserOut)
def read_user_by_mobile(mobile: str, db: Session = Depends(get_db)):
    db_user = get_user_by_mobile(db, mobile=mobile)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=UserOut)
def update_existing_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(db=db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}", response_model=UserOut)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    db_user = delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
