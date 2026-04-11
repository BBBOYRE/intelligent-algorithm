from config import Config


def create_llm():
    """根据配置创建 LLM 实例（支持本地 / 云端切换）"""
    provider = Config.LLM_PROVIDER.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=Config.LLM_MODEL,
            base_url=Config.LLM_BASE_URL or "http://localhost:11434",
            temperature=0,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=Config.LLM_MODEL,
            base_url=Config.LLM_BASE_URL,
            api_key=Config.LLM_API_KEY,
            temperature=0,
        )
