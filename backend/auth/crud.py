# backend/auth/crud.py

from sqlalchemy.orm import Session
from .models import User
from .auth_utils import hash_password, verify_password

# --- 通过用户名查找用户 ---
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# --- 通过邮箱查找用户 ---
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# --- 创建新用户 ---
def create_user(db: Session, username: str, email: str, password: str):
    hashed_pw = hash_password(password)
    user = User(username=username, email=email, password_hash=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- 验证用户身份（支持用户名或邮箱登录） ---
def authenticate_user(db: Session, username_or_email: str, password: str):
    user = (
        db.query(User)
        .filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        )
        .first()
    )
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
