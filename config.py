import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ==================== LLM 配置 ====================
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

    # ==================== Embedding 配置 ====================
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "")

    # ==================== ChromaDB 配置 ====================
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # ==================== 文件路径 ====================
    UPLOAD_DIR = "./data/uploads"
    OUTPUT_DIR = "./data/outputs"

    # ==================== RAG 参数 ====================
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "15"))
    CHUNK_SIZE = 512
