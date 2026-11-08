# The Actually-Free Job Training Directory

A plain-English, warm Gen-X-neighbor-quality directory of **job Training and upskilling that costs $0.00**: university courses taken in audit mode, learning platforms already paid for by your public library, certificates that are genuinely free (Google and cloud basics included), US state and federal workforce programs, and CEU samplers for licensed health workers.

Part of the Asdale Dynamics "actually free" family — every entry documents **exactly what "free" means for that offer**, because "free" is the most abused word in course marketing.

## What's inside

| Path | What it is |
| --- | --- |
| `data/entries.json` | The single source of truth: 28 verified offers in 5 categories |
| `index.md` + `pages/*.md` | The Markdown site (hand-readable GitHub/VS Code rendering) |
| `site/index.html` | The static HTML site — single file, zero JS, zero CDN, opens over `file://` |
| `scripts/build.py` | Regenerates all Markdown + HTML from the JSON |
| `scripts/validate.py` | Offline test suite: schema, links hygiene, artifact freshness, house text |
| `scripts/check_links.py` | Live link checker; writes `reports/link-check-*.md` |
| `reports/` | Dated link-check reports |

## Run it (locally, no installs)

Requires Python 3.9+. From the repository root:

```bash
python3 scripts/build.py        # regenerate index.md, pages/, site/index.html
python3 scripts/validate.py     # run the offline test suite
python3 scripts/check_links.py  # live-check every link (network needed)
```

Then just open `site/index.html` in any browser, or read `index.md` in any Markdown viewer. No build tools, no node modules, no API keys, no accounts.

## Editing an entry

1. Edit `data/entries.json` — never the generated files.
2. When you re-verify an offer by hand, set that entry's `verifiedOn` and `recheckBy` (and the top-level `lastVerified`) to today.
3. Run `build.py`, then `validate.py`. Fix anything it flags.
4. Periodically run `check_links.py`; it writes a dated report under `reports/`.

## The house rules

- Every offer must be free **in the way described** for the learner: if a paywall appears, the entry gets fixed or removed.
- **What "free" means** is spelled out per entry: free everywhere (MIT OCW), free with a library card (Gale Courses), free course content but paid paper (Coursera/edX audit), or a government grant that pays tuition for you (WIOA, Michigan Reconnect).
- No affiliate links, no referral codes, no tracking parameters, no ads, no analytics. There is nothing to buy, because we are not for sale.
- Health CEU content is **education for license renewal, never medical advice**; learners confirm credit types with their licensing board.
- Government program terms change — the official linked page is always the source of truth.

## How this stays distinct from the sibling directories

- `free-learn-online-directory` — the learner-favorites catalog for learning *anything* online (language apps, textbook archives, coding walks).
- `free-nursing-student-freebies-directory` — freebies for nursing *students* (flashcards, NCLEX practice, journal access, scholarships).
- **This directory** — career *upskilling* specifically: audit-mode university courses, employer-facing certificates, workforce funding that pays your tuition, and licensed-professional CEU samplers.

## Built by

### Asdale Dynamics, LLC

Built by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — plain-English AI education, books, and practical tools, "explained like a friend would." MIT licensed (`LICENSE`); all contributions should respect the no-secrets, no-personal-data, no-affiliates house rules.

*Dylan Asdale, RN turned AI author, maintains the health CEU category with a nurse's eye and a licensure board's paranoia.*

## Known gaps

See `STATUS.md` for current verification dates, link-check results, and honest gaps.
