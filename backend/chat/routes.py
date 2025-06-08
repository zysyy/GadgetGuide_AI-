# backend/chat/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.chat import crud, schemas
from backend.auth.routes import get_current_user
from backend.auth.models import User
from backend.database import SessionLocal
from typing import List

# === 新增，导入问答核心模块（生成智能回复）===
from backend.qa_handler import get_final_answer

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# === 依赖注入：获取数据库 Session ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === 创建新会话 ===
@router.post("/conversations/", response_model=schemas.ConversationOut)
def create_conversation(
    payload: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新会话，支持自定义标题（可空）。
    """
    return crud.create_conversation(db, current_user, title=payload.title)

# === 获取当前用户的所有会话列表 ===
@router.get("/conversations/", response_model=List[schemas.ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户所有会话，按创建时间排序。
    """
    return crud.get_user_conversations(db, current_user)

# === 重命名会话 ===
@router.put("/conversations/{conversation_id}/rename")
def rename_conversation(
    conversation_id: int,
    payload: schemas.ConversationRename,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    重命名指定会话标题。
    """
    conversation = crud.get_conversation_by_id(db, conversation_id, current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    conversation.title = payload.title
    db.commit()
    db.refresh(conversation)
    return {"success": True, "new_title": conversation.title}

# === 删除会话 ===
@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除指定会话及其消息（物理删除）。
    """
    conversation = crud.get_conversation_by_id(db, conversation_id, current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    db.delete(conversation)
    db.commit()
    return {"success": True, "deleted_id": conversation_id}

# === 发送消息并让 AI 回复（多轮上下文拼接）===
@router.post("/conversations/{conversation_id}/messages/", response_model=schemas.MessageOut)
def send_message(
    conversation_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户向指定会话发送新消息，AI 自动回复，均存库。
    """
    conversation = crud.get_conversation_by_id(db, conversation_id, current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")

    # 1️⃣ 保存用户消息
    user_msg = crud.create_message(db, conversation, role=payload.role, content=payload.content)

    # 2️⃣ 获取最近 N 条上下文（拼接上下文）
    previous_msgs = crud.get_messages_by_conversation(db, conversation)
    N = 10
    previous_msgs = previous_msgs[-N:] if len(previous_msgs) > N else previous_msgs

    history_context = "\n".join([f"{m.role}: {m.content}" for m in previous_msgs])
    prompt = f"{history_context}\nuser: {payload.content}"

    # 3️⃣ 调用 AI，生成回复
    try:
        result = get_final_answer(prompt)
        ai_content = result.get("answer", "很抱歉，未能获取到明确的回答。")
    except Exception as e:
        ai_content = f"AI内部错误：{str(e)}"

    # 4️⃣ 保存 AI 消息
    crud.create_message(db, conversation, role="assistant", content=ai_content)

    return user_msg

# === 获取会话的所有消息（按时间排序）===
@router.get("/conversations/{conversation_id}/messages/", response_model=List[schemas.MessageOut])
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定会话的所有消息，按时间升序返回。
    """
    conversation = crud.get_conversation_by_id(db, conversation_id, current_user)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    return crud.get_messages_by_conversation(db, conversation)
