from __future__ import annotations
from typing import Any
from pathlib import Path
import json
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
        if ("/" in model_path or "\\" in model_path) and not os.path.exists(model_path):
            print(f"[*] 未检测到本地模型 {model_path}，正在自动下载 BAAI/bge-small-zh-v1.5 ...")
            try:
                from huggingface_hub import snapshot_download
                snapshot_download(repo_id="BAAI/bge-small-zh-v1.5", local_dir=model_path)
                print("[*] 模型自动下载完成！")
            except Exception as e:
                print(f"[!] 自动下载模型失败，请检查网络或手动下载: {e}")
        if os.path.exists(model_path):
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
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
        # ---- 新增：用于保存所有完整 parsed_doc 的空间 ----
        self.all_parsed_docs: list[dict[str, Any]] = []
        self.persist_dir_path = Path(persist_dir or Config.CHROMA_PERSIST_DIR)
        self.docs_storage_file = self.persist_dir_path / f"_parsed_docs_storage_{collection_name}.json"
        # 如果持久化目录中已有历史数据，自动加载以防程序重启丢失
        if self.docs_storage_file.exists():
            try:
                self.all_parsed_docs = json.loads(self.docs_storage_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.all_parsed_docs = []
    def _generate_summary(self, file_name: str, chunks: list[str]) -> str:
        """Use LLM to generate a summary of the document."""
        try:
            from core.llm_factory import create_llm
            llm = create_llm()
            preview = "\n".join(chunks[:5])[:3000]
            response = llm.invoke(
                f"请用中文为以下文档生成一段简洁的摘要(100-200字)，概括文档的主题、关键内容和要点。\n\n"
                f"文件名: {file_name}\n\n内容片段:\n{preview}"
            )
            content = getattr(response, "content", "")
            if isinstance(content, list):
                content = "\n".join(str(p) for p in content)
            return str(content).strip() or ""
        except Exception as e:
            print(f"[SUMMARY] Failed to generate summary for {file_name}: {e}")
            return ""
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
        if "summary" not in parsed_doc or not parsed_doc["summary"]:
            parsed_doc["summary"] = self._generate_summary(file_name, chunks)
        self.all_parsed_docs = [d for d in self.all_parsed_docs if d.get("file_name") != file_name]
        self.all_parsed_docs.append(parsed_doc)
        self.persist_dir_path.mkdir(parents=True, exist_ok=True)
        self.docs_storage_file.write_text(
            json.dumps(self.all_parsed_docs, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
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
    # ---- 新增：提供一个便捷方法，获取所有文档的纯文本拼接 ----
    def get_full_text(self, separator: str = "\n\n") -> str:
        """从所有 parsed_doc 中提取 text 字段并拼接返回"""
        text_parts = []
        for doc in self.all_parsed_docs:
            text = doc.get("text") or doc.get("raw_text")
            if text:
                text_parts.append(text)
            else:
                text_parts.append("\n".join(doc.get("chunks", [])))
        return separator.join(text_parts)

    def remove_document(self, file_name: str) -> bool:
        """从知识库中删除指定文件名的文档及其所有分块"""
        # 从 ChromaDB 中删除对应分块
        try:
            self.collection.delete(where={"source": file_name})
        except Exception:
            # 如果 where 过滤不支持，按 ID 前缀删除
            try:
                ids_to_delete = [f"{file_name}_{i}" for i in range(10000)]
                existing = self.collection.get(ids=ids_to_delete[:100])
                if existing and existing["ids"]:
                    self.collection.delete(ids=existing["ids"])
            except Exception:
                pass

        # 从 parsed_docs 中移除
        before = len(self.all_parsed_docs)
        self.all_parsed_docs = [d for d in self.all_parsed_docs if d.get("file_name") != file_name]
        removed = before - len(self.all_parsed_docs)

        # 持久化
        self.persist_dir_path.mkdir(parents=True, exist_ok=True)
        self.docs_storage_file.write_text(
            json.dumps(self.all_parsed_docs, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return removed > 0

    def search_documents(self, query: str = "", file_format: str = "", top_k: int = 20) -> list[dict]:
        """搜索知识库中的文档（元数据级别，非分块级别）"""
        results = []
        for doc in self.all_parsed_docs:
            name = doc.get("file_name", "")
            fmt = doc.get("metadata", {}).get("format", "")
            chunks = doc.get("chunks", [])

            if file_format and fmt != file_format:
                continue
            if query and query.lower() not in name.lower():
                continue

            results.append({
                "file_name": name,
                "format": fmt,
                "chunk_count": len(chunks),
                "preview": (chunks[0][:200] + "...") if chunks else "",
                "source_path": doc.get("metadata", {}).get("source", ""),
            })

        return results[:top_k]
