# backend/knowledge_base_processor.py
import os
import json
import logging
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from .config import UPLOAD_FOLDER, FAISS_INDEX_PATH, OLLAMA_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

# --- 获取 logger 实例 ---
logger = logging.getLogger("gadgetguide_ai.knowledge_base_processor")

# 定义已处理文件记录路径
PROCESSED_FILES_PATH = os.path.join(FAISS_INDEX_PATH, "processed_files.json")

def load_processed_files():
    """加载已处理文件的记录"""
    if os.path.exists(PROCESSED_FILES_PATH):
        try:
            with open(PROCESSED_FILES_PATH, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"读取已处理文件记录失败: {e}")
    return set()

def save_processed_files(files: set):
    """保存已处理文件记录"""
    try:
        with open(PROCESSED_FILES_PATH, 'w', encoding='utf-8') as f:
            json.dump(list(files), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"保存已处理文件记录失败: {e}")

def inject_filename_to_documents(documents, source_path: str):
    """在每个文档前注入来源文件信息"""
    filename = Path(source_path).name
    for doc in documents:
        page = doc.metadata.get("page", None)
        if page is not None:
            doc.page_content = f"[{filename} - 第{page+1}页]\n" + doc.page_content
        else:
            doc.page_content = f"[来源文件: {filename}]\n" + doc.page_content
    return documents

def create_index_from_files(file_names: list[str]):
    """
    从指定的文件列表创建或更新 FAISS 索引。
    file_names: 在 UPLOAD_FOLDER 中的文件名列表。
    """
    logger.info(f"开始从文件列表创建/更新 FAISS 索引: {file_names}")
    doc_paths = [os.path.join(UPLOAD_FOLDER, fn) for fn in file_names]
    all_docs = []
    processed_files = load_processed_files()
    newly_processed = []

    for doc_path in doc_paths:
        file_name_for_log = os.path.basename(doc_path)
        if not os.path.exists(doc_path):
            logger.warning(f"文件 '{file_name_for_log}' 在路径 '{doc_path}' 未找到，已跳过。")
            continue
        if file_name_for_log in processed_files:
            logger.info(f"文件 '{file_name_for_log}' 已处理过，跳过。")
            continue
        
        loader = None
        try:
            if doc_path.lower().endswith(".txt"):
                logger.info(f"正在加载 TXT 文件: {file_name_for_log}...")
                loader = TextLoader(doc_path, encoding="utf-8")
            elif doc_path.lower().endswith(".pdf"):
                logger.info(f"正在加载 PDF 文件: {file_name_for_log}...")
                loader = PyPDFLoader(doc_path)
            else:
                logger.warning(f"不支持的文件格式 '{file_name_for_log}'，已跳过。")
                continue
            
            if loader:
                documents = loader.load()
                documents = inject_filename_to_documents(documents, doc_path)  # 注入文件名
                all_docs.extend(documents)
                newly_processed.append(file_name_for_log)
                logger.info(f"文件 '{file_name_for_log}' 加载成功，包含 {len(documents)} 个 Langchain Document 对象。")

        except Exception as e:
            logger.error(f"加载文件 '{file_name_for_log}' 时出错: {e}", exc_info=True)
            continue
    
    if not all_docs:
        logger.warning("没有成功加载任何文档，无法创建或更新索引。")
        return False

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
        separators=["\n\n", "\n", "。", ". ", "！", "？", "，", "、", "；", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(all_docs)
    logger.info(f"所有文档内容已分割完成，共生成 {len(split_docs)} 个文本片段用于嵌入。")

    try:
        logger.info(f"正在使用 Ollama 嵌入模型: {OLLAMA_EMBEDDING_MODEL}")
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

        if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
            logger.info("检测到已有索引，正在执行增量添加...")
            vector_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            vector_db.add_documents(split_docs)
        else:
            logger.info("首次创建索引...")
            vector_db = FAISS.from_documents(split_docs, embeddings)

        vector_db.save_local(FAISS_INDEX_PATH)
        logger.info(f"FAISS 索引已成功保存至: {FAISS_INDEX_PATH}")

        processed_files.update(newly_processed)
        save_processed_files(processed_files)

        return True
    except Exception as e:
        logger.error(f"创建 FAISS 索引时出错: {e}", exc_info=True)
        logger.error(f"请确保 Ollama 服务正在运行，并且模型 '{OLLAMA_EMBEDDING_MODEL}' 已通过 'ollama pull {OLLAMA_EMBEDDING_MODEL}' 下载。")
        return False

def load_faiss_index():
    """加载本地的 FAISS 索引。"""
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
        try:
            embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
            vector_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            logger.info(f"FAISS 索引已从 {FAISS_INDEX_PATH} 加载。")
            return vector_db
        except Exception as e:
            logger.error(f"加载 FAISS 索引时出错: {e}", exc_info=True)
            return None
    else:
        logger.info(f"FAISS 索引目录 {FAISS_INDEX_PATH} 不存在或为空，将不会加载现有索引。")
        return None

def rebuild_index_from_all_files():
    """从 upload 文件夹中所有文件重新构建索引"""
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.pdf', '.txt'))]
        if not files:
            return False, "知识库中没有可用文件"
        success = create_index_from_files(files)
        return success, f"索引刷新 {'成功' if success else '失败'}，处理了 {len(files)} 个文件。"
    except Exception as e:
        logger.error(f"刷新索引失败: {e}", exc_info=True)
        return False, f"刷新失败：{str(e)}"
