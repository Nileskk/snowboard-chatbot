import os
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb

# ----- 智能加载 .env -----
# 强制从 rag_core.py 所在目录加载 .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# ----- 初始化组件 -----
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

embedder = SentenceTransformer('shibing624/text2vec-base-chinese')  # 和 build_db.py 保持一致

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("ski_knowledge")

# ----- 检索函数 -----
def retrieve_context(query, top_k=3):
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results['documents'][0]

# ----- 生成回答 -----
def ask_deepseek(question, context_chunks):
    context_text = "\n\n---\n\n".join(context_chunks)
    
    system_prompt = """你是一位世界级的滑雪专家，精通各种滑雪技巧、装备选择、安全知识以及雪场攻略。
请严格按照提供的【参考知识】来回答问题。如果参考知识不足以回答，请如实说明。
语气要专业、热情，便于滑雪爱好者理解。"""

    user_message = f"""【参考知识】：
{context_text}

【用户问题】：
{question}

请回答："""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content

# ----- 整合流水线 -----
def qa_pipeline(question):
    chunks = retrieve_context(question)
    answer = ask_deepseek(question, chunks)
    return answer
