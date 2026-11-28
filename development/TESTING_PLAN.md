# TESTING_PLAN

## Automated (exist today)
| Test | Command | Covers |
|---|---|---|
| Data validation | `python3 tools/validate.py` | Required fields, enums, unique IDs, references (prerequisites, projects, certs, paths, migrations), no later-stage prerequisites, no cycles |
| Validator unit tests | `python3 -m pytest tests/` | Each validation rule rejects a bad change; current data passes |
| Browser smoke test | `python3 tests/e2e_smoke.py` (set `CHROME_PATH` if Playwright's Chromium isn't installed) | Loads with no JS errors; every destination, lens and Plan section renders; node shows name not ID; panel shows ID; status persists across reload; Kanban drag; export; reset; phone width loads. Screenshots in `build/screens/` |

Last run 23 Nov 2026: all pass (data v1.2).

## To add (Stage 3–5)
- **Upgrade/migration test:** build A (current data) → set progress → export; build B with a renamed ID (with
  migration), a removed ID and an added ID → import → assert nothing lost (renamed carried over, removed in
  orphans, added empty).
- **Import validation:** malformed JSON, wrong shape, older storage version, merge vs replace.
- **Locked/ready logic:** unit-test `isBlocked` on fixtures (cheap to test via the smoke harness with `page.evaluate`).
- **Keyboard path:** tab to a node, Enter opens the panel, status buttons reachable, Escape closes.
- **Accessibility scan:** axe-core run in the smoke test (dev-only dependency; pin a version) or a documented manual pass.
- **UI (implemented in `tests/e2e_ui.py`):** navigation marks the current destination and lens (`aria-current`) and keeps the view and filters in the URL; the List names source and line and opens each stage gate; Space/Escape and focus return on nodes; search and `#ID` deep links; group clusters; job band; focus chain; background click; resize keeps zoom; Kanban drop rule; data-driven cert timeline; contrast token; no page overflow at 390 px in every view; encrypted timetable round trip (wrong password refused, no plain text in the build).
- **Today, sessions, route (implemented in `tests/e2e_today.py`):** Start puts a ready competency on the line; a session logs in one step and records only what was typed; logging never changes a status unless "Also mark in progress" is ticked; Remove takes two clicks; Track and Learn are separate tabs; an import merge keeps sessions from both sides and a crafted log is shown as text; the Route lens centres on the URL's station, moves along the line and Back returns; at 390 px the destinations sit in a bottom bar and the drawer fills the screen.
- **Sync (implemented in `tests/e2e_sync.py`):** with sync off there is no network request; connect creates one secret gist and a second browser finds it; both sides' progress is kept; edits, cleared fields, removed sessions and a reset travel; differing notes are joined; a rejected token is reported and local changes kept; a gist with foreign content is never overwritten; the token is never in progress or an export.
- **Persistence (implemented in `tests/e2e_persistence.py`):** progress survives a data update that renames, removes and adds competencies; v1 → v2 migration; orphans; seed import; export → import on a fresh origin; lateness; backup reminder. `tests/upgrade_demo.py` is the Gate 3 demo against an older git ref.
- **Privacy lint (implemented in `tools/validate.py`, tested in `tests/test_validate.py`):** record IDs and records notes anywhere in `data/`, evidence levels or status in `ev`, record IDs and private terms (`private/privacy-terms.txt`) in every public file. Guards AUDIT P-01, A-21.
- **Import sanitizing (implemented in `tests/e2e_smoke.py`):** a crafted import runs no script; unknown IDs, bad statuses and non-string fields are dropped; the same file imports twice (A-12, A-22).

## Manual checklist (before each release)
- [ ] Chrome and Firefox desktop; Safari if available; phone width (390 px) in devtools and on a real phone
- [ ] From `file://` and from `python3 -m http.server -d dist` (same-origin behaviour of a static host)
- [ ] Offline (devtools "Offline"): everything works
- [ ] Keyboard only: reach and change a status; open/close the panel; switch views
- [ ] Zoom/pan, fit toggle, path filter, "Locked only", "All dependencies"
- [ ] Export → reset → import restores everything
- [ ] Previous release's export imports into this release

## CI (in the deploy workflow)
validate → unit tests → build → smoke test (Playwright with Chromium) → upload `dist/` → deploy. Any failure stops
the deploy.
