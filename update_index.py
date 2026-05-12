import re

file_path = '/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace('<div class="card newest">', '<div class="card">')
content = content.replace('<span class="tag latest">Latest</span>\n                ', '')

new_digest = """
        <!-- Newest Digest -->
        <div class="card newest">
            <a href="digests/2026-05-12-0930.html">
                <span class="tag latest">Latest</span>
                <h2>2026-05-12 09:30 Digest</h2>
                <p>US stock futures edge up awaiting CPI while Middle East tensions persist. TAIEX opens up 90 pts to 41,880. Memory sector remains strong with MU and WDC soaring over 6%. PTT sentiment reveals intense TSMC debate amid Apple/Intel rumors and extreme retail FOMO driven by surging margin balances.</p>
                <div class="date">May 12, 2026 - 09:30 CST</div>
            </a>
        </div>
"""

content = content.replace('<div class="history">', '<div class="history">\n' + new_digest)

with open(file_path, 'w') as f:
    f.write(content)
