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

    def fill_template(self, template_path: str | Path, output_path: str | Path) -> dict[str, Any]:
        path = Path(template_path)
        out = Path(output_path)

        parsed = self.template_parser.parse_template(path)
        template_md = parsed["markdown"]
        coordinates = parsed["coordinates"]

        suffix = path.suffix.lower()
        if suffix == ".docx":
            return self._fill_word(path, out, template_md, coordinates)
        if suffix in {".xlsx", ".xls"}:
            return self._fill_excel(path, out, template_md, coordinates)
        raise ValueError(f"Unsupported template format: {suffix}")

    def _fill_word(self, template_path: Path, output_path: Path, template_md: str, coordinates: list[dict]) -> dict:
        doc = DocxDocument(template_path)
        total_filled = 0

        for table_info in coordinates:
            headers = [h for h in table_info.get("headers", []) if h]
            if not headers:
                continue

            table = doc.tables[table_info["table_index"]]
            hits = self.kb.search(", ".join(headers), top_k=8)
            context = "\n\n".join([h["text"] for h in hits])
            fill_rows = self._extract_data(template_md, headers, context)

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

    def _fill_excel(self, template_path: Path, output_path: Path, template_md: str, coordinates: list[dict]) -> dict:
        wb = load_workbook(template_path)
        total_filled = 0

        for sheet_info in coordinates:
            ws = wb[sheet_info["sheet_name"]]
            headers_map: dict[str, str] = sheet_info.get("headers", {})
            if not headers_map:
                continue

            header_names = list(headers_map.values())
            hits = self.kb.search(", ".join(header_names), top_k=8)
            context = "\n\n".join([h["text"] for h in hits])
            fill_rows = self._extract_data(template_md, header_names, context)

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

    def _extract_data(self, template_md: str, headers: list[str], context: str) -> list[dict[str, Any]]:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是数据提取专家。根据模板和上下文提取结构化数据。

模板（Markdown）:
{template_md}

字段:
{headers}

规则:
1. 必须返回 JSON 数组。
2. 每个元素表示一行。
3. 字段名必须与给定字段一致。
4. 未找到的信息填 N/A。""",
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
            }
        )

        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            match = re.search(r"\[.*\]", content, flags=re.DOTALL)
            if not match:
                return []
            try:
                parsed = json.loads(match.group(0))
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
