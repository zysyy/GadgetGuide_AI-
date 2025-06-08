import os
import logging
from dotenv import load_dotenv

# --- 日志配置 ---
logger = logging.getLogger("gadgetguide_ai")

# --- 加载 API 密钥 ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- JWT 配置（新加）---
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 天

# --- BASE_DIR 配置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'users.db')}"

# --- DEBUG 日志输出 ---
logger.debug(f"--- In config.py ---")
if DEEPSEEK_API_KEY:
    logger.debug(f"Value of DEEPSEEK_API_KEY loaded by os.getenv: Key is present (e.g., '{DEEPSEEK_API_KEY[:5]}...')")
    logger.debug(f"Type of DEEPSEEK_API_KEY: {type(DEEPSEEK_API_KEY)}")
else:
    logger.warning("Value of DEEPSEEK_API_KEY loaded by os.getenv is: None. API Key is MISSING or not loaded correctly.")
logger.debug(f"--- End of API Key check in config.py ---")

# --- 数据库配置 ---
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'users.db')}")
if "sqlite" in DATABASE_URL:
    logger.debug(f"Using SQLite database at: {DATABASE_URL}")
else:
    logger.debug(f"Using external database (e.g., MySQL/PostgreSQL): {DATABASE_URL}")

# --- Ollama 配置 ---
OLLAMA_EMBEDDING_MODEL = "bge-m3"
logger.debug(f"Ollama embedding model set to: {OLLAMA_EMBEDDING_MODEL}")

# --- 路径配置 ---
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

logger.debug(f"BASE_DIR set to: {BASE_DIR}")
logger.debug(f"UPLOAD_FOLDER set to: {UPLOAD_FOLDER}")
logger.debug(f"FAISS_INDEX_PATH set to: {FAISS_INDEX_PATH}")

# --- 确保路径存在 ---
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    logger.debug(f"Ensured UPLOAD_FOLDER ('{UPLOAD_FOLDER}') and FAISS_INDEX_PATH ('{FAISS_INDEX_PATH}') exist.")
except OSError as e:
    logger.error(f"Error creating directories UPLOAD_FOLDER or FAISS_INDEX_PATH: {e}", exc_info=True)

# --- 文本分割参数 ---
CHUNK_SIZE = 350
CHUNK_OVERLAP = 70
logger.debug(f"CHUNK_SIZE set to: {CHUNK_SIZE}")
logger.debug(f"CHUNK_OVERLAP set to: {CHUNK_OVERLAP}")

logger.info("Configuration from config.py loaded.")
