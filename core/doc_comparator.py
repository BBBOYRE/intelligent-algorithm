"""两文档 LLM 对比分析"""
from __future__ import annotations

from pathlib import Path
from core.llm_factory import create_llm
from core.document_parser import DocumentParser
from langchain_core.prompts import ChatPromptTemplate


class DocComparator:
    def __init__(self):
        self.llm = create_llm()
        self.parser = DocumentParser()

    def compare(self, file_path_a: str | Path, file_path_b: str | Path) -> dict:
        doc_a = self.parser.parse(file_path_a)
        doc_b = self.parser.parse(file_path_b)

        text_a = (doc_a.get("markdown") or "")[:4000]
        text_b = (doc_b.get("markdown") or "")[:4000]

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是文档对比分析专家。请对比以下两个文档，输出结构化的对比报告。

报告格式要求：
1. **概要差异**：一句话总结两个文档的主要区别
2. **内容对比**：逐项列出关键差异点（新增、删除、修改的内容）
3. **结构差异**：格式、章节、表格等结构上的不同
4. **建议**：基于差异给出合并或修改建议

用中文回答，使用 Markdown 格式。"""),
            ("human", "文档A（{name_a}）:\n{text_a}\n\n---\n\n文档B（{name_b}）:\n{text_b}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "name_a": doc_a["file_name"],
            "name_b": doc_b["file_name"],
            "text_a": text_a,
            "text_b": text_b,
        })

        content = getattr(response, "content", str(response))
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        return {
            "status": "success",
            "file_a": doc_a["file_name"],
            "file_b": doc_b["file_name"],
            "report": content,
        }
