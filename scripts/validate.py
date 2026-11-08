#!/usr/bin/env python3
"""Validate the Actually-Free Job Training Directory.

Offline test suite (no network). Exits non-zero on any failure.

Checks:
  1. data/entries.json parses and each entry has the full required schema.
  2. Entry ids are unique; categories are from the known set.
  3. URLs are HTTPS and carry no affiliate or tracking parameters
     (utm_*, affiliate, cjevent, fbclid, gclid, ...).
  4. Verification dates are ISO dates and recheckBy > verifiedOn.
  5. House text is present (asdale credit for Asdale Dynamics, LLC; health
     education-only disclaimer).
  6. Generated artifacts (index.md, pages/*.md, site/index.html) exist,
     match a fresh in-memory build, and contain every entry.
  7. HTML is sane: one <html>, no external script/CDN assets, no inline
     event handlers.

Usage: python3 scripts/validate.py   (run from the repository root)
"""

import datetime
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build  # noqa: E402  (reuse the same generators for a freshness check)

REQUIRED_ENTRY_FIELDS = [
    "id", "title", "category", "provider", "url", "whatItIs", "freeWhat",
    "paperTrail", "timeNeeded", "catchOrLimit", "tags", "verifiedOn", "recheckBy",
]
REQUIRED_CATEGORY_FIELDS = ["id", "name", "blurb", "entries"]
KNOWN_CATEGORIES = {
    "audit-courses", "library-platforms", "free-certificates",
    "workforce-programs", "health-ceu",
}
TRACKING_TOKENS = ("utm_", "affiliate", "cjevent", "_hsenc", "fbclid", "gclid", "mkt_tok")
BANNED_IN_TEXT = ("http://", "utm_", "affiliate")
HOUSE_CREDIT = "Asdale Dynamics, LLC"
PROBLEMS = []


def check(condition, message):
    if not condition:
        PROBLEMS.append(message)


