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
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一个中文文档理解助手。请严格基于提供的知识库片段回答问题。
规则：
1. 回答语言必须是中文。
2. 若证据不足，明确说明“当前知识库信息不足”。
3. 结尾附上“来源”摘要（文件名列表）。""",
                ),
                (
                    "human",
                    """用户问题：{question}

知识库片段：
{context}

历史对话（可为空）：
{history}""",
                ),
            ]
        )

    def _format_history(self, chat_history: list[dict[str, Any]] | None) -> str:
        if not chat_history:
            return "无"
        lines: list[str] = []
        for item in chat_history[-6:]:
            role = item.get("role", "user")
            content = str(item.get("content", "")).strip()
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines) if lines else "无"

    def chat(self, message: str, chat_history: list[dict[str, Any]] | None = None) -> str:
        results = self.kb.search(message, top_k=5)
        if not results:
            return "当前知识库信息不足，暂时无法给出可靠答案。请先上传相关文档后再试。"

        context = "\n\n---\n\n".join(
            f"[来源: {row['metadata'].get('source', 'unknown')}]\n{row['text']}" for row in results
        )
        chain = self.prompt | self.llm
        response = chain.invoke(
            {
                "question": message,
                "context": context,
                "history": self._format_history(chat_history),
            }
        )

        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        return str(content).strip() or "未生成有效回答，请重试。"
