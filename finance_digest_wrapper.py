#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

ROOT = Path("/Users/mini1/.openclaw/workspace/yahoo-finance-pages")
WORKSPACE = Path("/Users/mini1/.openclaw/workspace")
OPENCLAW_CONFIG = Path("/Users/mini1/.openclaw/openclaw.json")
DIGESTS_DIR = ROOT / "digests"
INDEX_REBUILD = ROOT / "rebuild_index.py"
PTT_A = WORKSPACE / "fetch_ptt_a.py"
PTT_DIGEST = WORKSPACE / "ptt_stock_digest.py"
PTT_VENV_PYTHON = WORKSPACE / "ptt_venv/bin/python3"
MEMORY_REPORT = WORKSPACE / "skills/today-returns/scripts/fetch_memory_report.py"
TZ = ZoneInfo("Asia/Taipei")
PUBLIC_BASE_URL = "https://wwwmjibchatgpt01-byte.github.io/yahoo-finance-pages"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)

SLOT_MAP = {
    "0510": "0510",
    "0530": "0510",
    "0900": "0900",
    "0930": "0930",
    "0940": "0930",
    "1350": "1350",
    "1410": "1350",
    "2130": "2130",
    "2150": "2130",
}


@dataclass
class SectionBundle:
    executive_summary: list[str]
    global_markets: list[str]
    taiwan_markets: list[str]
    ptt_sentiment: list[str]
    takeaways: list[str]
    headline: str


def log(message: str) -> None:
    print(f"[finance-wrapper] {message}", file=sys.stderr, flush=True)


def digest_public_url(digest_name: str) -> str:
    return f"{PUBLIC_BASE_URL}/digests/{digest_name}"


def run_command(
    command: list[str],
    cwd: Path | None = None,
    check: bool = True,
    timeout: int | None = 120,
) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
        )
    return completed.stdout.strip()


def fetch_url(url: str) -> str:
    try:
        return run_command(
            [
                "curl",
                "-fsSL",
                "--compressed",
                "-A",
                USER_AGENT,
                url,
            ],
            timeout=30,
        )
    except Exception:  # noqa: BLE001
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        response.raise_for_status()
        response.encoding = response.encoding or "utf-8"
        return response.text


def extract_headlines_from_html(html: str, limit: int = 8) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    headlines: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "a", "span"]):
        text = " ".join(tag.get_text(" ", strip=True).split())
        if len(text) < 12 or len(text) > 140:
            continue
        if text in seen:
            continue
        seen.add(text)
        headlines.append(text)
        if len(headlines) >= limit:
            break
    return headlines


def fetch_cna_items(limit: int = 8) -> list[str]:
    xml_text = fetch_url("https://feeds.feedburner.com/rsscna/finance")
    root = ET.fromstring(xml_text)
    items: list[str] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        if title:
            items.append(title)
        if len(items) >= limit:
            break
    return items


def normalize_slot(raw_slot: str | None, now: datetime) -> str:
    if raw_slot:
        slot = raw_slot.strip()
        if slot not in SLOT_MAP:
            raise ValueError(f"Unsupported slot: {slot}")
        return SLOT_MAP[slot]
    current = now.strftime("%H%M")
    if current not in SLOT_MAP:
        raise ValueError(f"Current time {current} does not map to a finance digest slot")
    return SLOT_MAP[current]


def run_optional(command: list[str], *, timeout: int = 45) -> str:
    try:
        return run_command(command, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return f"[FAILED] {' '.join(command)}\n{exc}"


def collect_local_data() -> dict[str, str]:
    log("collecting local script outputs")
    return {
        "ptt_digest": run_optional([str(PTT_VENV_PYTHON), str(PTT_DIGEST)], timeout=60),
        "ptt_hot": run_optional(["python3", str(PTT_A)], timeout=25),
        "memory_report": run_optional(["python3", str(MEMORY_REPORT)], timeout=60),
    }


def collect_news_data() -> dict[str, list[str]]:
    log("fetching Yahoo/CNA headlines")
    try:
        us_headlines = extract_headlines_from_html(fetch_url("https://finance.yahoo.com/"))
    except Exception as exc:  # noqa: BLE001
        log(f"Yahoo US fetch failed: {exc}")
        us_headlines = ["Yahoo Finance 抓取失敗，本次改以本地腳本資料為主。"]
    try:
        tw_headlines = extract_headlines_from_html(fetch_url("https://tw.stock.yahoo.com/"))
    except Exception as exc:  # noqa: BLE001
        log(f"Yahoo TW fetch failed: {exc}")
        tw_headlines = ["Yahoo 股市抓取失敗，本次改以本地腳本資料為主。"]
    try:
        cna_headlines = fetch_cna_items()
    except Exception as exc:  # noqa: BLE001
        log(f"CNA fetch failed: {exc}")
        cna_headlines = ["CNA Finance RSS 抓取失敗，本次改以本地腳本資料為主。"]
    return {
        "yahoo_us": us_headlines,
        "yahoo_tw": tw_headlines,
        "cna": cna_headlines,
    }


def load_telegram_bot_token() -> str | None:
    env_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if env_token:
        return env_token
    try:
        data = json.loads(OPENCLAW_CONFIG.read_text())
    except Exception:  # noqa: BLE001
        return None
    token = (((data.get("channels") or {}).get("telegram") or {}).get("botToken") or "").strip()
    return token or None


def load_telegram_chat_id() -> str | None:
    env_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if env_chat_id:
        return env_chat_id
    return None


def send_telegram_message(text: str) -> None:
    bot_token = load_telegram_bot_token()
    chat_id = load_telegram_chat_id()
    if not bot_token or not chat_id:
        log("telegram notification skipped: missing bot token or chat id")
        return
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=20,
    )
    response.raise_for_status()


