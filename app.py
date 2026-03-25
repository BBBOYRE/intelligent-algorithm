from __future__ import annotations

import streamlit as st

from core.knowledge_base import KnowledgeBase
from utils.file_utils import ensure_runtime_dirs


def main() -> None:
    ensure_runtime_dirs()

    st.set_page_config(page_title="文档智能系统", page_icon="📄", layout="wide")
    st.title("📄 基于大语言模型的文档理解与多源数据融合系统")
    st.markdown("请在左侧页面导航中选择功能：文档上传、智能问答、模板表格填写。")

    with st.sidebar:
        st.header("📊 知识库状态")
        try:
            kb = KnowledgeBase()
            stats = kb.get_stats()
            st.metric("已入库分块", stats["total_chunks"])
        except Exception as exc:
            st.warning(f"知识库初始化失败: {exc}")

    st.info("建议流程：先上传文档入库，再进入智能问答或模板表格填写。")


if __name__ == "__main__":
    main()
