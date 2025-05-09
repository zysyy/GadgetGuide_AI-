# backend/qa_handler.py
from langchain_ollama import OllamaEmbeddings
from .knowledge_base_processor import load_faiss_index
from .config import OLLAMA_EMBEDDING_MODEL

# 在模块加载时尝试加载 FAISS 索引
# 注意：这使得 vector_db 成为模块级变量。在 FastAPI 中，更好的做法可能是
# 通过依赖注入或在应用启动时加载并传递给需要它的函数/类。
# 但为了简单起见，我们先用模块级变量。
vector_db = load_faiss_index()

def reload_vector_db():
    """重新加载 FAISS 索引，用于索引更新后。"""
    global vector_db
    vector_db = load_faiss_index()
    return vector_db

def retrieve_context(query: str):
    """
    根据用户查询从 FAISS 索引中检索相关上下文。
    """
    if vector_db is None:
        return {"error": "知识库索引未加载，请先处理知识库文档。"}

    try:
        # embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL) # 如果 vector_db 加载时未指定 embedding，则需要
        # results = vector_db.similarity_search_by_vector(embeddings.embed_query(query), k=3)
        results = vector_db.similarity_search(query, k=3) # k=3 表示返回3个最相关的片段
        
        if not results:
            return {"message": "未能从知识库中找到相关信息。", "retrieved_chunks": []}

        retrieved_chunks = [doc.page_content for doc in results]
        return {"retrieved_chunks": retrieved_chunks}
    except Exception as e:
        print(f"检索上下文时出错: {e}")
        return {"error": f"检索上下文时出错: {e}"}

# 稍后我们会在这里添加调用 DeepSeek API 的逻辑
# def get_answer_from_llm(query: str, context_chunks: list[str]):
#     pass