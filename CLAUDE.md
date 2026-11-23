# CLAUDE.md

Project: the unified NTI + DEBI cloud-security learning roadmap and its interactive tracker (a single offline
HTML app, to be hosted on GitHub Pages). "The owner" below is the person whose study plan this is.

## Read first, in this order
Personal and meta docs live in `private/docs/` (gitignored; its own local git repo, never pushed).
1. `private/docs/CLAUDE_CODE_HANDOFF.md` — your brief: stages, authority, approval gates.
2. `private/docs/AUDIT.md` — known contradictions, bugs, privacy blockers, decisions.
3. `private/docs/STUDY_PLAN.md` — the learning methodology you must not silently change.
4. `development/ARCHITECTURE.md` — how the app and data are built.
If `private/` is missing (e.g. a fresh clone), stop and ask the owner for it; don't reconstruct it.

## Hard rules
- **Inspect before you modify. Work in the stages in the handoff and stop at each approval gate.**
- **Never push, create a GitHub repo, enable Pages or publish anything without the owner's explicit "yes" in this session.** A local `git init` and local commits are fine once Stage 1 is approved.
- **Never commit `private/` or `archive/`.** Before any commit, run `git status --ignored` and confirm both are ignored.
- **Personal data is private by default.** No names, schedules, record IDs (`H-…`), evidence levels or CV diagnostics in committed files. The one exception is the encrypted timetable blob (AUDIT D-10). `tools/validate.py` lints `data/` and public docs for this.
- **Never fabricate or infer learning progress.** Progress comes only from the owner (in the app) or from the Study Plan records (`private/progress/`). A course finished is not a competency completed.
- **Study-plan decisions are the owner's.** Don't change decisions listed in `private/docs/STUDY_PLAN.md` §5; if something conflicts, add it to `private/docs/AUDIT.md` with a recommendation and ask.
- **`data/*.json` is the single source of truth for roadmap content.** Never hand-edit `dist/`. Keep competency IDs stable; retired or renamed IDs go in `data/id-migrations.json`.
- **Keep the output a single self-contained file that works from `file://` and offline.** No runtime CDN, no fetch of data at runtime, no build-time framework unless the owner approves it after you explain why.
- **NTI course material must never enter the repo** (NTI's terms forbid publishing it). Only the owner's own summaries and module names/hours.
- Back up before destructive changes (git commit or a copy under `archive/`).
- Explain significant architectural decisions before implementing them.

## Commands
```bash
python3 tools/validate.py        # data checks (IDs, references, stage order, cycles)
python3 tools/build.py           # validate + inline data into dist/index.html
python3 tools/docgen.py --write # regenerate ROADMAP.md Phase 2/4/5 from data (--check in CI)
python3 -m pytest tests/         # unit tests (validator)
python3 tests/e2e_smoke.py       # browser smoke test of dist/index.html (needs Playwright + Chromium)
python3 tests/e2e_persistence.py # progress survives renames/removals/additions, imports, seed
python3 tests/e2e_ui.py          # keyboard, search/deep links, clusters, mobile, encrypted timetable
python3 tests/upgrade_demo.py    # export from an older build (git ref), upgrade, import: nothing lost
python3 tools/seed_from_records.py  # records snapshot (private/) -> progress seed (private/)
```
Open `dist/index.html` directly in a browser to use the app.
