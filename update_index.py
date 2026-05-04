import re

with open('/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the 'newest' class and 'Latest' tag from the old latest digest
content = content.replace('class="card newest"', 'class="card"')
content = content.replace('<span class="tag latest">Latest</span>\n                ', '')

# Prepare the new card HTML
new_card = """        <!-- Newest Digest -->
        <div class="card newest">
            <a href="digests/2026-05-04-1350.html">
                <span class="tag latest">Latest</span>
                <h2>2026-05-04 13:50 Digest</h2>
                <p>TAIEX breaks 40,700 (+1,700 pts) as TSMC and MediaTek skyrocket. SanDisk earnings fuel a global memory rally, while retail FOMO and high leverage dominate PTT sentiment.</p>
                <div class="date">May 4, 2026 - 13:50 CST</div>
            </a>
        </div>

"""

# Insert the new card after '<div class="history">\n'
content = content.replace('<div class="history">\n', '<div class="history">\n' + new_card)

with open('/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
