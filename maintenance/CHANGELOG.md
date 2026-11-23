# CHANGELOG

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
