from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.knowledge_base import KnowledgeBase
from core.table_filler import TableFiller
from utils.file_utils import build_output_path, save_uploaded_file

st.header("📊 模板表格自动填写")
st.caption("上传 Word/Excel 模板后，系统将结合知识库自动回填字段。")

template_file = st.file_uploader("上传模板表格", type=["docx", "xlsx"])

if template_file and st.button("🚀 开始自动填写"):
    with st.spinner("正在分析模板并填写数据..."):
        try:
            template_path = save_uploaded_file(template_file)
            output_path = build_output_path(template_file.name)

            filler = TableFiller(KnowledgeBase())
            result = filler.fill_template(template_path, output_path)

            if result["status"] == "success":
                st.success(f"✅ 填写完成，共填入 {result['filled_cells']} 个单元格")
                out_path = Path(result["output_path"])
                with out_path.open("rb") as f:
                    st.download_button(
                        label="📥 下载填写后的文件",
                        data=f,
                        file_name=out_path.name,
                    )
            else:
                st.error(f"填写失败：{result}")
        except Exception as exc:
            st.error(f"执行失败：{exc}")
