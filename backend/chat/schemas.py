# backend/chat/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2: 替代 orm_mode

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationRename(BaseModel):
    """
    新增：用于重命名会话的请求体模型
    """
    title: str

    class Config:
        from_attributes = True

class ConversationOut(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True
