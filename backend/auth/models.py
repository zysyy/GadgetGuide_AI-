# backend/auth/models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)      # 唯一且非空
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)                     # 新增: 管理员标志
    created_at = Column(DateTime, default=datetime.utcnow)
    # conversations 不在类体内直接定义，见下

# 延迟注册 conversations 关系，避免循环依赖
try:
    from backend.chat.models import Conversation
    User.conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
except ImportError:
    # 允许迁移或特殊环境下跳过
    pass
