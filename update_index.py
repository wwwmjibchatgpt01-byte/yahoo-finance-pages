import re

with open('index.html', 'r') as f:
    content = f.read()

new_card = """
        <div class="digest-card">
            <h2><a href="digests/2026-04-10-0930.html">Finance Digest - 2026-04-10 09:30 CST</a></h2>
            <p><strong>Executive Summary:</strong> 全球市場焦點仍集中在中東停火協議的發展上。台股方面，市場聚焦台積電3月營收及即將到來的法說會。記憶體板塊在 AI 需求與寡占效應下，前景看好，DRAM 預計缺貨至2027年。PTT 散戶情緒因中東局勢劇烈波動。</p>
            <span class="date">2026-04-10</span>
        </div>
"""

# Insert new card after the <div class="digests-container"> tag
updated_content = re.sub(r'(<div class="digests-container">)', r'\1' + new_card, content)

with open('index.html', 'w') as f:
    f.write(updated_content)
