import re

with open('/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_card = """
        <!-- Newest Digest -->
        <div class="card newest">
            <a href="digests/2026-05-13-0930.html">
                <span class="tag latest">Latest</span>
                <h2>2026-05-13 09:30 Digest</h2>
                <p>US April CPI jumps to 3.8% amid Iran tensions, putting pressure on tech and pushing 30-year yields over 5%. Taiwan's market faces downward pressure with memory sector stocks like Phison and Nanya pulling back. PTT sentiment is marked by extreme FOMO over the record-breaking 00403A ETF volume (4.19M) and fears of an impending sell-off.</p>
                <div class="date">May 13, 2026 - 09:30 CST</div>
            </a>
        </div>
"""

# Remove "newest" class and "latest" tag from old cards
content = content.replace('class="card newest"', 'class="card"')
content = re.sub(r'\s*<span class="tag latest">Latest</span>', '', content)

# Insert new card
content = content.replace('<div class="history">', f'<div class="history">\n{new_card}')

with open('/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
