# REQUIREMENTS (incl. design spec)

Status re-assessed 23 Nov 2026 in the Stage 1 audit (data v1.2, verified in the browser) and updated at Gate 1
with the owner's decisions (AUDIT D-03 – D-10): ✅ implemented · ◐ partial · ✗ missing.

## Functional

### Views
| ID | Requirement | Status |
|---|---|---|
| FR-1 | Flowchart of the whole journey: competencies left to right in dependency order, prerequisites drawn as arrows, zoom and pan | ✅ Implemented |
| FR-2 | Stage map: the five stages (Foundation; Cloud and DevOps Engineering; Security Engineering; Cloud Security Specialization; Portfolio and Job Readiness) × domains, with stage gates | ✅ Implemented |
| FR-3 | Distinct visual identifiers for NTI, DEBI, independent, shared and existing competencies, with a legend | ✅ Implemented |
| FR-4 | Node headline is the competency **name**; the ID appears in details, chips and checklist | ✅ Implemented |
| FR-5 | Kanban: Locked / Ready / In progress / Completed; drag to change status; filters by stage, path, search | ◐ Partial: mouse-only drag; Locked → Ready snaps back (A-13); unusable at 390 px (A-17) |
| FR-6 | Competency checklist with filters (status, source, stage, locked) | ✅ Implemented |
| FR-7 | Career specialization decision point: five paths, shared vs path-specific competencies, recommended path highlighted, highlight on graph | ◐ Partial: core + path double counting (A-18) |
| FR-8 | NTI vs DEBI comparison with NTI module hours and verified/unverified notice | ✅ Implemented |
| FR-9 | Project progression PS-1 … PS-8 with competencies and progress | ✅ Implemented |
| FR-10 | Certification timeline with readiness from competencies | ◐ Partial: hard-coded timeline window (A-20) |
| FR-11 | Dashboard: overall and per-stage/per-source progress, skills radar, next up, in progress, locked with blockers, existing to claim | ✅ Implemented |
| FR-12 | Search and focus a competency in the graph; deep links `#ID` | ✗ Missing |
| FR-13 | "Focus chain" mode: show only a competency's prerequisites and what it unlocks | ◐ Partial (highlight only) |
| FR-14 | Timetable view: the owner's weekly timetable, stored only as an encrypted blob in the repo and unlocked with a password; in-app encrypt panel produces the blob (D-10) | ✗ Missing |
| FR-15 | "Late" indicator per stage, project and cert: window passed with work not done → "cut or re-plan" prompt; never a missed-session count (D-10) | ✅ Implemented (stages and projects carry `due`; certs use `end`) |

### Competency details
| ID | Requirement | Status |
|---|---|---|
| FR-20 | Panel shows name, ID, description, why, objectives, prerequisites, unlocks, NTI material, DEBI material, resources, labs, evidence of mastery, hours, career paths, project stages | ✅ Implemented |
| FR-21 | Missing source information is shown as such ("not stated in the source material"), never invented | ✅ Implemented |
| FR-22 | Evidence fields aligned with the Study Plan (level E0–E4, U/E/D, evidence link) | ✅ Implemented: level, U/E/D, link, last verified; "Completed without evidence" until E4 + link (D-03) |

### Progress
| ID | Requirement | Status |
|---|---|---|
| FR-30 | Status per competency: Not started / In progress / Completed | ✅ Implemented |
| FR-31 | Locked state when prerequisites aren't completed; show the blockers | ✅ Implemented |
| FR-32 | Notes and evidence text per competency | ✅ Implemented (notes, evidence notes, evidence block) |
| FR-33 | Progress by stage, source, domain | ✅ Implemented |
| FR-34 | Persist in localStorage; export, import, reset | ✅ Implemented: v2 envelope; export, import with validation, reset with backup |
| FR-35 | Survive data updates: versioned storage, ID migrations, orphans | ✅ Implemented: v1 → v2 migration, renames merged, splits and removed IDs kept as orphans |
| FR-36 | Import with validation, preview and merge; auto-backup before import/reset; backup reminders | ✅ Implemented: preview, merge or replace, backup download before import/reset, 7-day reminder |
| FR-37 | First-run import on a new origin (file:// ↔ Pages) | ✅ Implemented: first-run notice on an empty origin |
| FR-38 | Optional progress-seed import from the Study Plan records | ✅ Implemented: `tools/seed_from_records.py` + seed import with preview (D-06) |

### Maintenance
| ID | Requirement | Status |
|---|---|---|
| FR-40 | Roadmap content editable as data without touching app code | ✅ Implemented |
| FR-41 | Validation of data before build (IDs, references, stage order, cycles) | ◐ Partial: no privacy lint or core-exclusivity rule (A-21) |
| FR-42 | Written-roadmap tables regenerated from the same data | ✅ Implemented (output still pasted into ROADMAP.md by hand) |
| FR-43 | App shows a summary of data changes since the last visit | ✅ Implemented: "changed since your last visit" notice |

## Non-functional
| ID | Requirement | Status |
|---|---|---|
| NFR-1 | One self-contained HTML file; no external dependencies; works offline and from `file://` | ✅ Implemented (no requests; only SVG namespace strings) |
| NFR-2 | Hostable on GitHub Pages; deployed by GitHub Actions | ◐ Partial: draft workflow only |
| NFR-3 | Responsive: usable at 390 px width (panel becomes full-screen) | ◐ Partial, close to failing (A-15 – A-17) |
| NFR-4 | Accessibility toward WCAG 2.1 AA: keyboard access to every action (incl. status changes), visible focus, contrast ≥ 4.5:1 for text, names for SVG controls, no colour-only meaning | ◐ Partial (AUDIT_REPORT §3) |
| NFR-5 | Performance: first render < 1 s on a mid-range laptop; interactions instant at ~150 nodes | ✅ Implemented at 86 nodes |
| NFR-6 | Privacy: no personal data in the repo or the deployed site; progress never leaves the browser except by explicit export | ◐ Partial (P-01, P-02) |
| NFR-7 | No analytics, trackers, cookies or third-party requests | ✅ Implemented (verified) |

## Design spec
- **Aesthetic:** professional technical dashboard; **dark theme by default**; restrained colour; no decorative animation.
- **Colour tokens** (`:root` in the template): NTI blue `#4c8dff`, DEBI purple `#c27bff`, independent amber `#f0a83a`,
  shared teal `#2fbfa8`, existing slate `#9aabbd` with a dashed border; status: ready (outline), in progress `#e3b341`,
  completed `#3fb950`, locked = padlock icon (grey), not red, because most items start locked.
- **Hierarchy:** node = name (2 lines max) + small muted line (stage · source in the flowchart); status dot or padlock
  top-right; "have"/"refresh" tag bottom-right. Stage headers carry a progress bar; gates are diamonds.
- **Interaction:** click a node → detail panel; selected node highlights incoming (blue) and outgoing (purple)
  edges; wheel to zoom, drag to pan, buttons for zoom in/out/fit; filters are shared between graph views.
- **Typography:** system UI font stack; no web fonts (offline).
- **Copy:** plain English, short; honest labels for unknowns ("unverified", "not stated in the source material").
