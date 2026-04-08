import os
import glob
from datetime import datetime

digests_dir = '/Users/mini1/.openclaw/workspace/yahoo-finance-pages/digests'
index_path = '/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html'

files = glob.glob(os.path.join(digests_dir, '*.html'))
files = sorted([os.path.basename(f) for f in files], reverse=True)

html = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Finance Digest Index</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background: #f9f9f9; color: #333; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .card h2 { margin-top: 0; color: #2980b9; font-size: 1.2em; }
        .card a { text-decoration: none; color: inherit; display: block; }
        .card .date { font-size: 0.9em; color: #7f8c8d; margin-bottom: 0; }
        .highlight { border-left: 5px solid #e74c3c; }
    </style>
</head>
<body>
    <h1>Finance Digests</h1>
"""

for i, f in enumerate(files):
    name = f.replace('.html', '')
    try:
        dt = datetime.strptime(name, '%Y-%m-%d-%H%M')
        title = f"Digest: {dt.strftime('%Y-%m-%d %H:%M')}"
        date_str = dt.strftime('%b %d, %Y')
    except Exception:
        title = f"Digest: {name}"
        date_str = name
        
    highlight = " highlight" if i == 0 else ""
    title_prefix = "Latest " if i == 0 else ""
    
    html += f"""
    <div class="card{highlight}">
        <a href="digests/{f}">
            <h2>{title_prefix}{title}</h2>
            <p class="date">Published on {date_str}</p>
        </a>
    </div>
"""

html += """
</body>
</html>
"""

with open(index_path, 'w', encoding='utf-8') as file:
    file.write(html)
