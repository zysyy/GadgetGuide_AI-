# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import DATABASE_URL, logger


# --- 日志记录数据库初始化 ---
logger.debug("--- Initializing database.py ---")

# --- SQLite 连接参数特殊处理 ---
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# --- 创建数据库引擎 ---
try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    logger.info(f"Database engine created with URL: {DATABASE_URL}")
except Exception as e:
    logger.error("Failed to create database engine", exc_info=True)
    raise

# --- 创建 Session 工厂 ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 创建模型继承的基础类 ---
Base = declarative_base()

logger.debug("--- database.py loaded successfully ---")
