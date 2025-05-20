# backend/auth/schemas.py

from pydantic import BaseModel

# --- 用户注册与登录输入 ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# --- 用户信息输出（不包含密码） ---
class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True  # 允许 SQLAlchemy 模型转为 Pydantic 对象
