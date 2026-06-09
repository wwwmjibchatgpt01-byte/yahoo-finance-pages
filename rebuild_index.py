import os
import re
from datetime import datetime

def rebuild():
    # Use paths relative to the script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    digest_dir = os.path.join(base_dir, "digests")
    index_path = os.path.join(base_dir, "index.html")
    
    if not os.path.exists(digest_dir):
        print(f"Error: {digest_dir} does not exist.")
        return

    # Get all html files and sort them by date (filename)
    files = [f for f in os.listdir(digest_dir) if f.endswith('.html')]
    # Use a key that handles optional 'digest_' prefix for correct chronological sorting
    files.sort(key=lambda x: x.replace('digest_', ''), reverse=True)

    if not files:
        print("No digest files found.")
        return

    # Find the latest one
    latest_file = files[0]
    latest_link = f"digests/{latest_file}"
    latest_title = latest_file.replace('.html', '')
    
    try:
        with open(os.path.join(digest_dir, latest_file), 'r', encoding='utf-8') as f:
            content = f.read()
            # Use regex to find H1 content, more robust than simple find
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL | re.IGNORECASE)
            if h1_match:
                title_html = h1_match.group(1).strip()
                # Strip internal HTML tags like <br>, <small> from the title
                latest_title = re.sub(r'<[^>]+>', ' ', title_html)
                latest_title = ' '.join(latest_title.split()) # Clean up whitespace
    except Exception as e:
        print(f"Could not read latest file for title: {e}")

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>📊 財經摘要索引 ({datetime.now().strftime('%Y/%m/%d')})</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f7f6; }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
        h2 {{ color: #e67e22; border-left: 5px solid #e67e22; padding-left: 10px; margin-top: 30px; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .post {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .post:last-child {{ border-bottom: none; }}
        .title {{ font-weight: bold; color: #2980b9; text-decoration: none; display: block; margin-bottom: 5px; }}
        .title:hover {{ text-decoration: underline; }}
        .meta {{ font-size: 0.85em; color: #7f8c8d; margin-bottom: 10px; }}
    </style>
</head>
<body>

<h1 id="index-title">📊 財經摘要索引 ({datetime.now().strftime('%Y/%m/%d')})</h1>

<div class="section">
    <h2 id="latest-digest">🆕 最新摘要</h2>
    <div class="post">
        <a href="{latest_link}" class="title">{latest_title}</a>
        <div class="meta">檔案: {latest_file} | 狀態: 已發佈</div>
    </div>
</div>

<div class="section">
    <h2 id="archive">📚 歷史摘要</h2>
"""

    # Add all other files to archive
    for f in files[1:]:
        html_content += f"""
    <div class="post">
        <a href="digests/{f}" class="title">{f.replace('.html', '')}</a>
        <div class="meta">檔案: {f}</div>
    </div>
"""

    html_content += """
</div>

</body>
</html>
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Successfully rebuilt {index_path}")

if __name__ == "__main__":
    rebuild()
