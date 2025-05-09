# backend/knowledge_base_processor.py
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings # 确保使用新的包
from langchain_community.vectorstores import FAISS

# 从 config.py 导入配置
from .config import UPLOAD_FOLDER, FAISS_INDEX_PATH, OLLAMA_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

def create_index_from_files(file_names: list[str]):
    """
    从指定的文件列表创建或更新 FAISS 索引。
    file_names: 在 UPLOAD_FOLDER 中的文件名列表，例如 ["sample_apple_info.txt"]
    """
    doc_paths = [os.path.join(UPLOAD_FOLDER, fn) for fn in file_names]
    all_docs = []

    for doc_path in doc_paths:
        if not os.path.exists(doc_path):
            print(f"警告：文件 {doc_path} 不存在，已跳过。")
            continue
        try:
            # 目前只支持 .txt，后续可以根据 get_loader 扩展
            if doc_path.endswith(".txt"):
                loader = TextLoader(doc_path, encoding="utf-8")
                documents = loader.load()
                all_docs.extend(documents)
            else:
                print(f"警告：不支持的文件格式 {doc_path}，已跳过。")
        except Exception as e:
            print(f"加载文件 {doc_path} 出错: {e}")
            continue
    
    if not all_docs:
        print("没有成功加载任何文档，无法创建索引。")
        return False

    text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    split_docs = text_splitter.split_documents(all_docs)

    print(f"文档分割完成，共 {len(split_docs)} 个片段。")

    # 确保 Ollama 服务正在运行，并且 bge-m3 模型已下载 (ollama pull bge-m3)
    try:
        print(f"正在使用 Ollama 嵌入模型: {OLLAMA_EMBEDDING_MODEL}")
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        
        print("正在创建 FAISS 索引...")
        vector_db = FAISS.from_documents(split_docs, embeddings)
        vector_db.save_local(FAISS_INDEX_PATH)
        print(f"FAISS 索引已成功创建并保存到: {FAISS_INDEX_PATH}")
        return True
    except Exception as e:
        print(f"创建 FAISS 索引时出错: {e}")
        print("请确保 Ollama 服务正在运行，并且模型 '{OLLAMA_EMBEDDING_MODEL}' 已通过 'ollama pull {OLLAMA_EMBEDDING_MODEL}' 下载。")
        return False

def load_faiss_index():
    """加载本地的 FAISS 索引。"""
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH): # 确保目录存在且不为空
        try:
            embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
            # 对于较新版本的 FAISS 和 LangChain，可能需要 allow_dangerous_deserialization=True
            # 具体取决于您的 FAISS 版本和 LangChain 如何处理 pickle
            vector_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            print(f"FAISS 索引已从 {FAISS_INDEX_PATH} 加载。")
            return vector_db
        except Exception as e:
            print(f"加载 FAISS 索引时出错: {e}")
            return None
    else:
        print(f"FAISS 索引目录 {FAISS_INDEX_PATH} 不存在或为空。")
        return None