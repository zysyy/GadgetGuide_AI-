# backend/main.py (文件顶部)
from dotenv import load_dotenv
load_dotenv() # 加载 .env 文件

from fastapi import FastAPI, HTTPException, Form
from typing import List, Dict, Any # 引入类型提示
# 从其他模块导入函数和变量
# 确保这些 .py 文件和其中的函数都已按照之前的建议创建好
from .knowledge_base_processor import create_index_from_files 
from .qa_handler import retrieve_context, reload_vector_db # 确保 reload_vector_db 也被导入
# from .config import UPLOAD_FOLDER # UPLOAD_FOLDER 在 knowledge_base_processor 中使用，这里可能不需要直接导入

app = FastAPI(title="GadgetGuide AI API")

@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的事件。
    qa_handler 模块在被导入时会尝试加载 FAISS 索引。
    如果需要，可以在这里添加其他启动逻辑。
    """
    print("应用程序启动，qa_handler 将尝试加载现有索引...")
    # qa_handler.vector_db 应该在 qa_handler.py 模块加载时被初始化
    # 如果你想在这里显式触发一次加载（或者如果 qa_handler 中的加载逻辑需要被调用）
    # if not qa_handler.vector_db:
    #     qa_handler.reload_vector_db()
    pass


@app.get("/")
async def read_root():
    return {"message": "Welcome to GadgetGuide AI API!"}

@app.post("/retrieve_context", response_model=Dict[str, Any]) # 使用类型提示定义响应模型
async def retrieve_context_endpoint(query: str = Form(...)):
    """
    接收用户查询，返回从知识库中检索到的相关文本片段。
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空。")
    
    result = retrieve_context(query) # retrieve_context 来自 qa_handler.py
    if result.get("error"): # 检查是否有错误键
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/build_index_from_sample") 
async def build_index_from_sample_endpoint():
    """
    (临时端点) 使用 uploads/sample_apple_info.txt 创建或更新索引。
    """
    sample_files = ["sample_apple_info.txt"] # 确保这个文件在 uploads 文件夹中
    # create_index_from_files 来自 knowledge_base_processor.py
    if create_index_from_files(sample_files):
        # reload_vector_db 来自 qa_handler.py
        if reload_vector_db(): 
             return {"message": f"索引已成功基于 {sample_files} 创建/更新，并已重新加载。"}
        else:
            # 即使索引创建成功，如果 qa_handler 中的 vector_db 实例没有正确更新，查询也可能使用旧的或空的索引
            return {"message": f"索引已成功基于 {sample_files} 创建/更新，但重新加载到服务时可能存在问题或索引仍为空。请检查日志。"}
    else:
        raise HTTPException(status_code=500, detail=f"基于 {sample_files} 创建/更新索引失败。请检查服务器日志获取详细信息。")

# TODO: 稍后实现 /ask 端点，它会调用 retrieve_context 并将结果传给 LLM
# TODO: 稍后实现 /upload-documents 端点，用于上传新文档并触发索引更新