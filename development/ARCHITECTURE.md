# ARCHITECTURE

Describes the app as it is (data v1.2, 23 Nov 2026) and the recommended persistence design. Claude Code:
verify this against the code in Stage 1; correct this file where it's wrong.

## 1. Overview
```
data/*.json ──► tools/validate.py ──► tools/build.py ──► dist/index.html  (one self-contained file)
                                         ▲
                              app/template.html  (HTML + CSS + JS, placeholder /*DATA*/null)
data/*.json ──► tools/docgen.py ──► build/docgen/*.md  (tables for ROADMAP.md)
```
- No runtime dependencies, no network calls, no framework. Works from `file://`, offline, and on any static host.
- Data is **inlined at build time** (not fetched) so the file still works offline and from disk. Fetching JSON at
  runtime was rejected: browsers block `fetch()` of local files from `file://` pages.

## 2. Data model (`data/`)
| File | Content |
|---|---|
| `roadmap.json` | `schemaVersion` (data schema, int), `dataVersion` (content version string), `stages[]` {id, n, name, window, gate}, `lanes[]` {id, name}, `sources` {NTI, DEBI, IND, SHARED, EXIST → label}, `paths[]` {id, name, rec, entry, why}, `ntiHours`, `ntiPart2Hours` |
| `competencies.json` | Array, **in roadmap order** (this order is the learning sequence shown in the checklist and in ROADMAP.md) |
| `projects.json` | PS-1 … PS-8 {id, name, stage, doc19, window, comps[], arch, steps[], goal, deliv, value} |
| `certifications.json` | {id, name, when, start "YYYY-MM", end, status, cost, fills, verdict, comps[]} |
| `comparison.json` | NTI vs DEBI rows {area, nti, debi, cls, lead, action} |
| `id-migrations.json` | {"migrations": {"OLD-ID": "NEW-ID" \| ["NEW-1", …]}}: a string is a rename, a list is a split (e.g. `PY-1–7` → PY-1 … PY-7, data 1.3). App support pending (AUDIT A-06) |

**Competency fields** (all required; validated by `tools/validate.py`):
| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable ID. Doc 06 scheme or new prefixes (IAC, K8S, DSO, VM, NSEC, LOG, IR, TM, CSEC, JOB). Since data 1.3 there are no group rows; the retired group IDs (`PY-1–7`, `DB-1–6`, `WEB-1–8`, `GIT-1–4`) live only in `id-migrations.json` |
| `name` | string | Short name; shown as the node headline |
| `stage` | FND·CDE·SEN·CSS·JOB | Roadmap stage |
| `lane` | net·lnx·code·ctr·cloud·sec·csec·career | Domain row in the stage map; drives the skills radar |
| `src` | NTI·DEBI·IND·SHARED·EXIST | Lead source |
| `desc`, `why` | string | Description; why it matters |
| `obj`, `res`, `labs` | string[] | Learning objectives; extra resources; labs/exercises |
| `pre` | string[] | Prerequisite IDs (never a later stage; no cycles) |
| `nti`, `debi` | string or null | Relevant program material; `null` = none identified (shown honestly). "(verified …)" / "(unverified)" markers are part of the text |
| `ev` | string | Evidence of mastery. **Must not contain personal progress** (AUDIT P-01) |
| `hours` | string or null | Only when a source states hours |
| `pri` | H·M·L | Priority |
| `existing` | null·"have"·"refresh" | The owner already has it / partly has it |
| `paths` | string[] | `"core"` and/or career path IDs (DSO, CSE, CSO, ASE, CIE) |

## 3. App structure (`app/template.html`, ~610 lines)
Sections, in file order: CSS (dark theme tokens in `:root`) → HTML shell (header, tabs, one `<section>` per view,
side `#panel`) → script: storage · helpers · tabs · shared graph helpers (`Viewer` zoom/pan, `drawNode`,
`drawEdges`) · stage map layout · flowchart layout (longest-path depth columns + barycenter ordering) · shared
state render (`renderGraphState`) · toolbars · Kanban · side panel (competency and stage) · checklist · career
paths · compare · projects · certs · dashboard (incl. skills radar) · header/refresh.

- **Global data:** `const D = /*DATA*/` (build payload: version, schemaVersion, stages, lanes, sources, paths,
  ntiHours, ntiPart2Hours, comps, projects, certs, compare, migrations).
- **Derived:** `byId`, `dependents`, `projByComp`, `isBlocked(id)` = not done and any prerequisite not done.
- **Views:** flow, roadmap (stage map), kanban, checklist, paths, compare, projects, certs, dash. Graph views
  share selection, path filter, "locked only" and "all dependencies" toggles.
- **Re-render model:** state change → `save()` → `refreshAll()` (header, graph state, current view, open panel).
  Simple and fast enough for ~100 nodes.

## 4. Current persistence (v1.2)
- `localStorage["ntidebi-roadmap-v1"] = {status: {ID: "ns"|"ip"|"done"}, notes: {ID: text}, evidence: {ID: text},
  updated: {ID: ISO time}}`. Wrapped in try/catch; falls back to memory with a warning.
- Export: downloads the object as `roadmap-progress-YYYY-MM-DD.json`. Import: replaces the object if it has `status`.
  Reset: confirm, then clears.
- Weaknesses: no schema version, no data version, no migration, unknown IDs silently kept but invisible, import
  replaces without preview, per-origin storage (AUDIT A-05, A-06, A-07).

## 5. Recommended persistence design (for Stage 3; Claude Code may refine with reasons)
1. **Envelope:** `{app: "nti-debi-roadmap", storageVersion: 2, dataVersion, savedAt, progress: {ID: {status,
   notes, evidence, updated, level?, u?, e?, d?, link?}}, orphans: {…}, lastExportAt}`. Keep the same
   localStorage key family; migrate v1 → v2 on first load and keep a one-time copy under `…-v1-backup`.
2. **ID migrations on load:** apply `D.migrations` (chained), merging into the new ID (newer `updated` wins per
   field, notes concatenated). Unknown IDs go to `orphans`, shown on the dashboard with "reassign / delete".
   **Splits** (a list of new IDs) never copy a status, level or evidence to the parts, because a finished group
   doesn't prove each part (that would invent progress). The old entry goes to `orphans` with a "split into …"
   pointer so its notes can be reassigned by hand.
3. **Data-change summary:** remember the last seen `dataVersion` and ID set; on change, show "added / removed /
   renamed since your last visit".
4. **Export/import:** export the whole envelope; import validates the shape, shows a preview (counts, conflicts,
   orphans) and lets the owner choose **replace** or **merge**; always auto-export a backup before applying.
5. **Backups:** dashboard reminder when there are unsaved-to-file changes and the last export is older than 7 days;
   reset exports first.
6. **Origins:** on a fresh origin with empty storage, offer "Import progress from a file" (file:// ↔ Pages).
7. **Progress seed (decided, AUDIT D-06):** re-importable seed produced locally by `tools/seed_from_records.py`
   from the records snapshot in `private/progress/`. On import, the records own `level`, `u`/`e`/`d` and
   `lastVerified`; the app owns status, notes and link. Always a preview first. The seed never sets "done".
8. **Never** send progress anywhere. GitHub Pages hosts code only.

## 6. Known technical debt
See AUDIT A-08 … A-11. The single-file template is acceptable at this size; split into source modules only with
a reason, and keep one output file.
