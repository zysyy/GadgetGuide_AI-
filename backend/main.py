# backend/main.py (文件顶部)
import os # 需要 os 来构建路径或检查文件，或者用 pathlib
from pathlib import Path # 推荐使用 pathlib 处理路径
from dotenv import load_dotenv

# 获取 main.py 文件所在的目录 (即 backend/ 目录)
BACKEND_DIR = Path(__file__).resolve().parent
# 构建 .env 文件的完整路径
DOTENV_PATH = BACKEND_DIR / ".env"

print(f"--- DEBUG [main.py]: Attempting to load .env from: {DOTENV_PATH} ---")
if DOTENV_PATH.is_file(): # 检查文件是否存在
    print(f"--- DEBUG [main.py]: .env file found at {DOTENV_PATH}. Loading... ---")
    load_dotenv(dotenv_path=DOTENV_PATH, verbose=True) # verbose=True 会打印加载过程信息
else:
    print(f"--- DEBUG [main.py]: .env file NOT found at {DOTENV_PATH}. Attempting default load_dotenv(). ---")
    load_dotenv(verbose=True) # 尝试默认加载（会搜索当前工作目录和父目录）

from fastapi import FastAPI, HTTPException, Form
from typing import List, Dict, Any # 引入类型提示

# 从其他模块导入函数和变量
# 确保这些 .py 文件和其中的函数都已按照之前的建议创建好
from .knowledge_base_processor import create_index_from_files
# 现在我们主要使用 get_final_answer，它内部会调用 retrieve_context
# retrieve_context 仍然可以保留，如果想单独测试检索步骤
from .qa_handler import retrieve_context, reload_vector_db, get_final_answer 
# from .config import UPLOAD_FOLDER # UPLOAD_FOLDER 在 knowledge_base_processor 中使用

app = FastAPI(title="GadgetGuide AI API")

@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的事件。
    qa_handler 模块在被导入时会尝试加载 FAISS 索引。
    """
    print("应用程序启动，qa_handler 将尝试加载现有索引...")
    # qa_handler.vector_db 应该在 qa_handler.py 模块加载时被初始化
    # 如果 qa_handler.py 中的 vector_db 初始加载失败（例如索引第一次不存在），
    # 那么在调用 /build_index_from_sample 成功后，reload_vector_db() 会更新它。
    pass


@app.get("/")
async def read_root():
    return {"message": "Welcome to GadgetGuide AI API!"}

@app.post("/ask", response_model=Dict[str, Any])
async def ask_question_endpoint(query: str = Form(...)):
    """
    接收用户查询，进行 RAG 处理 (检索 + LLM 生成)，并返回最终答案。
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空。")
    
    # 调用 qa_handler 中的核心 RAG 问答函数
    result = get_final_answer(query) 
    
    if result.get("error"): # 检查是否有错误键
        # 根据错误类型可以返回不同的状态码，这里简化处理
        # 例如，如果是 API Key 问题，可能是 503 Service Unavailable
        # 如果是找不到上下文，可能不是 500，而是由 get_final_answer 直接返回提示信息
        # 这里我们假设 get_final_answer 中标记为 "error" 的都是需要 HTTP 错误响应的
        print(f"Error in /ask endpoint: {result.get('error')}") # 打印错误到服务器日志
        raise HTTPException(status_code=500, detail=result.get("error", "处理请求时发生未知错误。"))
    
    # 如果没有错误，返回包含问题和答案的字典
    # get_final_answer 应该总是返回一个包含 "answer" 键的字典（如果成功）
    # 或者一个包含 "error" 键的字典（如果失败）
    return {"question": query, "answer": result.get("answer", "未能获取到明确的回答。")}


@app.post("/retrieve_context", response_model=Dict[str, Any]) 
async def retrieve_context_endpoint(query: str = Form(...)):
    """
    (调试用) 接收用户查询，仅返回从知识库中检索到的相关文本片段。
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空。")
    
    result = retrieve_context(query) 
    if result.get("error"): 
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/build_index_from_sample") 
async def build_index_from_sample_endpoint():
    """
    (临时端点) 使用 uploads/sample_apple_info.txt 创建或更新索引。
    """
    sample_files = ["sample_apple_info.txt"] 
    if create_index_from_files(sample_files):
        if reload_vector_db(): 
             return {"message": f"索引已成功基于 {sample_files} 创建/更新，并已重新加载。"}
        else:
            return {"message": f"索引已成功基于 {sample_files} 创建/更新，但重新加载到服务时可能存在问题或索引仍为空。请检查日志。"}
    else:
        raise HTTPException(status_code=500, detail=f"基于 {sample_files} 创建/更新索引失败。请检查服务器日志获取详细信息。")

# TODO: 稍后实现 /upload-documents 端点，用于上传新文档并触发索引更新
# 这个端点会更复杂，需要处理文件保存和调用 create_index_from_files 及 reload_vector_db

# 如果您想在直接运行 python main.py 时启动 uvicorn (主要用于开发，但不推荐用于多文件项目中的相对导入)
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)