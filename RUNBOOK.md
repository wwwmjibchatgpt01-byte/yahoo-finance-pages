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

## Canonical Cron Entry Point
All scheduled and fallback cron jobs must use this shared wrapper. Do not reimplement these steps in the cron prompt.

```bash
cd /Users/mini1/.openclaw/workspace/yahoo-finance-pages
python3 finance_digest_wrapper.py --slot HHMM
```

Supported slots:
- `0510` for premarket
- `0930` for morning
- `1350` for midday
- `2130` for evening

The wrapper is the source of truth for:
1. Fallback/existing-file check. If `digests/YYYY-MM-DD-HHMM.html` already exists, it exits without rewriting it.
2. Fetching local PTT and return data before Yahoo/CNA enrichment.
3. Writing the digest to `digests/YYYY-MM-DD-HHMM.html`.
4. Rebuilding `index.html` as the index page only.
5. Committing and pushing changed digest/index files.
6. Sending Telegram notification when configured.

## Goal & Execution Steps
For each scheduled run or fallback run:
1. Read this `RUNBOOK.md`.
2. Execute the canonical wrapper command for the target slot.
3. Report the wrapper JSON output or the exact command error.

## Cron Guardrails
- Do all shell execution directly in the isolated cron session.
- Do not hand-write digest HTML from the cron prompt.
- Do not write the digest body into `index.html`; `index.html` is only the digest index.
- Do not bypass `finance_digest_wrapper.py` for normal scheduled or fallback digest generation.
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
