# backend/chat/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.chat import crud, schemas
from backend.auth.routes import get_current_user
from backend.auth.models import User
from backend.database import SessionLocal
from typing import List

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# --- 获取数据库 Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 创建新会话 ---
@router.post("/conversations/", response_model=schemas.ConversationOut)
def create_conversation(
    payload: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_conversation(db, current_user, title=payload.title)

# --- 获取当前用户的所有会话 ---
@router.get("/conversations/", response_model=List[schemas.ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_user_conversations(db, current_user)

# --- 向会话发送消息（用户或助手）---
@router.post("/conversations/{conversation_id}/messages/", response_model=schemas.MessageOut)
def send_message(
    conversation_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = crud.get_conversation_by_id(db, conversation_id, current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    return crud.create_message(db, conversation, role=payload.role, content=payload.content)

# --- 获取某会话的所有消息 ---
@router.get("/conversations/{conversation_id}/messages/", response_model=List[schemas.MessageOut])
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = crud.get_conversation_by_id(db, conversation_id, current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    return crud.get_messages_by_conversation(db, conversation)
