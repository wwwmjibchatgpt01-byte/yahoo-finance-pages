# Finance Digest Runbook (Master Config)

Repository path: `/Users/mini1/.openclaw/workspace/yahoo-finance-pages`

## Data Sources (Must fetch all)
1. **Yahoo Finance** (US): `https://finance.yahoo.com/`
2. **Yahoo Stock** (TW): `https://tw.stock.yahoo.com/`
3. **CNA Finance** (TW): `https://feeds.feedburner.com/rsscna/finance` (RSS Feed)
4. **PTT Stock Hot Posts & Sentiment (Method A)**: 
   Run the local Python script `python3 /Users/mini1/.openclaw/workspace/fetch_ptt_a.py` to get the latest hot posts and sentiment from the PTT Stock board.
5. **Memory Stock Sector Performance**: 
   Run the local Python script `python3 /Users/mini1/.openclaw/workspace/skills/today-returns/scripts/fetch_memory_report.py` to fetch daily change and YTD (Year-to-Date) returns for the following watchlist:
   - **TW**: 2337.TW (旺宏), 8299.TWO (群聯), 2408.TW (南亞科), 2344.TW (華邦電)
   - **US**: MU (Micron), WDC (Western Digital), STX (Seagate), SNDK (SanDisk)
   - **KR**: 005930.KS (Samsung), 000660.KS (SK Hynix)

## Goal & Execution Steps
For each scheduled run (or fallback run):
1. **Fallback Check**: If this is a fallback job, FIRST check if the digest for the target time slot (05:10, 09:00, 13:50, or 21:30) is already published in `digests/`. If it is, exit immediately.
2. **Fetch Data**:
   - Use `exec` to run the local scripts first:
     - `python3 /Users/mini1/.openclaw/workspace/fetch_ptt_a.py`
     - `python3 /Users/mini1/.openclaw/workspace/skills/today-returns/scripts/fetch_memory_report.py`
   - For Yahoo/CNA, prefer lightweight fetch methods that do not open an interactive browser.
   - In cron runs, **do not open the browser by default**. Use browser only as a last resort if a required page cannot be fetched any other way.
   - Do not use `stock-returns-calculator` in cron. The local Python script is the source of truth for return calculations.
3. **Write HTML Digest**: Produce a complete HTML digest in Traditional Chinese under `digests/YYYY-MM-DD-HHMM.html` (Asia/Taipei time). 
   - **New Requirement**: Include a dedicated section for "Memory Sector Performance" containing the table of daily changes and YTD returns for the watchlist above.
   - **Layout Requirements**: The design must be stylish, clean, and modern, ensuring high readability for the user. Content must remain comprehensive; do not omit important details for the sake of brevity.
4. **Update Index**: Update `index.html` to highlight the newest digest as a card near the top, and append it to the history list. Ensure the index also follows the stylish and clean layout standards.
5. **Git Operations**: Commit (`feat: add finance digest for YYYY-MM-DD HH:MM CST`) and push all changed files to `main`.
6. **Reporting**: Return the GitHub Pages index URL (`https://wwwmjibchatgpt01-byte.github.io/yahoo-finance-pages/`) and the specific digest URL to the user.

## Cron Guardrails
- Do all shell execution, HTML writing, index updates, `git commit`, and `git push` directly in the isolated cron session.
- Do not delegate these steps to subagents.
- If a tool is actually unavailable, report the exact tool name and exact command that failed.
- Do not claim the environment "cannot write files" or "git failed" unless a real write or git command has actually failed.

## Digest Structure (HTML)
- Title with timestamp
- **Executive Summary** (Short)
- **Memory Sector Performance** (Table with Ticker, Name, Daily Change, YTD Return)
- **Global Markets** (Yahoo Finance + Global Memory News summary)
- **Taiwan Markets** (Yahoo Stock & CNA Finance + TW Memory News summary)
- **PTT Market Sentiment (Method A)** (List top hot posts, summarize retail investor sentiment, FOMO/panic indicators)
- **Cross-market Takeaways & Risks**
- **Source Links**
- At the bottom of the HTML, record which model was used to generate it.
