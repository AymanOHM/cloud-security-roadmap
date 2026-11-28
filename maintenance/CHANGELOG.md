# CHANGELOG

## app 2026-11-28 (2): UX redesign — Today, Roadmap, Plan (no data change; storage stays v2)
- **Three destinations instead of ten tabs.** Today (landing), Roadmap and Plan, plus Data. On a phone they sit
  in a bottom bar; the competency drawer becomes a full-screen sheet.
- **Today:** what's in progress, each with a one-step session form; Up next (ready, in roadmap order) with Start;
  Needs attention (late windows, completed without evidence, backup, orphans, the next stage window); this
  week's sessions; today's timetable slots once unlocked.
- **Session log (new, optional `log` field per competency, AUDIT-style rule: owner-entered only):** a line of
  what you did, minutes, optionally a new evidence level. It never changes a status unless "Also mark in
  progress" is ticked. Shown in the drawer, removable with a confirming second click; kept on merge.
- **Roadmap lenses with one filter bar** (search, stage, path, status, source) kept in the URL: List (the
  checklist, with "Waiting on" links per row and stage headers that open each gate), Board (the Kanban; one
  column at a time on a phone), Route (new: one competency as a station, two steps back and two ahead), Map
  (the flowchart). The stage map is retired into the List and the Route.
- **Drawer split into Track | Learn.** Status sits above both; Track holds the session form, evidence, notes and
  sessions; Learn holds the description, objectives, the competency's line, NTI/DEBI material, labs and paths.
