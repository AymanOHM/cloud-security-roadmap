# CHANGELOG

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
