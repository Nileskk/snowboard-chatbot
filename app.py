import os
import subprocess
import sys
import shutil
import chromadb

# ----- 🔨 智能检查并自动构建向量数据库 -----
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "ski_knowledge"

def is_collection_ready():
    """检查向量数据库集合是否存在且可用"""
    if not os.path.exists(CHROMA_DB_PATH):
        return False
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        client.get_collection(COLLECTION_NAME)
        return True
    except Exception:
        return False

if not is_collection_ready():
    print("🔨 向量数据库集合缺失，正在重新构建...")
    # 删除旧的（可能已损坏的）数据库文件夹
    if os.path.exists(CHROMA_DB_PATH):
        shutil.rmtree(CHROMA_DB_PATH)
    # 运行构建脚本
    subprocess.run([sys.executable, "build_db.py"], check=True)
    print("✅ 数据库构建完成")
else:
    print("✅ 向量数据库集合已就绪，直接启动。")

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
