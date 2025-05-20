# backend/chat/crud.py

from sqlalchemy.orm import Session
from backend.chat import models, schemas
from backend.auth.models import User
from typing import List, Optional

# --- 创建会话 ---
def create_conversation(db: Session, user: User, title: Optional[str] = None) -> models.Conversation:
    conversation = models.Conversation(user_id=user.id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

# --- 获取用户的所有会话 ---
def get_user_conversations(db: Session, user: User) -> List[models.Conversation]:
    return db.query(models.Conversation).filter(models.Conversation.user_id == user.id).order_by(models.Conversation.created_at.desc()).all()

# --- 获取指定会话 ---
def get_conversation_by_id(db: Session, conversation_id: int, user: User) -> Optional[models.Conversation]:
    return db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user.id
    ).first()

# --- 创建消息 ---
def create_message(db: Session, conversation: models.Conversation, role: str, content: str) -> models.Message:
    message = models.Message(conversation_id=conversation.id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

# --- 获取某个会话下的所有消息 ---
def get_messages_by_conversation(db: Session, conversation: models.Conversation) -> List[models.Message]:
    return db.query(models.Message).filter(models.Message.conversation_id == conversation.id).order_by(models.Message.created_at.asc()).all()
