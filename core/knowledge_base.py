from __future__ import annotations

from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from config import Config


def create_embedding_function() -> Any:
    """Create an embedding function based on configured provider."""
    provider = Config.EMBEDDING_PROVIDER.lower()

    if provider == "local":
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        import os

        model_path = Config.EMBEDDING_MODEL
        # 如果配置的是本地路径且不存在，则自动通过抱脸虫下载
        if ("/" in model_path or "\\" in model_path) and not os.path.exists(model_path):
            print(f"[*] 未检测到本地模型 {model_path}，正在自动下载 BAAI/bge-small-zh-v1.5 ...")
            try:
                from huggingface_hub import snapshot_download
                # 如果你需要换别的模型，请把 repo_id 换成对应的
                snapshot_download(repo_id="BAAI/bge-small-zh-v1.5", local_dir=model_path)
                print("[*] 模型自动下载完成！")
            except Exception as e:
                print(f"[!] 自动下载模型失败，请检查网络或手动下载: {e}")

        return SentenceTransformerEmbeddingFunction(model_name=model_path)

    if provider == "openai":
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

        return OpenAIEmbeddingFunction(
            api_key=Config.EMBEDDING_API_KEY,
            api_base=Config.EMBEDDING_BASE_URL or None,
            model_name=Config.EMBEDDING_MODEL,
        )

    if provider == "dashscope":
        from langchain_community.embeddings import DashScopeEmbeddings

        class DashscopeAdapter:
            def __init__(self) -> None:
                self._impl = DashScopeEmbeddings(
                    model=Config.EMBEDDING_MODEL,
                    dashscope_api_key=Config.EMBEDDING_API_KEY,
                )

            def __call__(self, input: list[str]) -> list[list[float]]:
                return self._impl.embed_documents(input)

        return DashscopeAdapter()

    raise ValueError(f"Unsupported embedding provider: {provider}")


class KnowledgeBase:
    """Chroma-backed vector knowledge base."""

    def __init__(self, persist_dir: str | None = None, collection_name: str = "documents") -> None:
        self.embed_fn = create_embedding_function()
        self.client = chromadb.PersistentClient(path=persist_dir or Config.CHROMA_PERSIST_DIR)
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(self, parsed_doc: dict[str, Any]) -> None:
        chunks = parsed_doc.get("chunks", [])
        if not chunks:
            return

        file_name = parsed_doc.get("file_name", "unknown")
        source_format = parsed_doc.get("metadata", {}).get("format", "")

        ids = [f"{file_name}_{idx}" for idx in range(len(chunks))]
        metadatas = [
            {"source": file_name, "format": source_format, "chunk_index": idx}
            for idx in range(len(chunks))
        ]

        self.collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)

    def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        if not query.strip() or self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k or Config.RETRIEVAL_TOP_K,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if results.get("distances") else [None] * len(documents)

        return [
            {"text": doc, "metadata": meta or {}, "distance": dist}
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

    def get_stats(self) -> dict[str, int]:
        return {"total_chunks": self.collection.count()}
