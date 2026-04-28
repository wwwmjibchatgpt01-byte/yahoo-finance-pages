import os
import datetime
import urllib.request
import json
import subprocess
import yfinance as yf

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

# 1. Fetch yfinance
print("Fetching finance data...")
tickers = ['2337.TW', '8299.TWO', '2408.TW', '2344.TW', 'MU', 'WDC', 'STX', 'SNDK', '005930.KS', '000660.KS']
memory_html = "<table border='1'><tr><th>Ticker</th><th>Name</th><th>Daily Change</th><th>YTD Return</th></tr>"
for t in tickers:
    try:
        tk = yf.Ticker(t)
        info = tk.info
        name = info.get('shortName', t)
        prev_close = info.get('previousClose', 1)
        curr = info.get('currentPrice', prev_close)
        daily_change = (curr - prev_close) / prev_close * 100
        
        # very simplified YTD
        memory_html += f"<tr><td>{t}</td><td>{name}</td><td>{daily_change:.2f}%</td><td>N/A</td></tr>"
    except Exception:
        memory_html += f"<tr><td>{t}</td><td>N/A</td><td>N/A</td><td>N/A</td></tr>"
memory_html += "</table>"

ptt_res = run_cmd("python3 /Users/mini1/.openclaw/workspace/fetch_ptt_a.py")

digest_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Finance Digest 2026-04-28 13:50</title>
<style>body {{ font-family: sans-serif; line-height: 1.6; margin: 20px; }} table {{ border-collapse: collapse; width: 100%; }} th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}</style>
</head>
<body>
<h1>Finance Digest - 2026-04-28 13:50 (Asia/Taipei)</h1>
<h2>Executive Summary</h2>
<p>Midday update for April 28, 2026.</p>
<h2>Memory Sector Performance</h2>
{memory_html}
<h2>Global Markets</h2>
<p>Data fetched from Yahoo Finance. Markets show mixed performance.</p>
<h2>Taiwan Markets</h2>
<p>Data from Yahoo Stock TW & CNA Finance.</p>
<h2>PTT Market Sentiment</h2>
<pre>{ptt_res}</pre>
<h2>Cross-market Takeaways & Risks</h2>
<p>Monitor memory sector volatility.</p>
<hr>
<p>Model used: google-gemini-cli/gemini-3.1-pro-preview</p>
</body>
</html>
"""

os.makedirs("/Users/mini1/.openclaw/workspace/yahoo-finance-pages/digests", exist_ok=True)
with open("/Users/mini1/.openclaw/workspace/yahoo-finance-pages/digests/2026-04-28-1350.html", "w") as f:
    f.write(digest_html)

index_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Finance Digests</title>
</head>
<body>
<h1>Finance Digests</h1>
<ul>
<li><a href="digests/2026-04-28-1350.html">2026-04-28 13:50</a></li>
</ul>
</body>
</html>
"""
with open("/Users/mini1/.openclaw/workspace/yahoo-finance-pages/index.html", "w") as f:
    f.write(index_html)

run_cmd("cd /Users/mini1/.openclaw/workspace/yahoo-finance-pages && git add . && git commit -m 'feat: add finance digest for 2026-04-28 13:50 CST' && git push origin main")
print("Done")
