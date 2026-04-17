"""知识图谱：从知识库文档中提取实体和关系"""
from __future__ import annotations

import json
import re
from core.knowledge_base import KnowledgeBase
from core.llm_factory import create_llm
from langchain_core.prompts import ChatPromptTemplate


class KnowledgeGraphBuilder:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.llm = create_llm()

    def build_graph(self, top_k: int = 20) -> dict:
        all_text = self.kb.get_full_text(separator="\n\n---\n\n")
        if not all_text.strip():
            return {"nodes": [], "edges": []}
        if len(all_text) > 6000:
            all_text = all_text[:6000]

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是知识图谱构建专家。从给定文本中提取实体和关系，返回 JSON。

要求：
1. 提取重要实体（人名、组织、地点、日期、事件、概念等）
2. 提取实体之间的关系
3. 每个实体有 id、label（名称）、type（person/org/location/date/event/concept）
4. 每个关系有 from（源实体id）、to（目标实体id）、label（关系描述）
5. 只输出 JSON，格式如下：

{{"nodes": [{{"id": "n1", "label": "张三", "type": "person"}}, ...], "edges": [{{"from": "n1", "to": "n2", "label": "就职于"}}, ...]}}

提取 10-30 个最重要的实体和它们之间的关系。只输出 JSON。"""),
            ("human", "{text}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"text": all_text})
        content = getattr(response, "content", str(response))
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        return self._parse_graph(content)

    @staticmethod
    def _parse_graph(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "nodes" in data:
                return data
        except json.JSONDecodeError:
            match = re.search(r'\{.*"nodes".*"edges".*\}', text, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return {"nodes": [], "edges": []}
