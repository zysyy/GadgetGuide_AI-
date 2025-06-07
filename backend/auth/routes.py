# backend/auth/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .schemas import UserCreate, UserLogin, UserOut
from .crud import get_user_by_username, get_user_by_email, create_user, authenticate_user
from .auth_utils import create_access_token
from ..database import SessionLocal
from ..config import SECRET_KEY, ALGORITHM
import logging

logger = logging.getLogger("gadgetguide_ai")

router = APIRouter(prefix="/auth", tags=["auth"])

# --- OAuth2 bearer token ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- 获取数据库 session 的依赖 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 从 token 中获取当前用户 ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

# --- 注册接口：接收 JSON ---
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名和邮箱唯一性
    if get_user_by_username(db, user.username):
        logger.info(f"Username already exists: {user.username}")
        raise HTTPException(status_code=400, detail="Username already exists.")
    if get_user_by_email(db, user.email):
        logger.info(f"Email already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already exists.")
    new_user = create_user(db, user.username, user.email, user.password)
    logger.info(f"New user registered: {new_user.username} ({new_user.email})")
    return new_user

# --- 登录接口：接收 JSON ---
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 登录可用用户名或邮箱（任选一个字段填写）
    username_or_email = user.username if user.username else user.email
    db_user = authenticate_user(db, username_or_email, user.password)
    if not db_user:
        logger.warning(f"Login failed for: {username_or_email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    token = create_access_token({"sub": db_user.username})
    logger.info(f"User logged in: {db_user.username}")
    return {"access_token": token, "token_type": "bearer"}

# --- 获取当前用户信息 ---
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    logger.debug(f"/auth/me called by user: {current_user.username}")
    return current_user
