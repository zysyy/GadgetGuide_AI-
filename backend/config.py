# backend/config.py
import os
import logging # <--- 1. 导入 logging 模块
from dotenv import load_dotenv # 虽然 load_dotenv() 主要在 main.py 调用，但保留导入以备不时之需或独立测试

# --- 2. 获取在 main.py 中配置的根 logger 或创建一个子 logger ---
# 我们使用与 main.py 中相同的 logger 名称 "gadgetguide_ai"，
# 这样它会自动继承 main.py 中为该 logger 名称配置的 handlers 和 formatters。
# 或者，可以创建子 logger: logger = logging.getLogger("gadgetguide_ai.config")
logger = logging.getLogger("gadgetguide_ai")

# --- API 密钥 ---
# load_dotenv() 应该已经在 main.py 的最顶部被调用了，
# 所以这里的 os.getenv 应该能读取到已加载到环境中的变量。
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 3. 使用 logger 替代 print 进行调试信息输出 ---
logger.debug(f"--- In config.py ---")
if DEEPSEEK_API_KEY:
    # 为了安全，通常不在日志中完整打印API Key，这里只打印部分或是否存在状态
    logger.debug(f"Value of DEEPSEEK_API_KEY loaded by os.getenv: Key is present (e.g., '{DEEPSEEK_API_KEY[:5]}...')")
    logger.debug(f"Type of DEEPSEEK_API_KEY: {type(DEEPSEEK_API_KEY)}")
else:
    logger.warning("Value of DEEPSEEK_API_KEY loaded by os.getenv is: None. API Key is MISSING or not loaded correctly.")
logger.debug(f"--- End of API Key check in config.py ---")


# --- Ollama 配置 ---
OLLAMA_EMBEDDING_MODEL = "bge-m3"
logger.debug(f"Ollama embedding model set to: {OLLAMA_EMBEDDING_MODEL}")

# --- 路径配置 ---
# __file__ 是当前文件 (config.py) 的路径
# os.path.abspath(__file__) 获取绝对路径
# os.path.dirname(...) 获取该文件所在的目录 (即 backend/ 目录)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

logger.debug(f"BASE_DIR set to: {BASE_DIR}")
logger.debug(f"UPLOAD_FOLDER set to: {UPLOAD_FOLDER}")
logger.debug(f"FAISS_INDEX_PATH set to: {FAISS_INDEX_PATH}")

# --- 确保目录存在 ---
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    logger.debug(f"Ensured UPLOAD_FOLDER ('{UPLOAD_FOLDER}') and FAISS_INDEX_PATH ('{FAISS_INDEX_PATH}') exist.")
except OSError as e:
    logger.error(f"Error creating directories UPLOAD_FOLDER or FAISS_INDEX_PATH: {e}", exc_info=True)


# --- 文本分割参数等其他配置 ---
CHUNK_SIZE = 350
CHUNK_OVERLAP = 70
logger.debug(f"CHUNK_SIZE set to: {CHUNK_SIZE}")
logger.debug(f"CHUNK_OVERLAP set to: {CHUNK_OVERLAP}")

logger.info("Configuration from config.py loaded.")