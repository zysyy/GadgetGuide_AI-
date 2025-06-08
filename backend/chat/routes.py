# backend/chat/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.chat import crud, schemas
from backend.auth.routes import get_current_user
from backend.auth.models import User
from backend.database import SessionLocal
from typing import List

# === 新增，导入你的问答核心 ===
from backend.qa_handler import get_final_answer

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/conversations/", response_model=schemas.ConversationOut)
def create_conversation(
    payload: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_conversation(db, current_user, title=payload.title)

@router.get("/conversations/", response_model=List[schemas.ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_user_conversations(db, current_user)

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

    # 1️⃣ 先保存用户消息
    user_msg = crud.create_message(db, conversation, role=payload.role, content=payload.content)

    # 2️⃣ 获取当前会话的历史消息，按时间顺序
    previous_msgs = crud.get_messages_by_conversation(db, conversation)

    # 3️⃣ 拼接多轮上下文（可限制最多最近N条上下文，防止上下文太长）
    N = 10
    previous_msgs = previous_msgs[-N:] if len(previous_msgs) > N else previous_msgs

    # 4️⃣ 生成上下文字符串，示例格式
    history_context = "\n".join([f"{m.role}: {m.content}" for m in previous_msgs])
    prompt = f"{history_context}\nuser: {payload.content}"

    # 5️⃣ 调用 AI，生成智能回复
    try:
        result = get_final_answer(prompt)  # 假设返回: {"answer": "..."}
        ai_content = result.get("answer", "很抱歉，未能获取到明确的回答。")
    except Exception as e:
        ai_content = f"AI内部错误：{str(e)}"

    # 6️⃣ 保存 AI 消息
    crud.create_message(db, conversation, role="assistant", content=ai_content)

    return user_msg

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
