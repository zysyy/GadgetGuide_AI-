# backend/knowledge_base_processor.py
import os
import logging # <--- 1. 导入 logging 模块
from langchain_community.document_loaders import TextLoader, PyPDFLoader
# from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# 从 config.py 导入配置
from .config import UPLOAD_FOLDER, FAISS_INDEX_PATH, OLLAMA_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

# --- 2. 获取 logger 实例 ---
# 创建一个子 logger，它会自动继承在 main.py 中为 "gadgetguide_ai" 配置的 handlers 和 formatters
logger = logging.getLogger("gadgetguide_ai.knowledge_base_processor")

def create_index_from_files(file_names: list[str]):
    """
    从指定的文件列表创建或更新 FAISS 索引。
    file_names: 在 UPLOAD_FOLDER 中的文件名列表。
    """
    logger.info(f"开始从文件列表创建/更新 FAISS 索引: {file_names}") # <--- 使用 logger
    doc_paths = [os.path.join(UPLOAD_FOLDER, fn) for fn in file_names]
    all_docs = []

    for doc_path in doc_paths:
        file_name_for_log = os.path.basename(doc_path)
        if not os.path.exists(doc_path):
            logger.warning(f"文件 '{file_name_for_log}' 在路径 '{doc_path}' 未找到，已跳过。") # <---
            continue
        
        loader = None
        try:
            if doc_path.lower().endswith(".txt"):
                logger.info(f"正在加载 TXT 文件: {file_name_for_log}...") # <---
                loader = TextLoader(doc_path, encoding="utf-8")
            elif doc_path.lower().endswith(".pdf"):
                logger.info(f"正在加载 PDF 文件: {file_name_for_log}...") # <---
                loader = PyPDFLoader(doc_path)
            # elif doc_path.lower().endswith(".docx"):
            #     logger.info(f"正在加载 DOCX 文件: {file_name_for_log}...") # <---
            #     from langchain_community.document_loaders import UnstructuredWordDocumentLoader
            #     loader = UnstructuredWordDocumentLoader(doc_path)
            else:
                logger.warning(f"不支持的文件格式 '{file_name_for_log}'，已跳过。") # <---
                continue
            
            if loader:
                documents = loader.load()
                all_docs.extend(documents)
                logger.info(f"文件 '{file_name_for_log}' 加载成功，包含 {len(documents)} 个 Langchain Document 对象。") # <---

        except Exception as e:
            logger.error(f"加载文件 '{file_name_for_log}' 时出错: {e}", exc_info=True) # <--- exc_info=True 会记录堆栈跟踪
            continue
    
    if not all_docs:
        logger.warning("没有成功加载任何文档，无法创建或更新索引。") # <---
        return False

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n", "\n", "。", ". ", "！", "？", "，", "、", "；", " ", ""
        ]
    )
    
    split_docs = text_splitter.split_documents(all_docs)
    logger.info(f"所有文档内容已分割完成，共生成 {len(split_docs)} 个文本片段用于嵌入。") # <---
    # # 可选的调试打印
    # for i, doc in enumerate(split_docs[:1]): # 只看第一个块
    #     logger.debug(f"--- Chunk {i+1} (length: {len(doc.page_content)}) ---")
    #     logger.debug(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
    #     logger.debug("--------------------------------------")

    try:
        logger.info(f"正在使用 Ollama 嵌入模型: {OLLAMA_EMBEDDING_MODEL}") # <---
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        
        logger.info("正在创建/覆盖 FAISS 索引...") # <---
        vector_db = FAISS.from_documents(split_docs, embeddings)
        vector_db.save_local(FAISS_INDEX_PATH)
        logger.info(f"FAISS 索引已成功创建/覆盖，并保存到: {FAISS_INDEX_PATH}") # <---
        return True
    except Exception as e:
        logger.error(f"创建 FAISS 索引时出错: {e}", exc_info=True) # <---
        logger.error(f"请确保 Ollama 服务正在运行，并且模型 '{OLLAMA_EMBEDDING_MODEL}' 已通过 'ollama pull {OLLAMA_EMBEDDING_MODEL}' 下载。") # <---
        return False

def load_faiss_index():
    """加载本地的 FAISS 索引。"""
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
        try:
            embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
            vector_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            logger.info(f"FAISS 索引已从 {FAISS_INDEX_PATH} 加载。") # <---
            return vector_db
        except Exception as e:
            logger.error(f"加载 FAISS 索引时出错: {e}", exc_info=True) # <---
            return None
    else:
        # 索引不存在或为空是正常情况（例如首次启动），用 INFO 或 DEBUG 级别更合适
        logger.info(f"FAISS 索引目录 {FAISS_INDEX_PATH} 不存在或为空，将不会加载现有索引。") # <---
        return None