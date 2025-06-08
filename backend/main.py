import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# --- 日志配置 ---
logger = logging.getLogger("gadgetguide_ai")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
ch.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(ch)

# --- .env 加载 ---
BACKEND_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BACKEND_DIR / ".env"
logger.debug(f"Attempting to load .env from: {DOTENV_PATH}")
if DOTENV_PATH.is_file():
    logger.debug(f".env file found at {DOTENV_PATH}. Loading...")
    load_dotenv(dotenv_path=DOTENV_PATH, verbose=True)
else:
    logger.warning(f".env file NOT found at {DOTENV_PATH}. Attempting default load_dotenv().")
    load_dotenv(verbose=True)

from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import shutil

# --- 模块导入 ---
from backend.knowledge_base_processor import create_index_from_files
from backend.qa_handler import retrieve_context, reload_vector_db, get_final_answer
from backend.config import UPLOAD_FOLDER
from backend.auth.routes import router as auth_router
from backend.chat.routes import router as chat_router
from backend.admin.routes import router as admin_router        # <--- 新增
from backend.auth import models
from backend.chat import models as chat_models
from backend.database import Base, engine

# --- 创建 FastAPI 实例 ---
app = FastAPI(title="GadgetGuide AI API")

# --- 创建所有数据表（用户表、会话表、消息表等） ---
Base.metadata.create_all(bind=engine)

# --- CORS 配置 ---
origins = [
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 路由挂载 ---
logger.debug("Mounting /auth, /chat and /admin routes...")
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(admin_router)     # <--- 新增
logger.info("Routes mounted successfully.")

@app.on_event("startup")
async def startup_event():
    logger.info("应用程序启动，qa_handler 将尝试加载现有索引...")

@app.get("/")
async def read_root():
    logger.info("Root endpoint / was called")
    return {"message": "Welcome to GadgetGuide AI API!"}

@app.post("/ask", response_model=Dict[str, Any])
async def ask_question_endpoint(query: str = Form(...)):
    logger.info(f"Received query for /ask endpoint: '{query}'")
    if not query.strip():
        logger.warning("Empty query received for /ask endpoint.")
        raise HTTPException(status_code=400, detail="查询不能为空。")
    result = get_final_answer(query)
    if result.get("error"):
        logger.error(f"Error in /ask endpoint for query '{query}': {result.get('error')}")
        raise HTTPException(status_code=500, detail=result.get("error", "处理请求时发生未知错误。"))
    logger.info(f"Successfully answered query for /ask endpoint: '{query}'")
    return {"question": query, "answer": result.get("answer", "未能获取到明确的回答。")}

@app.post("/upload-documents/", response_model=Dict[str, Any])
async def upload_documents_endpoint(files: List[UploadFile] = File(...)):
    logger.info(f"Received {len(files)} file(s) for /upload-documents endpoint.")
    if not files:
        logger.warning("No files received for /upload-documents endpoint.")
        raise HTTPException(status_code=400, detail="没有选择任何文件进行上传。")

    processed_files_info = []
    files_to_index = []

    for file in files:
        file_path_on_server = Path(UPLOAD_FOLDER) / file.filename
        try:
            with open(file_path_on_server, "wb+") as buffer:
                shutil.copyfileobj(file.file, buffer)
            files_to_index.append(file.filename)
            processed_files_info.append({"filename": file.filename, "status": "上传成功"})
            logger.info(f"文件 '{file.filename}' 已成功上传并保存到 '{file_path_on_server}'")
        except Exception as e:
            logger.error(f"保存文件 '{file.filename}' 时出错: {e}")
            processed_files_info.append({"filename": file.filename, "status": "上传失败", "error": str(e)})
        finally:
            file.file.close()

    if not files_to_index:
        logger.warning("所有文件都未能成功保存以进行处理。")
        raise HTTPException(status_code=400, detail="所有文件都未能成功保存以进行处理。")

    logger.info(f"准备使用以下已上传的文件名处理知识库: {files_to_index}")
    if create_index_from_files(files_to_index):
        if reload_vector_db():
            logger.info(f"{len(files_to_index)} 个文件已成功处理并用于更新知识库。新索引已加载。")
            return {
                "message": f"{len(files_to_index)} 个文件已成功处理并用于更新知识库。新索引已加载。",
                "processed_files_details": processed_files_info,
                "indexed_files": files_to_index
            }
        else:
            logger.warning(f"{len(files_to_index)} 个文件已处理索引，但新索引加载失败。")
            return {
                "message": f"{len(files_to_index)} 个文件已处理索引，但新索引加载失败。请重启应用或手动处理。",
                "processed_files_details": processed_files_info,
                "indexed_files": files_to_index,
                "warning": "Index reload failed."
            }
    else:
        logger.error(f"文件已上传，但在处理知识库和创建/更新索引时发生错误。已处理的文件: {files_to_index}")
        raise HTTPException(
            status_code=500,
            detail=f"文件已上传，但在处理知识库和创建/更新索引时发生错误。请检查服务器日志。",
            headers={"X-Processed-Files-Details": str(processed_files_info)}
        )

@app.post("/build_index_from_sample")
async def build_index_from_sample_endpoint():
    sample_files = [
        "iPhone 15 Pro - 技术规格 - 官方 Apple 支持 (中国).pdf",
        "iPhone 16 Pro - Tech Specs - Apple Support.pdf",
        "sample_apple_info.txt"
    ]
    logger.info(f"准备使用以下文件列表构建/更新索引: {sample_files}")
    if create_index_from_files(sample_files):
        if reload_vector_db():
            logger.info(f"索引已成功基于 {len(sample_files)} 个文件创建/更新，并已重新加载。")
            return {"message": f"索引已成功基于 {len(sample_files)} 个文件创建/更新，并已重新加载。文件列表: {sample_files}"}
        else:
            logger.warning(f"索引已成功基于 {len(sample_files)} 个文件创建/更新，但重新加载到服务时可能存在问题或索引仍为空。")
            return {"message": f"索引已成功基于 {len(sample_files)} 个文件创建/更新，但重新加载到服务时可能存在问题或索引仍为空。文件列表: {sample_files}，请检查日志。"}
    else:
        logger.error(f"基于指定文件列表创建/更新索引失败。")
        raise HTTPException(status_code=500, detail="基于指定文件列表创建/更新索引失败。请检查服务器日志获取详细信息。")
