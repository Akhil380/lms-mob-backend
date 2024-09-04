from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_mobile(db: Session, mobile: str) -> Optional[User]:
    return db.query(User).filter(User.mobile == mobile).first()

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    if get_user_by_email(db, email=user.email) or get_user_by_mobile(db, mobile=user.mobile):
        raise ValueError("User with this email or mobile already exists")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        mobile=user.mobile,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
#     db_user = get_user(db, user_id=user_id)
#     if db_user:
#         if user_update.name:
#             db_user.name = user_update.name
#         if user_update.email:
#             if get_user_by_email(db, email=user_update.email) and user_update.email != db_user.email:
#                 raise ValueError("Email already in use")
#             db_user.email = user_update.email
#         if user_update.mobile:
#             if get_user_by_mobile(db, mobile=user_update.mobile) and user_update.mobile != db_user.mobile:
#                 raise ValueError("Mobile number already in use")
#             db_user.mobile = user_update.mobile
#         if user_update.password:
#             db_user.hashed_password = pwd_context.hash(user_update.password)
#         db.commit()
#         db.refresh(db_user)
#         return db_user
#     return None

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email_or_mobile: str, password: str) -> Optional[User]:
    db_user = get_user_by_email(db, email=email_or_mobile) or get_user_by_mobile(db, mobile=email_or_mobile)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return None
    return db_user
