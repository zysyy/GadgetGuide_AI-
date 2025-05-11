# backend/main.py
import logging # <--- 导入 logging 模块
import os
from pathlib import Path
from dotenv import load_dotenv

# --- 1. 配置日志 ---
# 获取根 logger
logger = logging.getLogger("gadgetguide_ai") # 给您的 logger 起个名字
logger.setLevel(logging.DEBUG) # 设置这个 logger 的最低级别，开发时可以设为 DEBUG

# 创建一个 StreamHandler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) # 控制台 Handler 也输出 DEBUG 及以上级别

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
ch.setFormatter(formatter)

# 将 Handler 添加到 logger
if not logger.hasHandlers(): # 防止重复添加 Handler (尤其在 uvicorn --reload 时)
    logger.addHandler(ch)
# --- 日志配置结束 ---


# 获取 main.py 文件所在的目录 (即 backend/ 目录)
BACKEND_DIR = Path(__file__).resolve().parent
# 构建 .env 文件的完整路径
DOTENV_PATH = BACKEND_DIR / ".env"

# 使用 logger 替代 print
logger.debug(f"Attempting to load .env from: {DOTENV_PATH}") # <--- 修改
if DOTENV_PATH.is_file(): # 检查文件是否存在
    logger.debug(f".env file found at {DOTENV_PATH}. Loading...") # <--- 修改
    load_dotenv(dotenv_path=DOTENV_PATH, verbose=True) # verbose=True 也会打印一些信息
else:
    logger.warning(f".env file NOT found at {DOTENV_PATH}. Attempting default load_dotenv().") # <--- 修改
    load_dotenv(verbose=True)

from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import shutil

# 从其他模块导入函数和变量
from .knowledge_base_processor import create_index_from_files
from .qa_handler import retrieve_context, reload_vector_db, get_final_answer
from .config import UPLOAD_FOLDER

app = FastAPI(title="GadgetGuide AI API")

# --- CORS (跨源资源共享) 配置 ---
# ... (您的 CORS 配置保持不变) ...
origins = [
    "http://localhost:8080", 
    "http://localhost:8081", 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,     
    allow_methods=["*"],        
    allow_headers=["*"],        
)

@app.on_event("startup")
async def startup_event():
    logger.info("应用程序启动，qa_handler 将尝试加载现有索引...") # <--- 修改
    pass


@app.get("/")
async def read_root():
    logger.info("Root endpoint / was called") # <--- 示例：为端点添加日志
    return {"message": "Welcome to GadgetGuide AI API!"}

@app.post("/ask", response_model=Dict[str, Any])
async def ask_question_endpoint(query: str = Form(...)):
    logger.info(f"Received query for /ask endpoint: '{query}'") # <--- 修改
    if not query.strip():
        logger.warning("Empty query received for /ask endpoint.") # <--- 修改
        raise HTTPException(status_code=400, detail="查询不能为空。")
    result = get_final_answer(query)
    if result.get("error"):
        logger.error(f"Error in /ask endpoint for query '{query}': {result.get('error')}") # <--- 修改
        raise HTTPException(status_code=500, detail=result.get("error", "处理请求时发生未知错误。"))
    logger.info(f"Successfully answered query for /ask endpoint: '{query}'") # <--- 修改
    return {"question": query, "answer": result.get("answer", "未能获取到明确的回答。")}

@app.post("/upload-documents/", response_model=Dict[str, Any])
async def upload_documents_endpoint(files: List[UploadFile] = File(...)):
    logger.info(f"Received {len(files)} file(s) for /upload-documents endpoint.") # <--- 修改
    if not files:
        logger.warning("No files received for /upload-documents endpoint.") # <--- 修改
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
            logger.info(f"文件 '{file.filename}' 已成功上传并保存到 '{file_path_on_server}'") # <--- 修改
        except Exception as e:
            logger.error(f"保存文件 '{file.filename}' 时出错: {e}") # <--- 修改
            processed_files_info.append({"filename": file.filename, "status": "上传失败", "error": str(e)})
        finally:
            file.file.close()

    if not files_to_index:
        logger.warning("所有文件都未能成功保存以进行处理。") # <--- 修改
        raise HTTPException(status_code=400, detail="所有文件都未能成功保存以进行处理。")

    logger.info(f"准备使用以下已上传的文件名处理知识库: {files_to_index}") # <--- 修改
    if create_index_from_files(files_to_index):
        if reload_vector_db():
            logger.info(f"{len(files_to_index)} 个文件已成功处理并用于更新知识库。新索引已加载。") # <--- 修改
            return {
                "message": f"{len(files_to_index)} 个文件已成功处理并用于更新知识库。新索引已加载。",
                "processed_files_details": processed_files_info,
                "indexed_files": files_to_index
            }
        else:
            logger.warning(f"{len(files_to_index)} 个文件已处理索引，但新索引加载失败。") # <--- 修改
            return {
                "message": f"{len(files_to_index)} 个文件已处理索引，但新索引加载失败。请重启应用或手动处理。",
                "processed_files_details": processed_files_info,
                "indexed_files": files_to_index,
                "warning": "Index reload failed."
            }
    else:
        logger.error(f"文件已上传，但在处理知识库和创建/更新索引时发生错误。已处理的文件: {files_to_index}") # <--- 修改
        raise HTTPException(
            status_code=500,
            detail=f"文件已上传，但在处理知识库和创建/更新索引时发生错误。请检查服务器日志。",
            headers={"X-Processed-Files-Details": str(processed_files_info)}
        )

# ... (您的 /retrieve_context 和 /build_index_from_sample 端点也可以用类似方式添加日志) ...
# 例如 /build_index_from_sample:
@app.post("/build_index_from_sample")
async def build_index_from_sample_endpoint():
    sample_files = [
        "iPhone 15 Pro - 技术规格 - 官方 Apple 支持 (中国).pdf",
        "iPhone 16 Pro - Tech Specs - Apple Support.pdf", 
        "sample_apple_info.txt" 
    ]
    logger.info(f"准备使用以下文件列表构建/更新索引: {sample_files}") # <--- 修改
    if create_index_from_files(sample_files):
        if reload_vector_db():
            logger.info(f"索引已成功基于 {len(sample_files)} 个文件创建/更新，并已重新加载。") # <--- 修改
            return {"message": f"索引已成功基于 {len(sample_files)} 个文件创建/更新，并已重新加载。文件列表: {sample_files}"}
        else:
            logger.warning(f"索引已成功基于 {len(sample_files)} 个文件创建/更新，但重新加载到服务时可能存在问题或索引仍为空。") # <--- 修改
            return {"message": f"索引已成功基于 {len(sample_files)} 个文件创建/更新，但重新加载到服务时可能存在问题或索引仍为空。文件列表: {sample_files}，请检查日志。"}
    else:
        logger.error(f"基于指定文件列表创建/更新索引失败。") # <--- 修改
        raise HTTPException(status_code=500, detail=f"基于指定文件列表创建/更新索引失败。请检查服务器日志获取详细信息。")