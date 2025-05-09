# backend/knowledge_base_processor.py
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader # <--- 导入 PyPDFLoader
# 如果您想支持 .docx, 可以取消注释下一行并确保安装了 python-docx 和 unstructured
# from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings # 确保使用新的包
from langchain_community.vectorstores import FAISS

# 从 config.py 导入配置
from .config import UPLOAD_FOLDER, FAISS_INDEX_PATH, OLLAMA_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

def create_index_from_files(file_names: list[str]):
    """
    从指定的文件列表创建或更新 FAISS 索引。
    file_names: 在 UPLOAD_FOLDER 中的文件名列表，例如 ["sample_apple_info.txt", "product_manual.pdf"]
    """
    doc_paths = [os.path.join(UPLOAD_FOLDER, fn) for fn in file_names]
    all_docs = [] # 用于存储从所有文件中加载的文档对象

    for doc_path in doc_paths:
        file_name_for_log = os.path.basename(doc_path) # 获取文件名用于日志记录
        if not os.path.exists(doc_path):
            print(f"警告：文件 '{file_name_for_log}' 在路径 '{doc_path}' 未找到，已跳过。")
            continue
        
        loader = None # 初始化加载器为 None
        try:
            if doc_path.lower().endswith(".txt"):
                print(f"正在加载 TXT 文件: {file_name_for_log}...")
                loader = TextLoader(doc_path, encoding="utf-8")
            elif doc_path.lower().endswith(".pdf"):
                print(f"正在加载 PDF 文件: {file_name_for_log}...")
                # 确保您已安装 pypdf: pip install pypdf
                loader = PyPDFLoader(doc_path)
            # elif doc_path.lower().endswith(".docx"): # 示例：如何添加对 .docx 文件的支持
            #     print(f"正在加载 DOCX 文件: {file_name_for_log}...")
            #     # 确保您已安装 python-docx 和 unstructured: pip install python-docx unstructured
            #     loader = UnstructuredWordDocumentLoader(doc_path)
            # TODO: 在这里为其他文档格式添加更多的 elif 条件和相应的加载器
            else:
                print(f"警告：不支持的文件格式 '{file_name_for_log}'，已跳过。")
                continue # 跳过当前文件，处理下一个
            
            # 如果成功选择了加载器，则加载文档
            if loader:
                documents = loader.load()
                all_docs.extend(documents)
                print(f"文件 '{file_name_for_log}' 加载成功，包含 {len(documents)} 个 Langchain Document 对象。")

        except Exception as e:
            print(f"加载文件 '{file_name_for_log}' 时出错: {e}")
            continue # 加载单个文件出错时，跳过此文件，继续处理其他文件
    
    if not all_docs:
        print("没有成功加载任何文档，无法创建或更新索引。")
        return False

    # 统一对所有加载的文档内容进行文本分割
    # 注意：CharacterTextSplitter 对于某些格式（如PDF分頁）可能不是最优，
    # RecursiveCharacterTextSplitter 配合合适的参数可能效果更好。
    # 但 CharacterTextSplitter 作为起点是OK的。
    text_splitter = CharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP,
        separator="\n" # 可以尝试不同的分隔符，例如 "\n\n" 或 " "
    )
    split_docs = text_splitter.split_documents(all_docs)

    print(f"所有文档内容已分割完成，共生成 {len(split_docs)} 个文本片段用于嵌入。")

    # 确保 Ollama 服务正在运行，并且 bge-m3 模型已下载 (ollama pull bge-m3)
    try:
        print(f"正在使用 Ollama 嵌入模型: {OLLAMA_EMBEDDING_MODEL}")
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        
        # 创建或覆盖 FAISS 索引
        # 当前逻辑是：每次调用都基于本次传入的 file_names 中的内容来构建一个全新的索引并覆盖旧的。
        # 如果您希望是增量添加（即保留旧索引中的内容，并加入新文档的内容），
        # 则需要先加载现有索引 (FAISS.load_local)，然后使用 vector_db.add_documents(split_docs)。
        # 为了课程作业的简化，覆盖方式更容易实现。
        print("正在创建/覆盖 FAISS 索引...")
        vector_db = FAISS.from_documents(split_docs, embeddings)
        vector_db.save_local(FAISS_INDEX_PATH) # 保存到 .config 中定义的路径
        print(f"FAISS 索引已成功创建/覆盖，并保存到: {FAISS_INDEX_PATH}")
        return True
    except Exception as e:
        print(f"创建 FAISS 索引时出错: {e}")
        print(f"请确保 Ollama 服务正在运行，并且模型 '{OLLAMA_EMBEDDING_MODEL}' 已通过 'ollama pull {OLLAMA_EMBEDDING_MODEL}' 下载。")
        return False

def load_faiss_index():
    """加载本地的 FAISS 索引。"""
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH): # 确保目录存在且不为空
        try:
            embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
            # 注意：allow_dangerous_deserialization=True 对于 LangChain 加载 FAISS 索引通常是必需的
            # 因为 FAISS 索引中可能包含 Python 的 pickle 对象
            vector_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            print(f"FAISS 索引已从 {FAISS_INDEX_PATH} 加载。")
            return vector_db
        except Exception as e:
            print(f"加载 FAISS 索引时出错: {e}")
            # 可以考虑在这里返回 None 或者抛出异常，让调用者处理
            return None
    else:
        print(f"FAISS 索引目录 {FAISS_INDEX_PATH} 不存在或为空。")
        return None