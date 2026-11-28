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
| `roadmap.json` | `schemaVersion` (data schema, int), `dataVersion` (content version string), `stages[]` {id, n, name, window, gate, due}, `groups[]` {id, name, members[]} (flowchart clusters, D-04), `lanes[]` {id, name}, `sources` {NTI, DEBI, IND, SHARED, EXIST → label}, `paths[]` {id, name, rec, entry, why}, `ntiHours`, `ntiPart2Hours` |
| `competencies.json` | Array, **in roadmap order** (this order is the learning sequence shown in the checklist and in ROADMAP.md) |
| `projects.json` | PS-1 … PS-8 {id, name, stage, doc19, window, comps[], arch, steps[], goal, deliv, value} |
| `certifications.json` | {id, name, when, start "YYYY-MM", end, status, cost, fills, verdict, comps[]} |
| `comparison.json` | NTI vs DEBI rows {area, nti, debi, cls, lead, action} |
| `timetable.enc.json` | Optional. The owner's timetable as AES-256-GCM ciphertext {v, kdf, iter, cipher, salt, iv, ct}; written by the app's encrypt panel, validated as ciphertext by `validate.py` (AUDIT D-10) |
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

## 3. App structure (`app/template.html`, ~1,700 lines; UX redesign 28 Nov 2026)
Sections, in file order: CSS (Wayfind tokens in `:root`, a `night` colourway for dark mode, lane line colours
`--line-*`) → HTML shell (top bar with the three destinations, `#notice`, one `<section>` per destination, the
`#panel` drawer, `#dlg`) → script: storage · helpers · map graph (`Viewer` zoom/pan, `drawNode`, `drawEdges`,
`drawFlow`) · view state and URL routing · session log · Today · Roadmap lenses (List, Board, Route, Map) ·
drawer (Track | Learn, stage and group panels) · Plan sections · Data · orphans, notices, import · lateness ·
timetable · search, keyboard, colour mode, start.

- **Destinations:** Today (`#v-today`, landing), Roadmap (`#v-roadmap` with lenses `#v-checklist` List,
  `#v-kanban` Board, `#v-route` Route, `#v-flow` Map), Plan (`#v-plan` with `#v-paths`, `#v-projects`,
  `#v-certs`, `#v-compare`, `#v-time`, `#v-skills`) and Data (`#v-data`: export, import, reset, orphans, mode).
  On a phone (≤ 760 px) the destinations move to a bottom bar and the drawer fills the screen.
