import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))
class Config:
    # ==================== 部署模式 ====================
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "private")  # "private" | "saas"
    AUTH_DISABLED = os.getenv("AUTH_DISABLED", "false").lower() == "true"

    # ==================== 数据库配置 ====================
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'data', 'db', 'app.db')}")

    # ==================== JWT 配置 ====================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 默认24小时

    # ==================== LLM 配置 ====================
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

    # ==================== Embedding 配置 ====================
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", os.path.join(BASE_DIR, "data", "models", "bge-small-zh-v1.5"))
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "")

    # ==================== ChromaDB 配置 ====================
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join(BASE_DIR, "data", "chroma_db"))

    # ==================== 文件路径 ====================
    UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "outputs")
    DB_DIR = os.path.join(BASE_DIR, "data", "db")

    # ==================== RAG 参数 ====================
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "15"))
    CHUNK_SIZE = 512
