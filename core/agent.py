from __future__ import annotations
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from core.knowledge_base import KnowledgeBase
from core.llm_factory import create_llm

class DocumentAgent:
    """KB-driven document assistant compatible with LangChain 1.x."""

    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self.kb = knowledge_base
        self.llm = create_llm()
        self.rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个中文文档理解助手。请基于提供的知识库片段回答问题。\n"
                    "规则:\n"
                    "1. 回答语言必须是中文。\n"
                    "2. 若知识库片段不足以回答，可结合自身知识补充，但需注明哪些内容来自知识库、哪些是补充。\n"
                    "3. 结尾附上[来源]摘要(文件名列表)。\n\n"
                    "当前知识库状态:\n{kb_info}",
                ),
                (
                    "human",
                    "用户问题: {question}\n\n"
                    "知识库片段:\n{context}\n\n"
                    "历史对话(可为空):\n{history}",
                ),
            ]
        )
        self.general_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个智能中文助手，能够回答各类问题。\n"
                    "规则:\n"
                    "1. 回答语言必须是中文。\n"
                    "2. 回答要准确、简洁、有条理。\n"
                    "3. 如果不确定，请如实说明。\n\n"
                    "当前知识库状态:\n{kb_info}",
                ),
                (
                    "human",
                    "用户问题: {question}\n\n"
                    "历史对话(可为空):\n{history}",
                ),
            ]
        )

    def _get_kb_info(self) -> str:
        stats = self.kb.get_stats()
        docs = self.kb.all_parsed_docs
        file_count = len(docs)
        chunk_count = stats.get("total_chunks", 0)
        if file_count == 0:
            return "知识库为空，尚未上传任何文档。"
        parts = [f"共{file_count}个文件, {chunk_count}个文本块。\n"]
        for doc in docs[:15]:
            fname = doc.get("file_name", "unknown")
            summary = doc.get("summary", "")
            if summary:
                parts.append(f"- {fname}: {summary}")
            else:
                preview = ""
                chunks = doc.get("chunks", [])
                if chunks:
                    preview = chunks[0][:150] + "..."
                parts.append(f"- {fname}: {preview}")
        if file_count > 15:
            parts.append(f"...以及其他{file_count - 15}个文件")
        return "\n".join(parts)

    def _format_history(self, chat_history: list[dict[str, Any]] | None) -> str:
        if not chat_history:
            return "无"
        lines: list[str] = []
        # 提取最近的 6 条记录(相当于 3 轮对话)，防止上下文超出大模型限制
        for item in chat_history[-6:]:
            role = item.get("role", "user")
            content = str(item.get("content", "")).strip()
            if content:
                # 区分是用户的提问还是 AI 的回答
                display_role = "用户" if role == "user" else "AI助手"
                lines.append(f"{display_role}: {content}")
        return "\n".join(lines) if lines else "无"

    def _get_fallback_context(self, max_chars: int = 8000) -> str:
        """当语义检索无结果时，从知识库中尽可能多地拉取文档内容"""
        parts = []
        total = 0
        for doc in self.kb.all_parsed_docs:
            fname = doc.get("file_name", "unknown")
            chunks = doc.get("chunks", [])
            for chunk in chunks[:6]:
                snippet = chunk[:800]
                if total + len(snippet) > max_chars:
                    break
                parts.append(f"[来源: {fname}]\n{snippet}")
                total += len(snippet)
            if total >= max_chars:
                break
        return "\n\n---\n\n".join(parts) if parts else ""

    def chat(self, message: str, chat_history: list[dict[str, Any]] | None = None) -> str:
        # [核心修复 1] 确保 chat_history 是一个列表，方便后续追加数据
        if chat_history is None:
            chat_history = []

        from core.retriever import retrieve_context

        context = retrieve_context(self.kb, message, top_k=15)
        fallback = self._get_fallback_context()
        if context and fallback:
            context = context + "\n\n---\n\n" + fallback
        elif not context:
            context = fallback
        formatted_history = self._format_history(chat_history)
        kb_info = self._get_kb_info()

        if context:
            chain = self.rag_prompt | self.llm
            response = chain.invoke(
                {"question": message, "context": context, "history": formatted_history, "kb_info": kb_info}
            )
        else:
            chain = self.general_prompt | self.llm
            response = chain.invoke(
                {"question": message, "history": formatted_history, "kb_info": kb_info}
            )

        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        final_answer = str(content).strip() or "未生成有效回答，请重试。"

        # [核心修复 2] 将本次的"用户提问"和"模型回答"追加到历史记录中！
        # 这样下一次调用 chat() 时，大模型就能看到这一次的对话了。
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": final_answer})

        return final_answer

    def stream_chat(self, message: str, chat_history: list[dict[str, Any]] | None = None) -> Any:
        if chat_history is None:
            chat_history = []

        from core.retriever import retrieve_context

        context = retrieve_context(self.kb, message, top_k=15)
        fallback = self._get_fallback_context()
        if context and fallback:
            context = context + "\n\n---\n\n" + fallback
        elif not context:
            context = fallback
        formatted_history = self._format_history(chat_history)
        kb_info = self._get_kb_info()

        if context:
            chain = self.rag_prompt | self.llm
            for chunk in chain.stream(
                {"question": message, "context": context, "history": formatted_history, "kb_info": kb_info}
            ):
                yield chunk.content
        else:
            chain = self.general_prompt | self.llm
            for chunk in chain.stream(
                {"question": message, "history": formatted_history, "kb_info": kb_info}
            ):
                yield chunk.content