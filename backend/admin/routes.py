# backend/admin/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.auth.models import User
from backend.chat.models import Conversation, Message

from backend.auth.routes import get_current_user
from backend.knowledge_base_processor import create_index_from_files
from backend.qa_handler import reload_vector_db
from backend.config import UPLOAD_FOLDER

from typing import List
import shutil
from pathlib import Path
import os

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# ==== 数据库会话依赖 ====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==== 管理员权限依赖 ====
def admin_required(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无管理员权限")
    return current_user

# ==== 1. 获取所有用户列表 ====
@router.get("/users", response_model=List[dict])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required)
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": u.is_admin,
            "created_at": u.created_at
        } for u in users
    ]

# ==== 2. 获取指定用户的所有会话 ====
@router.get("/users/{user_id}/conversations", response_model=List[dict])
def user_conversations(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required)
):
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at
        } for c in conversations
    ]

# ==== 3. 获取某个会话的所有消息 ====
@router.get("/conversations/{conversation_id}/messages", response_model=List[dict])
def conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required)
):
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at
        } for m in messages
    ]

# ==== 4. 管理员上传文件并更新知识库索引 ====
@router.post("/upload-documents/", summary="上传文件并更新知识库索引（仅管理员）")
async def admin_upload_documents(
    files: List[UploadFile] = File(...),
    admin: User = Depends(admin_required)
):
    if not files:
        raise HTTPException(status_code=400, detail="未选择文件")
    
    processed_files_info = []
    files_to_index = []

    for file in files:
        file_path = Path(UPLOAD_FOLDER) / file.filename
        try:
            with open(file_path, "wb+") as buffer:
                shutil.copyfileobj(file.file, buffer)
            files_to_index.append(file.filename)
            processed_files_info.append({"filename": file.filename, "status": "上传成功"})
        except Exception as e:
            processed_files_info.append({"filename": file.filename, "status": "上传失败", "error": str(e)})
        finally:
            file.file.close()
    
    if not files_to_index:
        raise HTTPException(status_code=400, detail="文件保存失败，无法建立索引。")

    # 上传后重新构建所有文件的索引（不是只针对新上传的文件，而是全部）
    all_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    if create_index_from_files(all_files):
        reload_vector_db()
        return {
            "message": f"{len(files_to_index)} 个文件已成功上传，索引已基于所有上传文件刷新。",
            "processed_files_details": processed_files_info,
            "indexed_files": all_files
        }
    else:
        raise HTTPException(status_code=500, detail="文件上传，但知识库索引构建失败，请检查后端日志。")

# ==== 5. 获取所有已上传文件列表 ====
@router.get("/uploaded-files", summary="列出所有已上传的知识库文件", response_model=List[dict])
def list_uploaded_files(admin: User = Depends(admin_required)):
    file_list = []
    for file in Path(UPLOAD_FOLDER).iterdir():
        if file.is_file():
            stat = file.stat()
            file_list.append({
                "filename": file.name,
                "size": stat.st_size,
                "modified_at": int(stat.st_mtime)
            })
    file_list.sort(key=lambda x: x["modified_at"], reverse=True)
    return file_list

# ==== 6. 删除指定文件并刷新索引 ====
@router.delete("/uploaded-files/{filename}", summary="删除已上传的知识库文件（仅管理员）")
def delete_uploaded_file(
    filename: str,
    admin: User = Depends(admin_required)
):
    file_path = Path(UPLOAD_FOLDER) / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    try:
        file_path.unlink()
        # 删除后，重新构建索引
        all_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
        if all_files:
            if not create_index_from_files(all_files):
                raise HTTPException(status_code=500, detail="文件已删除，但索引重建失败")
            reload_vector_db()
        else:
            # 若删除后文件夹已空，可以考虑清空向量库，暂不处理
            reload_vector_db()
        return {"message": f"文件 {filename} 已删除，索引已刷新。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {e}")

# ==== 7. 热词统计（返回所有消息中的高频词） ====
from collections import Counter
import jieba  # 中文分词，若只考虑英文可直接 split

@router.get("/hot-words", summary="聊天内容热词统计（高频词）", tags=["admin"])
def get_hot_words(
    top_n: int = 30,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required)
):
    # 拉取所有聊天消息
    messages = db.query(Message.content).all()
    all_text = " ".join([m[0] for m in messages if m and m[0]])
    # 分词
    words = list(jieba.cut(all_text))
    # 停用词表
    stop_words = set(["的", "了", "是", "我", "你", "吗", "和", "有", "在", "我们", "他们", "它", "这", "那", "会", "吧", "请", "能", "为", "就", "不", "也", "但", "要", "与", "对", "到", "其", "等", "与", "及", "或", "一个", "如何", "是什么", "可以", "请问"])
    # 过滤
    filtered = [w for w in words if w.strip() and w not in stop_words and len(w) > 1]
    # 高频词统计
    count = Counter(filtered)
    return [{"word": w, "count": c} for w, c in count.most_common(top_n)]