def build_model_prompt(*, date_str: str, slot: str, local_data: dict[str, str], news_data: dict[str, list[str]]) -> str:
    return textwrap.dedent(
        f"""
        你是財經摘要編輯。請只根據下面提供的資料，產出嚴格 JSON，不能輸出 markdown code fence，不能輸出額外說明。

        目標時段：{date_str} {slot}（Asia/Taipei）

        JSON schema:
        {{
          "headline": "一行中文標題",
          "executive_summary": ["重點1", "重點2", "重點3"],
          "global_markets": ["重點1", "重點2", "重點3"],
          "taiwan_markets": ["重點1", "重點2", "重點3"],
          "ptt_sentiment": ["重點1", "重點2", "重點3"],
          "takeaways": ["重點1", "重點2", "重點3"]
        }}

        規則:
        - 使用繁體中文。
        - 內容要像真人整理重點，不要使用「不是A，而是B」這類模板句。
        - 不要編造數字；報酬率與漲跌只能引用記憶體報酬腳本內容。
        - 若資料不足，就直接說資料有限，不要幻想。
        - `ptt_sentiment` 必須以本地 PTT 腳本輸出為主。

        [LOCAL_MEMORY_REPORT]
        {local_data["memory_report"]}

        [LOCAL_PTT_HOT]
        {local_data["ptt_hot"]}

        [LOCAL_PTT_DIGEST]
        {local_data["ptt_digest"]}

        [YAHOO_US_HEADLINES]
        {"; ".join(news_data["yahoo_us"])}

        [YAHOO_TW_HEADLINES]
        {"; ".join(news_data["yahoo_tw"])}

        [CNA_FINANCE_HEADLINES]
        {"; ".join(news_data["cna"])}
        """
    ).strip()


def extract_json_object(text: str) -> dict[str, Any]:
    starts = [idx for idx, ch in enumerate(text) if ch == "{"]
    for start in reversed(starts):
        candidate = text[start:].strip()
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("No JSON object found in model output")


def load_model_candidates() -> list[tuple[str, str, str]]:
    data = json.loads(OPENCLAW_CONFIG.read_text())
    defaults_model = (((data.get("agents") or {}).get("defaults") or {}).get("model") or {})
    providers = ((data.get("models") or {}).get("providers") or {})

    model_refs: list[str] = []
    if isinstance(defaults_model, str):
        model_refs.append(defaults_model)
    elif isinstance(defaults_model, dict):
        primary = str(defaults_model.get("primary") or "").strip()
        if primary:
            model_refs.append(primary)
        for fallback in defaults_model.get("fallbacks") or []:
            fallback_ref = str(fallback or "").strip()
            if fallback_ref:
                model_refs.append(fallback_ref)

    if not model_refs:
        model_refs = ["lmstudio/google/gemma-4-26b-a4b"]

    candidates: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for model_ref in model_refs:
        if "/" not in model_ref or model_ref in seen:
            continue
        seen.add(model_ref)
        provider_id, model_id = model_ref.split("/", 1)
        provider = providers.get(provider_id) or {}
        base_url = str(provider.get("baseUrl") or "").rstrip("/")
        api = str(provider.get("api") or "openai-completions").strip()
        if not base_url:
            log(f"skipping model without baseUrl: {model_ref}")
            continue
        if api != "openai-completions":
            log(f"skipping non-openai-completions provider for wrapper: {model_ref} ({api})")
            continue
        candidates.append((model_ref, base_url, model_id))

    if not candidates:
        raise RuntimeError("No usable openai-completions model candidates found in openclaw.json")

    return candidates


