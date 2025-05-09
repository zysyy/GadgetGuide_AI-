# backend/main.py (文件顶部)
import os
from pathlib import Path
from dotenv import load_dotenv

# 获取 main.py 文件所在的目录 (即 backend/ 目录)
BACKEND_DIR = Path(__file__).resolve().parent
# 构建 .env 文件的完整路径
DOTENV_PATH = BACKEND_DIR / ".env"

print(f"--- DEBUG [main.py]: Attempting to load .env from: {DOTENV_PATH} ---")
if DOTENV_PATH.is_file(): # 检查文件是否存在
    print(f"--- DEBUG [main.py]: .env file found at {DOTENV_PATH}. Loading... ---")
    load_dotenv(dotenv_path=DOTENV_PATH, verbose=True)
else:
    print(f"--- DEBUG [main.py]: .env file NOT found at {DOTENV_PATH}. Attempting default load_dotenv(). ---")
    load_dotenv(verbose=True)

from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from typing import List, Dict, Any
import shutil

# 从其他模块导入函数和变量
from .knowledge_base_processor import create_index_from_files
from .qa_handler import retrieve_context, reload_vector_db, get_final_answer
from .config import UPLOAD_FOLDER

app = FastAPI(title="GadgetGuide AI API")

@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的事件。
    qa_handler 模块在被导入时会尝试加载 FAISS 索引。
    """
    print("应用程序启动，qa_handler 将尝试加载现有索引...")
    pass


@app.get("/")
async def read_root():
    return {"message": "Welcome to GadgetGuide AI API!"}

@app.post("/ask", response_model=Dict[str, Any])
async def ask_question_endpoint(query: str = Form(...)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空。")
    result = get_final_answer(query)
    if result.get("error"):
        print(f"Error in /ask endpoint: {result.get('error')}")
        raise HTTPException(status_code=500, detail=result.get("error", "处理请求时发生未知错误。"))
    return {"question": query, "answer": result.get("answer", "未能获取到明确的回答。")}

@app.post("/upload-documents/", response_model=Dict[str, Any])
async def upload_documents_endpoint(files: List[UploadFile] = File(...)):
    """
    接收上传的一个或多个文档，保存它们，然后处理并更新知识库索引。
    """
    if not files:
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
            print(f"文件 '{file.filename}' 已成功上传并保存到 '{file_path_on_server}'")
        except Exception as e:
            print(f"保存文件 '{file.filename}' 时出错: {e}")
            processed_files_info.append({"filename": file.filename, "status": "上传失败", "error": str(e)})
        finally:
            file.file.close()

    if not files_to_index:
        raise HTTPException(status_code=400, detail="所有文件都未能成功保存以进行处理。")

    print(f"准备使用以下已上传的文件名处理知识库: {files_to_index}")
    if create_index_from_files(files_to_index):
        if reload_vector_db():
            return {
                "message": f"{len(files_to_index)} 个文件已成功处理并用于更新知识库。新索引已加载。",
                "processed_files_details": processed_files_info,
                "indexed_files": files_to_index
            }
        else:
            return {
                "message": f"{len(files_to_index)} 个文件已处理索引，但新索引加载失败。请重启应用或手动处理。",
                "processed_files_details": processed_files_info,
                "indexed_files": files_to_index,
                "warning": "Index reload failed."
            }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"文件已上传，但在处理知识库和创建/更新索引时发生错误。请检查服务器日志。",
            headers={"X-Processed-Files-Details": str(processed_files_info)}
        )


@app.post("/retrieve_context", response_model=Dict[str, Any])
async def retrieve_context_endpoint(query: str = Form(...)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空。")
    result = retrieve_context(query)
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/build_index_from_sample")
async def build_index_from_sample_endpoint():
    """
    (临时端点) 使用 uploads/ 目录中指定的文件列表创建或更新索引。
    """
    # !!! 请确保以下文件名与您 backend/uploads/ 文件夹中的实际文件名完全一致 !!!
    sample_files = [
        "iPhone 15 Pro - 技术规格 - 官方 Apple 支持 (中国).pdf",
        "iPhone 16 Pro - Tech Specs - Apple Support.pdf", # <--- 请替换为您的iPhone 16 Pro PDF的准确文件名
        "sample_apple_info.txt"  # <--- 请替换为您示例TXT文件的准确文件名 (如果名称不同)
    ]
    print(f"准备使用以下文件列表构建/更新索引: {sample_files}")
    if create_index_from_files(sample_files):
        if reload_vector_db():
             return {"message": f"索引已成功基于 {len(sample_files)} 个文件创建/更新，并已重新加载。文件列表: {sample_files}"}
        else:
            return {"message": f"索引已成功基于 {len(sample_files)} 个文件创建/更新，但重新加载到服务时可能存在问题或索引仍为空。文件列表: {sample_files}，请检查日志。"}
    else:
        raise HTTPException(status_code=500, detail=f"基于指定文件列表创建/更新索引失败。请检查服务器日志获取详细信息。")