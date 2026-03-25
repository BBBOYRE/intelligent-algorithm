from __future__ import annotations

import streamlit as st

from core.agent import DocumentAgent
from core.knowledge_base import KnowledgeBase

st.header("💬 智能问答")
st.caption("回答基于已入库文档；如果信息不足，请先回到文档上传页面补充资料。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("请输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                agent = DocumentAgent(KnowledgeBase())
                answer = agent.chat(prompt)
            except Exception as exc:
                answer = f"调用失败：{exc}"
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
