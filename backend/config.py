# backend/config.py
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
# 通常在 main.py 的开头执行 load_dotenv()，这里也可以先定义好
# load_dotenv() # 如果你想在这里直接加载

# API 密钥 (从环境变量获取)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
#验证是否成功读取env内key的内容
print(f"--- DEBUG INFO from config.py ---")
print(f"Value of DEEPSEEK_API_KEY loaded by os.getenv: '{DEEPSEEK_API_KEY}'")
print(f"Type of DEEPSEEK_API_KEY: {type(DEEPSEEK_API_KEY)}")
print(f"--- END DEBUG INFO from config.py ---")

# Ollama 配置
OLLAMA_EMBEDDING_MODEL = "bge-m3" # 您选择的嵌入模型

# 路径配置 (相对于 backend 目录或者使用绝对路径)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # config.py 所在的目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

# 其他配置可以放这里，比如文本分割参数等
CHUNK_SIZE = 350
CHUNK_OVERLAP = 70

