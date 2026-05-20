import re
import chromadb
from sentence_transformers import SentenceTransformer

# ----------------- 自定义文本分块函数 -----------------
def split_text_recursive(text, chunk_size=400, chunk_overlap=50, separators=None):
    """
    根据分隔符列表递归分割文本，保持 chunk 大小在 chunk_size 左右。
    """
    if separators is None:
        separators = ["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", " ", ""]
    
    # 递归分割
    def _split(text, seps):
        final_chunks = []
        # 选择当前层级的分隔符
        sep = seps[0] if seps else " "
        # 如果分隔符为空，则按字符切分
        if not sep:
            # 已经没有分隔符可用，强行按长度切分
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunk = text[i:i + chunk_size]
                if chunk:
                    final_chunks.append(chunk)
            return final_chunks
        
        splits = text.split(sep)
        # 如果分割后只有一个元素，降级使用下一个分隔符
        if len(splits) == 1:
            return _split(text, seps[1:])
        
        good_chunks = []
        for piece in splits:
            # 如果当前片段长度在可接受范围内，直接保留
            if len(piece) <= chunk_size:
                good_chunks.append(piece)
            else:
                # 片段太长，用下一层分隔符继续分割
                good_chunks.extend(_split(piece, seps[1:]))
        
        # 合并较短的片段，使 chunk 大小接近 chunk_size
        merged = []
        current = ""
        for chunk in good_chunks:
            if len(current) + len(chunk) <= chunk_size + chunk_overlap:
                current = (current + " " + chunk).strip() if current else chunk
            else:
                if current:
                    merged.append(current)
                current = chunk
        if current:
            merged.append(current)
        return merged
    
    chunks = _split(text, separators)
    return chunks

# ----------------- 主流程 -----------------
# 1. 读取合并后的文稿
with open("all_transcripts.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# 2. 分块（使用我们的自定义函数）
chunks = split_text_recursive(
    raw_text,
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", " ", ""]
)
print(f"🔹 共切分为 {len(chunks)} 个文本块")

# 3. 加载本地 Embedding 模型（中文文稿用这个）
embedder = SentenceTransformer('shibing624/text2vec-base-chinese')

# 4. 初始化 ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("ski_knowledge")

# 5. 批量生成向量并存入
batch_size = 32
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    embeddings = embedder.encode(batch).tolist()
    ids = [f"chunk_{j}" for j in range(i, i+len(batch))]
    collection.add(
        documents=batch,
        embeddings=embeddings,
        ids=ids
    )
    print(f"✅ 已存入 {min(i+batch_size, len(chunks))}/{len(chunks)}")

print("🎉 向量数据库构建完成！")