- **URL:** `#NET-3` opens a competency (as before; the drawer's open state replaces the hash and restores the
  view's hash on close). Views: `#today`, `#roadmap/<lens>?stage=&path=&status=&src=&q=`, `#roadmap/route/<ID>`,
  `#plan/<section>`, `#data`. Filters are one shared set (`F`) for every lens; changing them replaces the hash,
  moving between views pushes it, so Back works. `hashchange` and `popstate` both route through `onHash()`.
- **Global data:** `const D = /*DATA*/` (build payload: version, schemaVersion, stages, lanes, sources, paths,
  ntiHours, ntiPart2Hours, comps, projects, certs, compare, migrations, timetable).
- **Derived:** `byId`, `dependents`, `projByComp`, `isBlocked(id)`, `stateOf(id)` (ready, locked, ip, done),
  `nextUp()` (ready, earliest stage, highest priority).
- **Route lens:** the selected competency, its prerequisites one and two steps back and what it unlocks one and
  two steps ahead, as HTML "stations" with the connecting lines drawn in an SVG overlay after layout.
- **Map lens:** the former flowchart (longest-path depth columns + barycenter ordering, group clusters per
  D-04, the ongoing JOB band). The former stage map is retired; its content lives in the List's stage headers.
- **Re-render model:** state change → `save()` → `refreshAll()` (notices, header, map state, current view, open
  drawer). Simple and fast enough for ~100 competencies.
- **Font:** Chivo Mono (SIL OFL, `app/fonts/`), inlined by `tools/build.py` as base64.

## 4. Current persistence (v1.2)
- `localStorage["ntidebi-roadmap-v1"] = {status: {ID: "ns"|"ip"|"done"}, notes: {ID: text}, evidence: {ID: text},
  updated: {ID: ISO time}}`. Wrapped in try/catch; falls back to memory with a warning.
- Export: downloads the object as `roadmap-progress-YYYY-MM-DD.json`. Import: replaces the object if it has `status`.
  Reset: confirm, then clears.
- Weaknesses: no schema version, no data version, no migration, unknown IDs silently kept but invisible, import
  replaces without preview, per-origin storage (AUDIT A-05, A-06, A-07).

## 5. Persistence design (implemented in Stage 3, data 1.3)
1. **Envelope:** `{app: "nti-debi-roadmap", storageVersion: 2, dataVersion, savedAt, progress: {ID: {status,
   notes, evidence, updated, level?, u?, e?, d?, link?, log?}}, orphans: {…}, lastExportAt}`. `log` (added 28 Nov
   2026, still storage version 2) is the session log, newest first: `[{d: "YYYY-MM-DD", min?, text?, lv?}]`, at
   most 1,000 entries, only ever typed by the owner. Logging never sets a status unless the owner ticks "Also
   mark in progress"; `lv` also sets `level`. Merges keep the sessions of both sides once each. Builds before
   this one drop `log` on import (`cleanEntry` allowlist), so import an export into this build or later. Keep the same
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
8. **Progress leaves the browser only through opt-in sync** (§5a, AUDIT D-11). GitHub Pages hosts code only.

**As implemented (Stage 3):** keys `ntidebi-roadmap-v2` (envelope), `ntidebi-roadmap-v1` (left untouched),
`ntidebi-roadmap-v1-backup` (one-time copy) and `ntidebi-roadmap-v2-prev` (state before the last import or reset).
Every entry passes `cleanEntry` (allowlisted statuses, levels and marks; strings only, length-capped), so a
crafted file can't inject markup. The envelope keeps `seen` (data version + ID list) for the change notice.
Lateness (AUDIT D-10) reads `due` on stages and projects (YYYY-MM-DD, null = no window) and `end` on certs.
Tests: `tests/e2e_persistence.py` (rename, remove and add survive an update; v1 migration; seed; import on a
fresh origin) and `tests/upgrade_demo.py` (export from the data 1.2 build, upgrade, import, nothing lost).

## 5a. Sync across devices (28 Nov 2026, AUDIT D-11)
Opt-in, off by default; with it off the app makes no network request. The owner pastes a fine-grained GitHub token
(only *Gists: read and write*) on the Data page.
- **Keys:** `ntidebi-sync` = `{token, gistId, lastSyncAt, lastError}`; `ntidebi-sync-base` = the `{progress,
  orphans}` last agreed with the gist. Neither is part of the envelope, so exports never carry the token.
- **Gist:** secret (`public: false`), one file `ntidebi-roadmap-progress.json` holding the whole v2 envelope.
  Connect lists the account's gists and reuses the one with that file, otherwise creates it from this browser.
- **Sync = pull, merge, push.** The pulled file goes through `parseAny` and `normalize` like an import (so old IDs
  migrate and crafted content is cleaned). If it isn't a v2 envelope, nothing is pushed. `merge3(base, local,
  remote)` per entry: the side that changed wins; if both changed, per field: the changed side wins, a deleted vs.
  edited field keeps the edit, differing notes/evidence are joined, anything else takes the newer `updated`.
  Sessions merge as a set, and a session removed on either side stays removed. Push only when the result differs
  from the gist, then store the result as the new base.
- **When:** on load, 2.5 s after the last `touch()`, when the tab becomes visible (if the last sync is older than 20 s),
  on hiding with changes pending, and on `online` after an error. A remote change redraws without re-rendering a
  drawer field that has focus.
- The app also calls `navigator.storage.persist()` so the browser doesn't evict progress.
- Tests: `tests/e2e_sync.py` fakes the Gists API with Playwright routing.

## 6. Known technical debt
See AUDIT A-08 … A-11. The single-file template is acceptable at this size; split into source modules only with
a reason, and keep one output file.