def call_primary_model(prompt: str) -> tuple[SectionBundle, str]:
    errors: list[str] = []
    for model_ref, base_url, model_id in load_model_candidates():
        log(f"calling model {model_ref}")
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                json={
                    "model": model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是財經摘要編輯。只輸出符合使用者 schema 的 JSON，不要輸出 markdown code fence。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2500,
                },
                timeout=240,
            )
            response.raise_for_status()
            payload = response.json()
            response_text = (
                (((payload.get("choices") or [{}])[0]).get("message") or {}).get("content")
                or ((payload.get("choices") or [{}])[0]).get("text")
                or ""
            )
            response_payload = extract_json_object(response_text)
            log(f"model returned structured response: {model_ref}")

            def as_list(key: str) -> list[str]:
                value = response_payload.get(key, [])
                if isinstance(value, list):
                    return [str(item).strip() for item in value if str(item).strip()]
                if isinstance(value, str) and value.strip():
                    return [value.strip()]
                return []

            headline = str(response_payload.get("headline", "")).strip() or "財經摘要"
            return (
                SectionBundle(
                    executive_summary=as_list("executive_summary"),
                    global_markets=as_list("global_markets"),
                    taiwan_markets=as_list("taiwan_markets"),
                    ptt_sentiment=as_list("ptt_sentiment"),
                    takeaways=as_list("takeaways"),
                    headline=headline,
                ),
                model_ref,
            )
        except Exception as exc:  # noqa: BLE001
            error = f"{model_ref}: {exc}"
            errors.append(error)
            log(f"model failed, trying next fallback: {error}")

    raise RuntimeError("All configured finance digest models failed: " + " | ".join(errors))


