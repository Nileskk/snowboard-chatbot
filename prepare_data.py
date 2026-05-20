import os

transcripts_dir = "transcripts"
all_texts = []

for filename in sorted(os.listdir(transcripts_dir)):
    if filename.endswith(".txt"):
        filepath = os.path.join(transcripts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            content = " ".join(content.split())  # 清洗多余空白
            if content:
                all_texts.append(content)
                print(f"✅ 已读取: {filename}")

with open("all_transcripts.txt", "w", encoding="utf-8") as f:
    for text in all_texts:
        f.write(text + "\n\n=====END_OF_VIDEO=====\n\n")

print(f"✅ 共合并 {len(all_texts)} 个文稿，已保存为 all_transcripts.txt")

