# STATUS.md — The Actually-Free Job Training Directory

Built: 2026-11-08 · Built by Asdale Dynamics, LLC · MIT licensed

## What was built

A plain-English directory of **zero-dollar job upskilling**, kept distinct from
`free-learn-online-directory` (learner favorites) and
`free-nursing-student-freebies-directory` (nursing-student freebies):

- **`data/entries.json`** — single source of truth: 28 hand-verified offers across 5 categories.
  Each entry states exactly **what "free" means** for that offer, its paper trail
  (certificate/CEU or none), the honest catch, and verification dates
  (`verifiedOn` / `recheckBy`).
- **Markdown site** — `index.md` (top-level) plus `pages/audit-courses.md`,
  `pages/library-platforms.md`, `pages/free-certificates.md`,
  `pages/workforce-programs.md`, `pages/health-ceu.md`.
- **Static HTML site** — `site/index.html`: single self-contained file, no JavaScript,
  no CDN assets, works offline over `file://`. Includes filters-free `<details>` cards
  with "what free means / paper trail / honest catch" per offer.
- **Tooling (Python 3, standard library only)**
  - `scripts/build.py` — regenerates index.md, 5 category pages, and site/index.html
    from the JSON; overwrites stale generated files on each run.
  - `scripts/validate.py` — offline test suite (exit 1 on failure): schema, HTTPS-only
    URLs, anti-affiliate/tracking-parameter checks, date logic, artifact freshness
    (byte-compare against an in-memory build), HTML sanity (no `<script>`, no CDN,
    no inline handlers), missing entry detection, LICENSE/README house text.
  - `scripts/check_links.py` — live link checker (GET with honest UA, 20 s timeout,
    1.5 s spacing); classifies PASS / BOT-BLOCKED (known allowlisted bot walls:
    open.edu, online.stanford.edu, medscape.org) / FAIL; writes dated reports.
  - `reports/link-check-2026-11-08.md` — today's full report.
- **Housekeeping** — `README.md` (usage + house rules + credit), `LICENSE` (MIT,
  `Copyright (c) 2026 Asdale Dynamics, LLC`), `.gitignore`, git repo initialized.

Categories covered, per the brief:

1. **University courses in audit mode** (8): MIT OCW, MIT Open Learning Library,
   Open Yale, CMU Open Learning Initiative, Coursera audit, edX audit, OpenLearn,
   Stanford Online free courses.
2. **Library learning platforms** (3): Gale Courses, Universal Class (IACET CEUs),
   LearningExpress Library.
3. **Free certificates — Google & cloud basics** (8): Google Skillshop, Grow with Google
   free courses, Cisco Networking Academy, AWS Skill Builder free tier, IBM SkillsBuild,
   Kaggle Learn, HubSpot Academy, Semrush Academy.
4. **State & federal workforce programs (US)** (5): CareerOneStop, America's Job Centers
   locator, WorkOne Indiana (+ Workforce Ready Grant note), Michigan Reconnect, Idaho LAUNCH.
5. **Health CEU samplers** (4): TRAIN Learning Network, CDC TRAIN, Alzheimer's Association
   eLearning, Medscape CE — education for license renewal only, never medical advice.

## How to run it

```bash
python3 scripts/build.py        # regenerate index.md, pages/, site/index.html
python3 scripts/validate.py     # offline test suite
python3 scripts/check_links.py  # live link check (network) -> reports/
```

No installs, no dependencies, no API keys, no accounts. Open `site/index.html`
in a browser or read `index.md` in any Markdown viewer.

## Verification results (2026-11-08)

- `python3 scripts/validate.py` → **all checks passed** (schema: 5 categories /
  28 entries; 7 generated artifacts present, fresh, and complete; HTML sanity OK).
- `python3 scripts/check_links.py` → **25 PASS / 3 BOT-BLOCKED / 0 FAIL** across 28 URLs.
  - BOT-BLOCKED are genuine bot walls verified working in a normal browser
    (OpenLearn 403, Stanford Online 403, Medscape CE 429) and are allowlisted
    with an explanatory note in the checker.
- URL candidates were also spot-checked individually with curl before inclusion
  (dead candidates such as `careeronestop.org/Toolkit/Training/find-training.aspx`
  and cf. `cmstraining` paths were rejected; correct live paths found instead).
- Generated files ship byte-identical to a fresh in-memory build (validator-enforced),
  so the committed site is reproducible.

## Known gaps

- **Depth, not breadth:** 28 offers rather than survey-everything depth within
  categories (e.g., only 3 library platforms; state workforce programs are
  exemplars — Indiana, Michigan, Idaho — plus federal finders, not all 50 states).
- **Catalog-level, not course-level:** entries verify whole platforms/programs;
  specific course offerings inside each (and their CE-accreditation flags)
  rotate and need a course-page-level human pass each semester.
- **Bot-walled sites** (OpenLearn, Stanford Online, Medscape) are verified by the
  automated checker only up to the bot wall; browser checks confirmed reachability
  on build day — those need eyes-on re-verification at `recheckBy`.
- **Program economics can move:** workforce program eligibility windows/amounts
  (Reconnect, LAUNCH, WIOA, Workforce Ready Grant) change by budget year.
- **Coursera/edX audit details vary per course** (some courses lack audit; audit
  access windows change by policy) — the entries teach the pattern rather than
  guarantee it per course.
- Friends-of-the-directory extras (resume services, apprenticeship boards,
  union training portals) are not yet included; room to grow without breaking
  the "actually free" rule.