def parse_memory_rows(memory_report: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current_group = ""
    pattern = re.compile(r"^- (?P<name>[^：]+)：(?P<daily>[+-]?\d+\.\d+%) \((?P<change>[+-]?\d+\.\d+)\)，(?P<price>\d+\.\d+) 元，YTD (?P<ytd>[+-]?\d+\.\d+%)$")
    for raw_line in memory_report.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith("：") and not line.startswith("- "):
            current_group = line[:-1]
            continue
        match = pattern.match(line)
        if not match:
            continue
        rows.append(
            {
                "group": current_group,
                "name": match.group("name"),
                "daily": match.group("daily"),
                "change": match.group("change"),
                "price": match.group("price"),
                "ytd": match.group("ytd"),
            }
        )
    return rows


def render_list(items: list[str]) -> str:
    if not items:
        return "<li>資料不足</li>"
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def render_memory_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "<p>記憶體報酬資料不足。</p>"
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{escape(row['group'])}</td>"
            f"<td>{escape(row['name'])}</td>"
            f"<td>{escape(row['daily'])}</td>"
            f"<td>{escape(row['change'])}</td>"
            f"<td>{escape(row['price'])}</td>"
            f"<td>{escape(row['ytd'])}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>族群</th><th>標的</th><th>日漲跌</th><th>漲跌價差</th><th>收盤價</th><th>YTD</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def build_digest_html(*, date_str: str, slot: str, sections: SectionBundle, memory_rows: list[dict[str, str]], model_label: str) -> str:
    title = f"{date_str} {slot} 財經摘要"
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f4f0ea;
      --paper: #fffdf9;
      --ink: #1f1f1f;
      --muted: #6b625b;
      --line: #e3d8ca;
      --accent: #b5542f;
      --accent-soft: #f2e1d6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Noto Serif TC", serif;
      background: radial-gradient(circle at top, #fff7ef 0%, var(--bg) 55%);
      color: var(--ink);
    }}
    .wrap {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 48px 20px 80px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(181,84,47,0.12), rgba(255,255,255,0.9));
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 28px;
      box-shadow: 0 18px 60px rgba(80, 55, 30, 0.08);
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 13px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      margin: 0 0 12px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(30px, 4vw, 52px);
      line-height: 1.02;
    }}
    .headline {{
      margin-top: 14px;
      font-size: 20px;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.25fr 1fr;
      gap: 18px;
      margin-top: 22px;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 10px 30px rgba(65, 45, 26, 0.05);
    }}
    .card h2 {{
      margin: 0 0 14px;
      font-size: 22px;
    }}
    .full {{
      margin-top: 18px;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
      line-height: 1.75;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 15px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 13px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .sources {{
      margin-top: 18px;
      font-size: 14px;
      color: var(--muted);
    }}
    .sources a {{
      color: var(--accent);
    }}
    footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 860px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <p class="eyebrow">Finance Digest</p>
      <h1>{escape(title)}</h1>
      <div class="headline">{escape(sections.headline)}</div>
    </section>

    <div class="grid">
      <section class="card">
        <h2>執行摘要</h2>
        <ul>{render_list(sections.executive_summary)}</ul>
      </section>
      <section class="card">
        <h2>跨市場重點與風險</h2>
        <ul>{render_list(sections.takeaways)}</ul>
      </section>
    </div>

    <section class="card full">
      <h2>記憶體族群與媽媽持股報酬</h2>
      {render_memory_table(memory_rows)}
    </section>

    <div class="grid">
      <section class="card">
        <h2>全球市場</h2>
        <ul>{render_list(sections.global_markets)}</ul>
      </section>
      <section class="card">
        <h2>台灣市場</h2>
        <ul>{render_list(sections.taiwan_markets)}</ul>
      </section>
    </div>

    <section class="card full">
      <h2>PTT Stock 熱門情緒</h2>
      <ul>{render_list(sections.ptt_sentiment)}</ul>
    </section>

    <section class="card full">
      <h2>資料來源</h2>
      <div class="sources">
        <div><a href="https://finance.yahoo.com/">Yahoo Finance</a></div>
        <div><a href="https://tw.stock.yahoo.com/">Yahoo 股市</a></div>
        <div><a href="https://feeds.feedburner.com/rsscna/finance">CNA Finance RSS</a></div>
        <div>本地腳本：`fetch_ptt_a.py`、`ptt_stock_digest.py`、`fetch_memory_report.py`</div>
      </div>
      <footer>Model: {escape(model_label)}</footer>
    </section>
  </div>
</body>
</html>
"""


def write_digest(html: str, digest_path: Path) -> None:
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(html, encoding="utf-8")


def rebuild_index() -> None:
    log("rebuilding index")
    run_command(["python3", str(INDEX_REBUILD)], cwd=ROOT)


def git_publish(slot_label: str, digest_filename: str) -> str:
    log(f"publishing git changes for {digest_filename}")
    run_command(["git", "add", str(DIGESTS_DIR / digest_filename), str(ROOT / "index.html")], cwd=ROOT)
    status = run_command(["git", "status", "--short"], cwd=ROOT, check=False)
    if not status.strip():
        return "no changes"
    run_command(
        ["git", "commit", "-m", f"feat: add finance digest for {slot_label} CST"],
        cwd=ROOT,
    )
    run_command(["git", "push", "origin", "main"], cwd=ROOT)
    sha = run_command(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT)
    return sha


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", help="HHMM slot or fallback time")
    parser.add_argument("--date", help="YYYY-MM-DD in Asia/Taipei")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-git", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    now = datetime.now(TZ)
    target_date = args.date or now.strftime("%Y-%m-%d")
    slot = normalize_slot(args.slot, now)
    digest_name = f"{target_date}-{slot}.html"
    digest_path = DIGESTS_DIR / digest_name
    public_url = digest_public_url(digest_name)
    slot_label = f"{target_date} {slot[:2]}:{slot[2:]}"

    try:
        if digest_path.exists():
            print(
                json.dumps(
                    {
                        "status": "skipped",
                        "digest": digest_name,
                        "path": str(digest_path),
                        "url": public_url,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        log(f"starting digest build for {digest_name}")
        local_data = collect_local_data()
        news_data = collect_news_data()
        prompt = build_model_prompt(
            date_str=target_date,
            slot=slot,
            local_data=local_data,
            news_data=news_data,
        )
        sections, model_label = call_primary_model(prompt)
        memory_rows = parse_memory_rows(local_data["memory_report"])
        html = build_digest_html(
            date_str=target_date,
            slot=slot,
            sections=sections,
            memory_rows=memory_rows,
            model_label=model_label,
        )

        if args.dry_run:
            log("dry-run completed")
            print(json.dumps({
                "digest": digest_name,
                "headline": sections.headline,
                "executive_summary": sections.executive_summary,
                "memory_rows": len(memory_rows),
            }, ensure_ascii=False, indent=2))
            return 0

        write_digest(html, digest_path)
        log(f"wrote digest to {digest_path}")
        rebuild_index()

        git_result = "skipped"
        if not args.skip_git:
            git_result = git_publish(slot_label, digest_name)

        send_telegram_message(
            "\n".join(
                [
                    f"財經摘要已更新：{slot_label}",
                    digest_name,
                    public_url,
                    sections.headline,
                    f"git: {git_result}",
                ]
            )
        )

        print(
            json.dumps(
                {
                    "status": "ok",
                    "digest": digest_name,
                    "path": str(digest_path),
                    "url": public_url,
                    "git": git_result,
                    "headline": sections.headline,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        if not args.dry_run:
            try:
                send_telegram_message(
                    "\n".join(
                        [
                            f"財經摘要失敗：{slot_label}",
                            digest_name,
                            str(exc),
                        ]
                    )
                )
            except Exception as notify_exc:  # noqa: BLE001
                log(f"telegram failure notification failed: {notify_exc}")
        raise


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