- **Plan:** career paths, projects (drawn as a line of stations), certifications, NTI vs DEBI, timetable and
  Skills (the dashboard's breakdowns and radar). Export, import and reset moved to Data.
- **Look:** Wayfind: cool grey paper, blue-black ink, Chivo Mono throughout (SIL OFL, inlined), square 2 px
  borders, cobalt for what is in progress, amber for figures on the ink departure board; a night colourway for
  dark mode. Lanes keep a line colour as a small square.
- **Kept:** competency IDs, `#ID` deep links, the `ntidebi-roadmap-v2` envelope and keys, migrations, orphans,
  import preview and seed, the encrypted timetable, group clusters on the map.
- **Tests:** new `tests/e2e_today.py`; `tests/nav.py` opens a view the way a person would. Existing browser tests
  changed only where they drove the old tabs or the stage map (approved by the owner).

## app 2026-11-28: redesign (no data or storage change)
- New look across all ten views: graphite dark mode and a warm paper light mode, following the OS with an
  Auto / Light / Dark button in the top bar (kept under its own `ntidebi-mode` key, never in progress data).
  Host Grotesk (SIL OFL, `app/fonts/`) is inlined by `tools/build.py`, so the page still works offline.
- Colour now means status: amber in progress and "unlocks", blue "needs", green done, red locked or late.
  Source (NTI, DEBI, ...) is a text label instead of a colour.
- Dashboard opens with the completed count set large, then Next up; projects read as a trail; Kanban cards
  lose the side stripe; the details panel header is held by layout, not `position: sticky`.
- Wording: dashes and middle-dot lists replaced with words and commas; evidence marks and lock/clip symbols
  are text or drawn icons instead of emoji. IDs, hooks, deep links, storage and import/export unchanged.
- Test: the `--faint == #8b949e` check became a contrast check of the quietest text on every surface in both
  modes (WCAG AA 4.5:1).

## data 1.3 · 2026-11-23 (after publishing): prerequisites narrowed
- The six competencies that depended on a whole former group now name only the members they need (the group
  expansion had made them wait on every member): TST-1 ← PY-3, PY-5, WEB-2 · CI-1 ← GIT-1 · CI-5 ← CI-3, GIT-4 ·
  TM-1 ← SEC-3, WEB-8 · APPSEC-1 ← SEC-3, WEB-1, WEB-4 · COMM-3 ← CLD-7, WEB-6, WEB-8. PS-2 now waits on 9 other
  competencies instead of about 25. Saved progress is unaffected (no IDs changed).

## 2026-11-23 — published
- Public repo https://github.com/AymanOHM/cloud-security-roadmap; site https://aymanohm.github.io/cloud-security-roadmap/
  deployed by GitHub Actions on every push to `main` (validate, docgen check, unit, smoke, persistence and UI tests first).
- Stage 5: workflow activated with current action versions, Dependabot, pinned test dependencies, public README,
  pre-publish checklist passed (tree and full history), commit author set to the GitHub no-reply address.
- The owner's encrypted timetable (`data/timetable.enc.json`) added.

## app 2026-11-23 (Stage 4: UX, flowchart, accessibility, timetable)
- **Find things:** search box (ID or name; `/` to focus), `#ID` deep links that update as you select, Focus chain mode.
- **Flowchart:** PY, DB, WEB and GIT drawn as collapsed group boxes (open to expand, D-04); job-readiness items with
  no prerequisites in an "ongoing" band instead of "Start here" (A-19); stage-map nodes name their source.
- **Keyboard and screen readers:** tabs pattern with arrow keys; Enter and Space activate nodes, stage headers,
  gates and Kanban cards; Escape closes the panel and returns focus; node names include ID and status; visible
  focus ring; `--faint` contrast raised (A-08).
- **Phone:** no page overflow at 390 px, compact toolbar with a folding legend, stacked Kanban, checklist as cards,
  readable flowchart scale, pinch-zoom and touch pan; a resize no longer resets your zoom (A-15 – A-17).
- **Fixes:** background click closes the panel (A-14); locked Kanban cards can't drop on Ready (A-13); cert timeline
  derived from the data (A-20).
- **Timetable (D-10):** optional `data/timetable.enc.json` (AES-256-GCM, PBKDF2 600k), unlocked in the Timetable
  view next to the "past their window" list; the in-app panel creates the file. `validate.py` rejects plain text.

## app 2026-11-23 (Stage 3: tracking and persistence; data 1.3 + `due` dates)
- **Storage v2:** versioned envelope; v1 progress migrates on first load (a copy of v1 is kept); renamed IDs
  carry their progress; split or removed IDs become orphans shown on the dashboard (move or delete).
- **Import/export:** import accepts v2, v1 and records seeds, validates every field, shows a preview and lets
  you merge or replace; a backup downloads before import or reset; reminder after 7 days without export;
  first-run notice on an empty browser (file:// and the website keep separate progress).
- **Evidence block (D-03):** level E0–E4, U/E/D, link, last verified; "Completed without evidence" until E4 + link.
- **Records seed (D-06):** `tools/seed_from_records.py` turns the private records snapshot into a seed; the
  seed sets level, U/E/D and last verified only.
- **Data changes notice:** added / removed / renamed since your last visit.
- **Late (D-10):** stages and projects have `due` dates; a passed window with work not done shows "Late" and
  a "cut or re-plan" prompt; never a missed-session count.

## data 1.3 · 2026-11-23 (Stage 2: privacy and approved data changes)
- **Privacy:** personal and meta docs moved to `private/docs/` (gitignored); learning-record notes removed from
  `ev` fields and ROADMAP.md; ROADMAP Phase 7 generalised (the personal timetable stays private); the owner's name
  removed from public files. `tools/validate.py` now runs a privacy lint over `data/` and every public file.
- **Group IDs expanded:** PY-1–7, DB-1–6, WEB-1–8, GIT-1–4 → 25 individual competencies (86 → 107). The old IDs
  are recorded as splits in `id-migrations.json`. Dependents of a group need all of its members.
- **Data:** DB core and a prerequisite of TST-2 (DB-2) and CLD-5 (DB-1, DB-2); K8S-1 core with an artifact as
  evidence; `core` is exclusive of path tags (DSO-1, LOG-1, IR-1, TM-1, APPSEC-1, DSA-1); CSEC-6 needs NET-5;
  CTR-1 needs LNX-4; DSO-1 adds a DAST baseline (OWASP ZAP); NSE 4 conditional on DEBI funding (G15 amended).
- **App:** saved and imported progress is sanitized (known IDs, allowlisted statuses, string fields only) and
  style attributes are escaped, closing a script-injection path (AUDIT A-12); re-importing the same file works;
  career-path "specific" counts exclude core.
- **Tools:** `docgen.py --write` updates ROADMAP Phase 2/4/5 in place, `--check` for CI; ID runs shown as
  `PY-1–7`. Draft workflow uses the validator instead of a grep.

## data 1.2 · package 2026-11-23 (handoff to Claude Code)
- **Fix:** NTI has a 7-hour Git module (Study Plan doc 17 §1). `GIT-1–4` lead source changed Independent → NTI,
  hours added, `ntiHours.Git = 7`, comparison row updated; ROADMAP.md updated to match.
- Added `ntiPart2Hours` (career development, 126 h).
- Source of truth moved from `data.py` (chat build) to `data/*.json`; new `tools/validate.py`, `tools/build.py`,
  `tools/docgen.py`, unit tests and a browser smoke test. `data/id-migrations.json` added (app support pending).
- Handoff documentation, audit, deployment plan and draft Pages workflow added. v1.1 backed up in `archive/`.

## data 1.1 · 2026-11-23
- Compared with devopsroadmap.io; added TST-2 integration testing, CI-5 release automation, CI-6 multi-environment
  promotion, K8S-3 Helm/Kustomize + GitOps (optional); project steps for Twelve-Factor review (PS-3) and an
  experienced reviewer (PS-7). 86 competencies.
- App: new Flowchart view (default), Kanban view, skills radar; node headlines show names, IDs moved to details;
  stage map kept.

## data 1.0 · 2026-11-23
- First interactive roadmap: 82 competencies reusing Study Plan doc 06 IDs plus new cloud-security IDs; five stages
  with gates; eight project stages; certification timeline; NTI vs DEBI matrix; progress in localStorage.
- Written roadmap aligned with Study Plan doc 19 (entry role, project order, weekly slots).
