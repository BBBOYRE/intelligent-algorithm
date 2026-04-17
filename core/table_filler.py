from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

from docx import Document as DocxDocument
from langchain_core.prompts import ChatPromptTemplate
from openpyxl import load_workbook

from core.knowledge_base import KnowledgeBase
from core.llm_factory import create_llm
from utils.template_parser import TemplateParser


class TableFiller:
    """Auto-fill Word/Excel template tables from KB context."""

    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self.kb = knowledge_base
        self.llm = create_llm()
        self.template_parser = TemplateParser()

    def fill_template(self, template_path: str | Path, output_path: str | Path, requirements: str = "", precision: str = "fine") -> dict[str, Any]:
        path = Path(template_path)
        out = Path(output_path)
        parsed = self.template_parser.parse_template(path)
        template_md = parsed["markdown"]
        coordinates = parsed["coordinates"]
        suffix = path.suffix.lower()
        if suffix == ".docx":
            return self._fill_word(path, out, template_md, coordinates, requirements, precision)
        if suffix in {".xlsx", ".xls"}:
            return self._fill_excel(path, out, template_md, coordinates, requirements, precision)
        raise ValueError(f"Unsupported template format: {suffix}")

    def preview_fill(self, template_path: str | Path, requirements: str = "", precision: str = "fine") -> dict[str, Any]:
        """预览填写结果，返回结构化数据但不写入文件"""
        path = Path(template_path)
        parsed = self.template_parser.parse_template(path)
        template_md = parsed["markdown"]
        coordinates = parsed["coordinates"]

        tables = []
        for coord in coordinates:
            if path.suffix.lower() == ".docx":
                headers = [h for h in coord.get("headers", []) if h]
            else:
                headers = list(coord.get("headers", {}).values())
            if not headers:
                continue
            context = self._get_context(headers, precision)
            rows = self._extract_data(template_md, headers, context, requirements)
            tables.append({"headers": headers, "rows": rows})

        return {"status": "success", "tables": tables}

    def _fill_word(self, template_path: Path, output_path: Path, template_md: str, coordinates: list[dict], requirements: str, precision: str) -> dict:
        doc = DocxDocument(template_path)
        total_filled = 0
        for table_info in coordinates:
            headers = [h for h in table_info.get("headers", []) if h]
            if not headers:
                continue
            table = doc.tables[table_info["table_index"]]
            context = self._get_context(headers, precision)
            fill_rows = self._extract_data(template_md, headers, context, requirements)
            for row_idx, row_data in enumerate(fill_rows):
                write_row_index = row_idx + 1
                if write_row_index >= len(table.rows):
                    table.add_row()
                row = table.rows[write_row_index]
                for col_idx, header in enumerate(headers):
                    if col_idx < len(row.cells) and header in row_data:
                        row.cells[col_idx].text = str(row_data[header])
                        total_filled += 1
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path)
        return {"status": "success", "filled_cells": total_filled, "output_path": str(output_path)}

    def _fill_excel(self, template_path: Path, output_path: Path, template_md: str, coordinates: list[dict], requirements: str, precision: str) -> dict:
        wb = load_workbook(template_path)
        total_filled = 0
        for sheet_info in coordinates:
            ws = wb[sheet_info["sheet_name"]]
            headers_map: dict[str, str] = sheet_info.get("headers", {})
            if not headers_map:
                continue
            header_names = list(headers_map.values())
            context = self._get_context(header_names, precision)
            fill_rows = self._extract_data(template_md, header_names, context, requirements)
            for row_idx, row_data in enumerate(fill_rows):
                excel_row = row_idx + 2
                for header_cell, header_name in headers_map.items():
                    col_letters = "".join(ch for ch in header_cell if ch.isalpha())
                    if header_name in row_data:
                        ws[f"{col_letters}{excel_row}"] = row_data[header_name]
                        total_filled += 1
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        return {"status": "success", "filled_cells": total_filled, "output_path": str(output_path)}

    def _get_context(self, headers: list[str], precision: str) -> str:
        if precision == "coarse":
            full_text = self.kb.get_full_text(separator="\n\n---\n\n")
            return full_text[:6000]

        # 精细模式：按字段分别检索 + 去重合并
        seen_texts: set[str] = set()
        all_hits: list[dict] = []
        per_header_k = max(3, 15 // len(headers)) if headers else 5

        for header in headers:
            hits = self.kb.search(header, top_k=per_header_k)
            for h in hits:
                if h["text"] not in seen_texts:
                    seen_texts.add(h["text"])
                    all_hits.append(h)

        all_hits.sort(key=lambda x: x.get("distance", 999))
        return "\n\n".join([h["text"] for h in all_hits[:15]])

    def _extract_data(self, template_md: str, headers: list[str], context: str, requirements: str) -> list[dict[str, Any]]:
        custom_rules = f"\n7. 用户特殊需求（最高优先级）：{requirements}" if requirements and requirements.strip() else ""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是数据提取专家。根据模板结构和上下文，提取所有匹配的结构化数据行。

模板（Markdown）:
{template_md}

需要提取的字段:
{headers}
{custom_rules}

严格规则:
1. 返回一个JSON数组，每个元素是一个对象，代表表格中的一行。
2. 对象的key必须与字段名完全一致（包括括号等符号）。
3. 从上下文中提取所有能找到的数据行，不要遗漏任何一条记录。
4. 保持原始值不变：数字、日期、百分比等照抄原文，不要转换格式。
5. 确实找不到的字段填空字符串""。
6. 只输出JSON数组，不要输出任何其他文字、解释或markdown代码块标记。

示例输出格式:
[{{"姓名": "张三", "部门": "技术部"}}, {{"姓名": "李四", "部门": "市场部"}}]""",
                ),
                ("human", "上下文如下:\n{context}"),
            ]
        )
        chain = prompt | self.llm
        response = chain.invoke(
            {
                "template_md": template_md,
                "headers": json.dumps(headers, ensure_ascii=False),
                "context": context or "",
                "custom_rules": custom_rules,
            }
        )
        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        parsed = self._parse_json_array(content)
        if parsed is not None:
            return parsed

        # 重试：让 LLM 修复 JSON
        repair_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是JSON修复专家。将以下文本修复为合法的JSON数组。只输出JSON数组，不要任何其他文字。"),
            ("human", "{broken_json}")
        ])
        repair_chain = repair_prompt | self.llm
        repair_response = repair_chain.invoke({"broken_json": content})
        repair_content = getattr(repair_response, "content", "")
        if isinstance(repair_content, list):
            repair_content = "\n".join(str(item) for item in repair_content)

        parsed = self._parse_json_array(repair_content)
        return parsed if parsed is not None else []

    @staticmethod
    def _parse_json_array(text: str) -> list | None:
        text = text.strip()
        # 去除可能的 markdown 代码块标记
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()
        try:
            result = json.loads(text)
            return result if isinstance(result, list) else None
        except json.JSONDecodeError:
            match = re.search(r"\[.*\]", text, flags=re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(0))
                    return result if isinstance(result, list) else None
                except json.JSONDecodeError:
                    return None
            return None
