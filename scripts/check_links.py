#!/usr/bin/env python3
"""Live link checker for the Actually-Free Job Training Directory.

Fetches every entry URL from data/entries.json (a real GET, because many
paywall-era sites reject HEAD), follows redirects, and classifies:

  PASS          HTTP 2xx (redirects followed)
  BOT-BLOCKED   Cloudflare/bot walls and rate limits from hosts we know work
                in a normal browser (allowlist below). Treated as OK-with-note.
  FAIL          anything else (4xx/5xx not on the allowlist, DNS errors, etc.)

Writes reports/link-check-YYYY-MM-DD.md and exits non-zero on any FAIL,
so this doubles as a network test in CI-ish workflows.

Politeness: sequential requests, small delay, honest User-Agent, 20s timeout.
No API keys, no personal data, nothing fetched gets logged beyond status codes.

Usage: python3 scripts/check_links.py   (run from the repository root)
"""

import datetime
import json
import pathlib
import sys
import time
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "entries.json"
REPORTS = ROOT / "reports"

USER_AGENT = ("AsdaleDynamicsFreeDirectoryLinkCheck/1.0 "
              "(contact: none; public repo checker) "
              "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/128.0")
TIMEOUT = 20
DELAY_BETWEEN = 1.5

# Hosts that 403/429 bot traffic but render fine for humans in a browser.
BOT_BLOCKED_HOSTS = {
    "www.open.edu",          # OpenLearn (Open University)
    "online.stanford.edu",   # Stanford Online
    "www.medscape.org",      # Medscape CE
    "www.cdc.gov",
    "www.kaggle.com",        # behind bot challenge sometimes
    "skillbuilder.aws",      # bot challenge sometimes; verified in browser
}

STATUS_QUEUE = []


def classify(url, status, error):
    host = urllib.request.urlsplit(url).netloc
    if status is not None and 200 <= status < 300:
        return "PASS"
    if status in (403, 429, 999, 503, 405) and host in BOT_BLOCKED_HOSTS:
        return "BOT-BLOCKED"
    if error == "bot-suspect" and host in BOT_BLOCKED_HOSTS:
        return "BOT-BLOCKED"
    return "FAIL"


def fetch(url):
    """Return (status_code or None, error_string or None)."""
    request = urllib.request.Request(
        url, method="GET",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,text/*;q=0.7,*/*;q=0.3",
            "Accept-Language": "en-US,en;q=0.9",
        })
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT)
        status = response.getcode()
        response.close()
        return status, None
    except urllib.error.HTTPError as err:
        return err.code, None
    except urllib.error.URSError as err:
        reason = getattr(err, "reason", err)
        return None, str(reason)
    except Exception as err:  # sockets/timings
        return None, str(err)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    results = []
    late = []
    today = datetime.date.today()
    for cat in data["categories"]:
        for e in cat["entries"]:
            target = e["url"]
            status, error = fetch(target)
            verdict = classify(target, status, error)
            results.append({
                "category": cat["name"],
                "entry": e["title"],
                "id": e["id"],
                "url": target,
                "http": status if status is not None else "-",
                "error": error or "",
                "verdict": verdict,
            })
            overdue = e.get("recheckBy", "9999-12-31") < today.isoformat()
            if overdue:
                late.append(e["id"])
            print(f"[{verdict:^11}] {status if status else error}  {target}")
            time.sleep(DELAY_BETWEEN)

    passes = sum(1 for r in results if r["verdict"] == "PASS")
    blocked = sum(1 for r in results if r["verdict"] == "BOT-BLOCKED")
    fails = sum(1 for r in results if r["verdict"] == "FAIL")

    REPORTS.mkdir(exist_ok=True)
    report_path = REPORTS / f"link-check-{today.isoformat()}.md"
    lines = [
        f"# Link check — {today.isoformat()}",
        "",
        f"Checked {len(results)} links from `data/entries.json` "
        f"(live GETs, redirects followed).",
        "",
        f"- **PASS:** {passes}",
        f"- **BOT-BLOCKED** (site 403/429s scripts but verified working in a "
        f"normal browser; allowlisted in `scripts/check_links.py`): {blocked}",
        f"- **FAIL:** {fails}",
        "",
        "Re-verify note: entries with `recheckBy` before today need a fresh "
        "human pass — see the table's last column.",
        "",
        "| Verdict | HTTP | Entry | Category | URL | Error | Overdue? |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        overdue = "yes" if r["id"] in (late) else ""
        note = r["error"] or ""
        lines.append("| {} | {} | {} | {} | <{}> | {} | {} |".format(
            r["verdict"], r["http"], r["entry"], r["category"], r["url"], note, overdue))
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"Report written to {report_path.relative_to(ROOT)}")
    print(f"PASS {passes} / BOT-BLOCKED {blocked} / FAIL {fails}")
    if late:
        print(f"WARNING: {len(late)} entries past their recheckBy date: {', '.join(late)}")
    if fails:
        print("FAILED: fix or remove failing links (update data/entries.json, rebuild).")
        return 1
    print("Link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
