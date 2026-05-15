import re

html_path = '/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old 'latest' tag
content = content.replace('<span class="tag latest">Latest</span>', '')
content = content.replace('class="card newest"', 'class="card"')

new_card = """
        <!-- Newest Digest -->
        <div class="card newest">
            <a href="digests/2026-05-15-1350.html">
                <span class="tag latest">Latest</span>
                <h2>2026-05-15 13:50 Digest</h2>
                <p>TAIEX hits record 42,408 pts early before giving up gains. Memory sector faces severe profit taking globally with major Asian memory stocks dropping over 8%. US markets hit record highs, and PTT retail sentiment shows extreme FOMO, blindly following Trump's "Stock Advisor" moves into Nvidia.</p>
                <div class="date">May 15, 2026 - 13:50 CST</div>
            </a>
        </div>
"""

# Insert new card after <div class="history">
content = re.sub(r'(<div class="history">)', r'\1\n' + new_card, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
