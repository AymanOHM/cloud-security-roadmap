# Cloud Security Roadmap — NTI + DEBI unified

A competency-based learning roadmap that merges two Egyptian training programs (NTI's DevSecOps track and
DEBI's Cybersecurity track) with independent learning. It aims at a junior DevOps/cloud role that grows into
DevSecOps and cloud security, with 107 competencies in five stages, eight project stages and a certification
plan.

It comes with an **offline, single-file tracker** in three places: **Today** (what you're on, what's next, a
one-step session log), **Roadmap** (every competency as a list, a board, one competency's route, or the whole
map, with one set of filters kept in the URL) and **Plan** (career paths, projects, certifications, NTI vs DEBI,
timetable, skills).

- **Live site:** https://aymanohm.github.io/cloud-security-roadmap/
- **Written roadmap:** [`ROADMAP.md`](ROADMAP.md)

## Use it
Open the site, or open `dist/index.html` from a local build. Everything works offline; nothing is sent anywhere.

- **Progress stays in your browser** (localStorage). The local file and the website keep **separate** progress:
  export on one (Data → Export) and import on the other. Import shows a preview and downloads a backup first.
- **Evidence, not completion.** A competency counts as done at evidence level E4 with a link; a finished course
  is E0–E2 at most. "Completed" without that shows a warning.
- **Find things:** the search box (`/`), links like `#NET-3` or `#roadmap/list?stage=FND&status=ready`, and the
  Route lens for one competency's prerequisites and what it unlocks. Keyboard: Enter or Space opens, Escape closes,
  arrow keys switch a competency's Track and Learn tabs.
- **Log a session** from Today or a competency's Track tab: a line of what you did, the minutes, optionally a new
  evidence level. A session never changes a status unless you tick "Also mark in progress".
- **Timetable:** published only as encrypted data and unlocked with the owner's password.

## Change the roadmap
All content is data in `data/*.json`; the app is generated from it.

```bash
python3 tools/validate.py          # IDs, references, stage order, cycles, privacy lint
python3 tools/build.py             # validate + inline the data into dist/index.html
python3 tools/docgen.py --write    # regenerate the ROADMAP.md tables from the data
```

Renamed or retired IDs go in `data/id-migrations.json` so saved progress follows them. The step-by-step guide is
[`maintenance/UPDATE_GUIDE.md`](maintenance/UPDATE_GUIDE.md); the history is in
[`maintenance/CHANGELOG.md`](maintenance/CHANGELOG.md).

## Tests
Python 3.12+. `pip install -r requirements-dev.txt && python3 -m playwright install chromium`, then:

```bash
python3 -m pytest tests/           # validator and seed-parser unit tests
python3 tests/e2e_smoke.py         # every view renders; status, export, import safety
python3 tests/e2e_persistence.py   # progress survives renames, removals and additions; import/export
python3 tests/e2e_ui.py            # keyboard, search, deep links, phone layout, encrypted timetable
python3 tests/e2e_today.py         # Today, the session log, the Track/Learn drawer, the Route lens
```

GitHub Actions runs all of them on every push and pull request, and deploys `dist/` to GitHub Pages from `main`
(`.github/workflows/deploy-pages.yml`).

## What's where
| Path | Purpose |
|---|---|
| `ROADMAP.md` | The written roadmap: curriculum analysis, overlap matrix, career analysis, staged roadmap, projects, certifications, weekly execution (master copy) |
| `data/` | Roadmap content: competencies, stages, groups, projects, certifications, comparison, ID migrations, the encrypted timetable (master for the app) |
| `app/template.html` | The app (HTML/CSS/JS) with a data placeholder; no frameworks, no runtime requests |
| `tools/` | `validate.py`, `build.py`, `docgen.py`, `seed_from_records.py` |
| `tests/` | Unit and browser tests; `upgrade_demo.py` proves an upgrade from an older build loses nothing |
| `curriculum/` | Verified facts and unknowns per program, and external benchmarks |
| `development/` | Requirements and design spec, architecture, testing plan, deployment plan |
| `maintenance/` | Update guide and changelog |

`private/` (personal notes, records and sources), `archive/`, `dist/` and `build/` are gitignored and never published.

## Privacy
The repository and site hold the roadmap, never learning progress. `tools/validate.py` fails the build if record
IDs, evidence-level status text or private terms appear in the data or any published file, and if the timetable
file is anything other than ciphertext. NTI course material is never included (NTI's terms forbid publishing it);
only module names and hours are.
