# backend/auth/auth_utils.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

logger = logging.getLogger("gadgetguide_ai")

# --- 密码加密上下文 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 加密密码 ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# --- 验证密码 ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- 创建访问 Token ---
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Issued JWT token for: {data.get('sub')}")
    return token
