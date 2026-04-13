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
        # 提取最近的 6 条记录（相当于 3 轮对话），防止上下文超出大模型限制
        for item in chat_history[-6:]:
            role = item.get("role", "user")
            content = str(item.get("content", "")).strip()
            if content:
                # 区分是用户的提问还是 AI 的回答
                display_role = "用户" if role == "user" else "AI助手"
                lines.append(f"{display_role}: {content}")
        return "\n".join(lines) if lines else "无"

    def chat(self, message: str, chat_history: list[dict[str, Any]] | None = None) -> str:
        # [核心修复 1] 确保 chat_history 是一个列表，方便后续追加数据
        if chat_history is None:
            chat_history = []

        from core.retriever import retrieve_context
        
        context = retrieve_context(self.kb, message, top_k=5)
        if not context:
            return "当前知识库信息不足，暂时无法给出可靠答案。请先上传相关文档后再试。"

        # 此时的 history 里面只有之前的对话，不包含当前的新问题
        formatted_history = self._format_history(chat_history)

        chain = self.prompt | self.llm
        response = chain.invoke(
            {
                "question": message,
                "context": context,
                "history": formatted_history,
            }
        )

        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        final_answer = str(content).strip() or "未生成有效回答，请重试。"

        # [核心修复 2] 将本次的“用户提问”和“模型回答”追加到历史记录中！
        # 这样下一次调用 chat() 时，大模型就能看到这一次的对话了。
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": final_answer})

        return final_answer