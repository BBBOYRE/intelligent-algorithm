from __future__ import annotations

import streamlit as st

from core.document_parser import DocumentParser
from core.knowledge_base import KnowledgeBase
from utils.file_utils import save_uploaded_file

st.header("📄 文档上传与解析")
st.caption("请先上传原始文档并完成入库，再进行问答或模板填写。")

uploaded_files = st.file_uploader(
    "上传文档（支持 docx/xlsx/md/txt）",
    type=["docx", "xlsx", "md", "txt"],
    accept_multiple_files=True,
)

if uploaded_files and st.button("🚀 开始解析并入库"):
    parser = DocumentParser()
    kb = KnowledgeBase()

    progress = st.progress(0)
    success_count = 0
    for idx, uploaded in enumerate(uploaded_files):
        with st.spinner(f"正在处理：{uploaded.name}"):
            try:
                file_path = save_uploaded_file(uploaded)
                parsed = parser.parse(file_path)
                kb.add_document(parsed)
                success_count += 1
            except Exception as exc:
                st.error(f"处理失败 {uploaded.name}：{exc}")
        progress.progress((idx + 1) / len(uploaded_files))

    st.success(f"✅ 成功解析并入库 {success_count} / {len(uploaded_files)} 个文档")

if st.button("刷新知识库统计"):
    kb = KnowledgeBase()
    stats = kb.get_stats()
    st.info(f"当前知识库分块数：{stats['total_chunks']}")