def iso(value):
    try:
        return datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def main():
    data = build.load_data()

    # -- Data schema --------------------------------------------------------
    check(bool(data.get("siteTitle")) and bool(data.get("tagline")), "siteTitle/tagline missing")
    check(iso(str(data.get("lastVerified", ""))) is not None, "lastVerified not an ISO date")

    categories = data.get("categories", [])
    check(len(categories) >= 4, f"expected >=4 categories, found {len(categories)}")

    seen_ids = set()
    total_entries = 0
    for cat in categories:
        cname = cat.get("id", "<missing>")
        check(cat.get("id") in KNOWN_CATEGORIES, f"unknown category id: {cname}")
        for field in REQUIRED_CATEGORY_FIELDS:
            check(field in cat and cat[field], f"category {cname} missing field: {field}")
        check(isinstance(cat.get("entries"), list) and cat["entries"],
              f"category {cname} has no entries")
        for e in cat.get("entries", []):
            total_entries += 1
            eid = e.get("id", "<missing>")
            check(e.get("category") == cat.get("id"),
                  f"entry {eid}: category field does not match its section")
            for field in REQUIRED_ENTRY_FIELDS:
                check(field in e and e[field], f"entry {eid} missing field: {field}")
            check(eid not in seen_ids, f"duplicate entry id: {eid}")
            seen_ids.add(eid)

            url = e.get("url", "")
            parsed = urllib.parse.urlparse(url)
            check(parsed.scheme == "https" and parsed.netloc,
                  f"entry {eid}: url must be absolute https -> {url}")
            query = (parsed.query or "").lower()
            for token in TRACKING_TOKENS:
                check(token not in query,
                      f"entry {eid}: tracking/affiliate token '{token}' in url query")

            check(isinstance(e.get("tags"), list) and len(e.get("tags", [])) >= 2,
                  f"entry {eid}: needs at least 2 tags")
            v_on, recheck = e.get("verifiedOn"), e.get("recheckBy")
            check(iso(v_on) is not None and iso(recheck) is not None,
                  f"entry {eid}: verifiedOn/recheckBy must be ISO dates")
            if iso(v_on) and iso(recheck):
                check(iso(recheck) > iso(v_on), f"entry {eid}: recheckBy must be after verifiedOn")
            check(iso(v_on) == iso(str(data.get("lastVerified"))),
                  f"entry {eid}: verifiedOn ({v_on}) differs from lastVerified "
                  f"({data.get('lastVerified')}); re-verify and re-set both")

            for field in ("whatItIs", "freeWhat", "paperTrail", "timeNeeded", "catchOrLimit"):
                value = e.get(field, "")
                check(len(value) >= 20, f"entry {eid} field '{field}' is too thin ({len(value)} chars)")
                for banned in BANNED_IN_TEXT:
                    check(banned not in value.lower(),
                          f"entry {eid} field '{field}' contains banned token '{banned}'")

    check(total_entries >= 20, f"expected >=20 entries, found {total_entries}")
    print(f"[data] {len(categories)} categories, {total_entries} entries: schema OK")

    # -- Generated artifacts live + fresh -----------------------------------
    generated = {
        "index.md": build.build_index_md(data),
        **{f"pages/{c['id']}.md": build.build_category_md(data, c) for c in categories},
        "site/index.html": build.build_site_html(data),
    }
    for rel, expected in generated.items():
        path = ROOT / rel
        check(path.exists(), f"missing generated artifact: {rel} (run scripts/build.py)")
        if path.exists():
            actual = path.read_text(encoding="utf-8")
            check(actual == expected, f"stale artifact: {rel} (run scripts/build.py)")
    print(f"[build] {len(generated)} generated artifacts present and fresh")

    for cat in categories:
        page = ROOT / "pages" / f"{cat['id']}.md"
        if page.exists():
            text = page.read_text(encoding="utf-8")
            check('What "free" means' in text, f"pages/{cat['id']}.md missing free-means labels")
            for e in cat["entries"]:
                check(e["title"] in text, f"pages/{cat['id']}.md missing entry title: {e['title']}")

    # -- HTML sanity --------------------------------------------------------
    html_text = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    check(html_text.count("<html") == 1, "site/index.html must contain exactly one <html>")
    check(HOUSE_CREDIT in html_text, "HTML missing Asdale Dynamics, LLC credit")
    check("never medical advice" in html_text.lower(),
          "HTML missing health education-only disclaimer")
    external_assets = re.findall(
        r'<(?:script|link)\b[^>]*(?:src|href)="([^"]+)"', html_text)
    for asset in external_assets:
        check(urllib.parse.urlparse(asset).scheme == "",
              f"external CDN asset in HTML: {asset}")
    check(not re.search(r"on(click|load|error|mouseover)=", html_text),
          "inline JS event handler found in HTML")
    check(not re.search(r"<script", html_text, re.I), "<script> tag found in HTML")
    for cat in categories:
        for e in cat["entries"]:
            check(e["url"] in html_text, f"site/index.html missing link for entry {e['id']}")
    print("[html] static site sanity OK (no CDN/no JS, all entry links embedded)")

    # -- Markdown site sanity ----------------------------------------------
    index_md = generated["index.md"]
    for cat in categories:
        check(cat["name"] in index_md, f"index.md missing category: {cat['name']}")
    check("not the same site" in index_md.lower(),
          "index.md missing distinctness note vs sibling directories")

    # -- LICENSE ------------------------------------------------------------
    lic = ROOT / "LICENSE"
    check(lic.exists(), "LICENSE file missing")
    if lic.exists():
        text = lic.read_text(encoding="utf-8")
        check("Copyright (c) 2026 Asdale Dynamics, LLC" in text,
              "LICENSE missing exact copyright line")

    # -- README credit ------------------------------------------------------
    readme = ROOT / "README.md"
    check(readme.exists(), "README.md missing")
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        check(HOUSE_CREDIT in text, "README.md missing Asdale Dynamics, LLC credit")

    # -----------------------------------------------------------------------
    if PROBLEMS:
        print(f"\nFAILED with {len(PROBLEMS)} problem(s):")
        for problem in PROBLEMS:
            print(f"  - {problem}")
        return 1
    print("\nAll validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
