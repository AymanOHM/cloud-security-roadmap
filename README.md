# Cloud Security Study Plan — NTI + DEBI unified roadmap

A competency-based learning roadmap that merges two training programs (NTI's DevSecOps track and DEBI's
Cybersecurity track) with independent learning, aimed at a DevOps/cloud entry role that grows into
DevSecOps and cloud security. It comes with an interactive, offline tracker: a flowchart, stage map,
Kanban board, checklist, career-path view, NTI vs DEBI comparison, project progression, certification
timeline and progress dashboard.

**Status (23 Nov 2026):** data v1.2, app working locally, not yet published. Prepared for Claude Code to
audit, improve and deploy to GitHub Pages. Claude Code starts with `CLAUDE.md`.

## Use the app now
Open `dist/index.html` in any browser. It works offline. Progress is saved in that browser only; use
Dashboard → Export to back it up.

To rebuild after changing data: `python3 tools/build.py`.

## What's where

| Path | Purpose | Authority |
|---|---|---|
| `CLAUDE.md` | Rules Claude Code loads automatically | — |
| `ROADMAP.md` | The written roadmap: curriculum analysis, overlap matrix, career analysis, staged roadmap, projects, certifications, weekly execution | **Master for roadmap analysis** |
| `curriculum/` | Verified facts and unknowns per program (`NTI.md`, `DEBI.md`) and external benchmarks | Facts with sources |
| `data/` | Roadmap content as JSON: competencies, stages, projects, certifications, comparison, ID migrations | **Master for app content** |
| `app/template.html` | The app (HTML/CSS/JS) with a data placeholder | Source |
| `tools/` | `validate.py`, `build.py`, `docgen.py` | Source |
| `tests/` | Validator unit tests and a browser smoke test | Source |
| `dist/` | Built app (`index.html`); gitignored, rebuilt by CI | Generated |
| `development/` | Requirements (incl. design spec), architecture, testing plan, deployment plan, draft Pages workflow | Plans |
| `maintenance/` | How to update the roadmap without rebuilding the app; changelog | Process |
| `private/` | Personal and meta docs (`docs/`: handoff, audit, study plan, project context), original PDFs, briefs, study-plan copies, progress snapshot, timetable. **Gitignored, never published**; its own local git repo | Sources |
| `archive/` | Backups of earlier versions. Gitignored | Backup |

**Layout notes:** career direction is `ROADMAP.md` Phase 3; the learning methodology summary and the audit
log are personal and live in `private/docs/` (references like "AUDIT A-06" in these docs point there). The curriculum comparison is
`ROADMAP.md` Phase 2 plus `data/comparison.json`, so it isn't repeated in `curriculum/`. The design spec is
part of `development/REQUIREMENTS.md`. Resources live inside each competency in `data/competencies.json`
rather than in a separate `resources.json`, so a resource can't drift from the competency it serves.

## Privacy model
- The public repo will hold the app, the roadmap data and the docs. GitHub Pages hosts the app only.
- Personal learning progress lives in the browser (localStorage) and in exported JSON files, never in the repo.
- `private/` holds personal and third-party material and is gitignored.
- Personal data is private by default: `tools/validate.py` fails on record IDs, evidence-level status text or
  the owner's name in `data/` and the public docs. The only personal item planned for the repo is the weekly
  timetable, as an encrypted blob unlocked in the app (not yet implemented).

## Requirements
Python 3.10+ for the tools. For tests: `pip install -r requirements-dev.txt` and
`python3 -m playwright install chromium`. The app itself needs only a browser.
