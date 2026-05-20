import os
import subprocess
import sys

# ----- 🔨 如果云端没有向量数据库，自动构建 -----
if not os.path.exists("chroma_db"):
    print("🔨 云端未检测到向量数据库，正在自动构建...")
    subprocess.run([sys.executable, "build_db.py"], check=True)
    print("✅ 数据库构建完成")

# ----- 现在可以安全导入 RAG 核心 -----
import streamlit as st
from rag_core import qa_pipeline

st.set_page_config(page_title="滑雪助手KK", page_icon="🏂️")
st.title("🏂️ KK的滑雪知识智能问答")
st.caption("基于KK的所有视频文稿训练而成，有什么问题尽管问！")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("例如：我在单板推坡的时候总是卡刃怎么办？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("正在检索滑雪知识..."):
            answer = qa_pipeline(prompt)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
