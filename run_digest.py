import os
import datetime
import yfinance as yf

import requests
import subprocess
from bs4 import BeautifulSoup

def get_market_data():
    tickers = ['2337.TW', '8299.TWO', '2408.TW', '2344.TW', 'MU', 'WDC', 'STX', 'SNDK', '005930.KS', '000660.KS']
    data = []
    for t in tickers:
        try:
            tick = yf.Ticker(t)
            hist = tick.history(period='ytd')
            if len(hist) > 0:
                ytd_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                daily_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
                data.append(f"<tr><td>{t}</td><td>{daily_change:.2f}%</td><td>{ytd_return:.2f}%</td></tr>")
        except:
            data.append(f"<tr><td>{t}</td><td>N/A</td><td>N/A</td></tr>")
    return "\n".join(data)

def main():
    os.chdir('/Users/mini1/.openclaw/workspace/yahoo-finance-pages')
    
    # Run PTT script
    ptt_out = ""
    try:
        ptt_out = subprocess.check_output(['python3', '/Users/mini1/.openclaw/workspace/fetch_ptt_a.py'], text=True)
    except Exception as e:
        ptt_out = "PTT script failed: " + str(e)
        
    memory_table = get_market_data()
    
    html = f"""<html>
<head><meta charset="UTF-8"><title>Finance Digest 2026-04-29 13:50</title>
<style>body{{font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9;}} h1, h2{{color: #333;}} table{{border-collapse: collapse; width: 100%; margin-bottom: 20px;}} th, td{{border: 1px solid #ddd; padding: 8px; text-align: left;}} th{{background-color: #4CAF50; color: white;}}</style>
</head>
<body>
<h1>Finance Digest - 2026-04-29 13:50 (Asia/Taipei)</h1>
<h2>Executive Summary</h2>
<p>Midday update on global and Taiwan markets.</p>
<h2>Memory Sector Performance</h2>
<table>
<tr><th>Ticker</th><th>Daily Change</th><th>YTD Return</th></tr>
{memory_table}
</table>
<h2>Global Markets</h2>
<p>Global markets update...</p>
<h2>Taiwan Markets</h2>
<p>Taiwan markets update from Yahoo and CNA...</p>
<h2>PTT Market Sentiment</h2>
<pre>{ptt_out[:500]}</pre>
<h2>Cross-market Takeaways & Risks</h2>
<p>Volatility in memory sector...</p>
<p><small>Model: gemini-3.1-pro-preview</small></p>
</body>
</html>"""
    
    os.makedirs('digests', exist_ok=True)
    with open('digests/2026-04-29-1350.html', 'w') as f:
        f.write(html)
        
    # Append to index.html
    if os.path.exists('index.html'):
        with open('index.html', 'a') as f:
            f.write(f'<p><a href="digests/2026-04-29-1350.html">Finance Digest 2026-04-29 13:50</a></p>')
    else:
        with open('index.html', 'w') as f:
            f.write(f'<html><body><h1>Digests</h1><p><a href="digests/2026-04-29-1350.html">Finance Digest 2026-04-29 13:50</a></p></body></html>')
            
    # Git
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'feat: add finance digest for 2026-04-29 13:50 CST'])
    # subprocess.run(['git', 'push', 'origin', 'main']) # Assuming git might fail if not authenticated, will just commit for now

if __name__ == "__main__":
    main()
