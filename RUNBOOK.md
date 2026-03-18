# Finance Digest Runbook (Master Config)

Repository path: `/Users/mini1/.openclaw/workspace/yahoo-finance-pages`

## Data Sources (Must fetch all)
1. **Yahoo Finance** (US): `https://finance.yahoo.com/`
2. **Yahoo Stock** (TW): `https://tw.stock.yahoo.com/`
3. **CNA Finance** (TW): `https://www.cna.com.tw/list/asc.aspx`
4. **PTT Stock Hot Posts & Sentiment (Method A)**: 
   Run the local Python script `python3 /Users/mini1/.openclaw/workspace/fetch_ptt_a.py` to get the latest hot posts and sentiment from the PTT Stock board.

## Goal & Execution Steps
For each scheduled run (or fallback run):
1. **Fallback Check**: If this is a fallback job, FIRST check if the digest for the target time slot (05:10, 09:00, 13:50, or 21:30) is already published in `digests/`. If it is, exit immediately.
2. **Fetch Data**: Use `web_fetch` (or browser) for Yahoo/CNA and `exec` for the PTT Python script.
3. **Write HTML Digest**: Produce a complete HTML digest in Traditional Chinese under `digests/YYYY-MM-DD-HHMM.html` (Asia/Taipei time).
4. **Update Index**: Update `index.html` to highlight the newest digest as a card near the top, and append it to the history list.
5. **Git Operations**: Commit (`feat: add finance digest for YYYY-MM-DD HH:MM CST`) and push all changed files to `main`.
6. **Reporting**: Return the GitHub Pages index URL (`https://wwwmjibchatgpt01-byte.github.io/yahoo-finance-pages/`) and the specific digest URL to the user.

## Digest Structure (HTML)
- Title with timestamp
- **Executive Summary** (Short)
- **Global Markets** (Yahoo Finance)
- **Taiwan Markets** (Yahoo Stock & CNA Finance)
- **PTT Market Sentiment (Method A)** (List top hot posts, summarize retail investor sentiment, FOMO/panic indicators)
- **Cross-market Takeaways & Risks**
- **Source Links**