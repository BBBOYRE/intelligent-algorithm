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
            rows = self._extract_data_adaptive(template_md, headers, context, requirements)
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
            fill_rows = self._extract_data_adaptive(template_md, headers, context, requirements)
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

    # 新增 precision 参数
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
            fill_rows = self._extract_data_adaptive(template_md, header_names, context, requirements)
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
        total_chunks = self.kb.get_stats().get("total_chunks", 0)
        print(f"[TABLE CTX] total_chunks={total_chunks} headers={headers} precision={precision}", flush=True)

        # 小文档（<50 chunks）：直接全文喂入
        if total_chunks <= 50:
            full_text = self.kb.get_full_text(separator="\n\n")
            print(f"[TABLE CTX] Small doc strategy: full_text={len(full_text)} chars", flush=True)
            return full_text[:30000]

        # 中等文档（50-300 chunks）：语义检索 + 全文补充
        if total_chunks <= 300:
            context = self._search_context(headers, top_per_header=10, max_hits=30)
            print(f"[TABLE CTX] Medium doc strategy: search={len(context)} chars", flush=True)
            if len(context) < 8000:
                full_text = self.kb.get_full_text(separator="\n\n")
                context += "\n\n---\n\n" + full_text[:20000 - len(context)]
                print(f"[TABLE CTX] Added full_text supplement, total={len(context)} chars", flush=True)
            return context[:25000]

        # 大文档（>300 chunks）：纯语义检索，加大检索量
        if precision == "coarse":
            full_text = self.kb.get_full_text(separator="\n\n")
            print(f"[TABLE CTX] Large doc coarse: full_text={len(full_text)} chars", flush=True)
            return full_text[:30000]

        context = self._search_context(headers, top_per_header=15, max_hits=50)
        print(f"[TABLE CTX] Large doc fine: search={len(context)} chars", flush=True)
        return context[:30000]

    def _search_context(self, headers: list[str], top_per_header: int = 10, max_hits: int = 30) -> str:
        seen: set[str] = set()
        hits: list[dict] = []
        per_k = max(top_per_header, 30 // max(len(headers), 1))
        for header in headers:
            for h in self.kb.search(header, top_k=per_k):
                if h["text"] not in seen:
                    seen.add(h["text"])
                    hits.append(h)
        hits.sort(key=lambda x: x.get("distance", 999))
        return "\n\n".join(h["text"] for h in hits[:max_hits])

    def _extract_data_adaptive(self, template_md: str, headers: list[str], context: str, requirements: str) -> list[dict[str, Any]]:
        batch_size = 6000
        print(f"[TABLE EXTRACT] context={len(context)} chars, batch_size={batch_size}, batches={max(1, (len(context)+batch_size-1)//batch_size)}", flush=True)
        if len(context) <= batch_size:
            return self._extract_data(template_md, headers, context, requirements)

        all_rows = []
        seen_keys: set[str] = set()
        batch_num = 0
        for i in range(0, len(context), batch_size):
            batch = context[i:i + batch_size]
            batch_num += 1
            if batch_num > 1:
                import time as _t
                _t.sleep(3)
            print(f"[TABLE EXTRACT] Batch {batch_num}: {len(batch)} chars", flush=True)
            try:
                rows = self._extract_data(template_md, headers, batch, requirements)
            except Exception as e:
                print(f"[TABLE EXTRACT] Batch {batch_num} error: {e}", flush=True)
                rows = []
            print(f"[TABLE EXTRACT] Batch {batch_num} returned {len(rows)} rows", flush=True)
            for row in rows:
                key = json.dumps(row, ensure_ascii=False, sort_keys=True)
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_rows.append(row)
            if batch_num >= 8:
                print(f"[TABLE EXTRACT] Reached max 8 batches, stopping", flush=True)
                break
        print(f"[TABLE EXTRACT] Total unique rows: {len(all_rows)}", flush=True)
        return all_rows

    def _infer_field_descriptions(self, headers: list[str]) -> str:
        """根据表头名称自动推断字段语义，生成约束说明"""
        type_keywords = [
            (["人名", "姓名", "名字", "作者", "负责人", "联系人", "教师", "学生"], "人物姓名（如'张三'、'叶文洁'），不可填事件或地点"),
            (["地名", "地点", "地址", "城市", "省份", "国家", "位置", "区域"], "地理位置名称（如'北京'、'上海'），不可填人名或事件"),
            (["时间", "日期", "年份", "年代", "时期"], "时间日期（如'1967年'、'3月15日'），必须含数字或时间词"),
            (["电话", "手机", "号码"], "电话号码"),
            (["金额", "价格", "费用", "成本", "收入"], "金额数值"),
            (["数量", "数目", "个数", "人数", "次数"], "数字"),
            (["编号", "序号", "代码"], "编号标识"),
            (["职位", "职务", "岗位", "职称", "身份"], "职务或身份"),
            (["单位", "公司", "机构", "组织", "部门", "学校"], "组织机构名称"),
            (["事件", "事迹", "经历", "经过"], "事件的简短描述"),
            (["原因", "理由", "动机"], "原因说明"),
            (["结果", "结论", "成果", "影响"], "结果说明"),
        ]
        lines = []
        for h in headers:
            matched_desc = None
            for keywords, desc in type_keywords:
                if any(kw in h for kw in keywords):
                    matched_desc = desc
                    break
            if matched_desc:
                lines.append(f"  - 「{h}」→ 必须是: {matched_desc}")
            else:
                lines.append(f"  - 「{h}」→ 按字面含义填写对应类型内容")
        return "\n".join(lines)

    def _validate_extracted_rows(self, rows: list[dict], headers: list[str]) -> list[dict]:
        """轻量级校验：过滤全空行，清除明显类型不匹配的字段值"""
        name_kw = ["人名", "姓名", "名字", "作者", "负责人", "联系人"]
        place_kw = ["地名", "地点", "城市", "省份", "国家"]
        time_kw = ["时间", "日期", "年份", "年代"]

        def _match(header, kws):
            return any(k in header for k in kws)

        validated = []
        for row in rows:
            cleaned = dict(row)
            for h in headers:
                val = str(cleaned.get(h, "")).strip()
                if not val:
                    continue
                # 人名字段：不应超过20字，不应含句子标点
                if _match(h, name_kw):
                    if len(val) > 20 or any(c in val for c in "，。！？；："):
                        cleaned[h] = ""
                # 地名字段：不应超过30字，不应含句末标点
                elif _match(h, place_kw):
                    if len(val) > 30 or any(c in val for c in "。！？"):
                        cleaned[h] = ""
                # 时间字段：必须含数字或时间汉字
                elif _match(h, time_kw):
                    if not re.search(r'[\d年月日时分秒世纪]', val):
                        cleaned[h] = ""
            # 跳过全空行
            if all(not str(cleaned.get(h, "")).strip() for h in headers):
                continue
            validated.append(cleaned)
        return validated

    def _extract_data(self, template_md: str, headers: list[str], context: str, requirements: str) -> list[dict[str, Any]]:
        if len(context) > 30000:
            context = context[:30000]
        if len(template_md) > 3000:
            template_md = template_md[:3000]

        import time
        t0 = time.time()
        print(f"[TABLE LLM] Calling LLM: context={len(context)} chars, headers={headers}", flush=True)

        custom_rules = f"\n用户额外需求: {requirements}" if requirements and requirements.strip() else ""
        field_descriptions = self._infer_field_descriptions(headers)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是严格的数据提取专家。从文本中精确提取与表格字段语义完全匹配的数据。\n\n"
                    "目标字段: {headers}\n\n"
                    "各字段语义约束（务必严格遵守）:\n{field_descriptions}\n"
                    "{custom_rules}\n\n"
                    "严格规则:\n"
                    "1. 返回JSON数组，每个元素是一行数据对象\n"
                    "2. key必须与字段名完全一致\n"
                    "3. 【核心】每个字段的值必须严格匹配该字段的语义类型！\n"
                    "   人名字段只能填人名，地名字段只能填地名，绝不可混淆\n"
                    "4. 宁缺毋滥：不确定的字段填空字符串，绝不可编造或填写不匹配的内容\n"
                    "5. 每个字段值简短精炼（不超过50字）\n"
                    "6. 最多提取20条最相关的记录\n"
                    "7. 只输出JSON数组，不要任何其他文字\n\n"
                    "反面示例（绝不可这样做）:\n"
                    "字段['地名','人名']时 错误: [{{\"地名\":\"发现了线索\",\"人名\":\"开始调查\"}}]\n"
                    "字段['地名','人名']时 正确: [{{\"地名\":\"北京\",\"人名\":\"张三\"}}]",
                ),
                ("human", "请严格按字段语义从以下文本提取数据，不匹配的留空：\n\n{context}"),
            ]
        )
        try:
            chain = prompt | self.llm
            for attempt in range(3):
                try:
                    response = chain.invoke(
                        {
                            "headers": json.dumps(headers, ensure_ascii=False),
                            "context": context or "",
                            "custom_rules": custom_rules,
                            "field_descriptions": field_descriptions,
                        }
                    )
                    break
                except Exception as retry_err:
                    if "429" in str(retry_err) or "rate" in str(retry_err).lower():
                        wait = (attempt + 1) * 5
                        print(f"[TABLE LLM] Rate limited, waiting {wait}s (attempt {attempt+1}/3)", flush=True)
                        time.sleep(wait)
                        if attempt == 2:
                            raise
                    else:
                        raise
        except Exception as e:
            elapsed = time.time() - t0
            print(f"[TABLE LLM] FAILED in {elapsed:.1f}s: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []
        elapsed = time.time() - t0
        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)
        print(f"[TABLE LLM] Response in {elapsed:.1f}s: {len(content)} chars, preview: {content[:200]}", flush=True)

        parsed = self._parse_json_array(content)
        if parsed is not None:
            parsed = self._validate_extracted_rows(parsed, headers)
            print(f"[TABLE LLM] Parsed OK after validation: {len(parsed)} rows", flush=True)
            return parsed

        print(f"[TABLE LLM] Parse failed, attempting repair...", flush=True)
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
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()
        # 直接解析
        try:
            result = json.loads(text)
            return result if isinstance(result, list) else None
        except json.JSONDecodeError:
            pass
        # 提取 [...] 部分
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(0))
                return result if isinstance(result, list) else None
            except json.JSONDecodeError:
                pass
        # 处理截断的 JSON — 找最后一个完整的 }, 截断并闭合
        if text.startswith("["):
            last_brace = text.rfind("}")
            if last_brace > 0:
                truncated = text[:last_brace + 1] + "]"
                try:
                    result = json.loads(truncated)
                    return result if isinstance(result, list) else None
                except json.JSONDecodeError:
                    pass
        return None
