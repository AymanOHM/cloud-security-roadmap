# TESTING_PLAN

## Automated (exist today)
| Test | Command | Covers |
|---|---|---|
| Data validation | `python3 tools/validate.py` | Required fields, enums, unique IDs, references (prerequisites, projects, certs, paths, migrations), no later-stage prerequisites, no cycles |
| Validator unit tests | `python3 -m pytest tests/` | Each validation rule rejects a bad change; current data passes |
| Browser smoke test | `python3 tests/e2e_smoke.py` (set `CHROME_PATH` if Playwright's Chromium isn't installed) | Loads with no JS errors; all 9 views render; node shows name not ID; panel shows ID; status persists across reload; Kanban drag; export; reset; phone width loads. Screenshots in `build/screens/` |

Last run 23 Nov 2026: all pass (data v1.2).

## To add (Stage 3–5)
- **Upgrade/migration test:** build A (current data) → set progress → export; build B with a renamed ID (with
  migration), a removed ID and an added ID → import → assert nothing lost (renamed carried over, removed in
  orphans, added empty).
- **Import validation:** malformed JSON, wrong shape, older storage version, merge vs replace.
- **Locked/ready logic:** unit-test `isBlocked` on fixtures (cheap to test via the smoke harness with `page.evaluate`).
- **Keyboard path:** tab to a node, Enter opens the panel, status buttons reachable, Escape closes.
- **Accessibility scan:** axe-core run in the smoke test (dev-only dependency; pin a version) or a documented manual pass.
- **Data lint (optional):** ID format, en-dash use in group IDs, no "H-2026…" or other record IDs in `data/` (guards AUDIT P-01).

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
