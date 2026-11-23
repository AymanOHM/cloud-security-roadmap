# UPDATE_GUIDE — changing the roadmap without rebuilding the app

All roadmap content lives in `data/*.json`. The app is regenerated from it with one command; app code changes
only when the *kind* of information changes (a new field or view), not when content changes.

## The loop (every change)
1. **Export your progress first** (app → Dashboard → Export) and keep the file outside the repo.
2. Edit `data/*.json` (any editor; keep valid JSON).
3. `python3 tools/validate.py` → fix anything it reports.
4. `python3 tools/build.py` → open `dist/index.html` and look at what you changed.
5. `python3 tools/docgen.py --write` → regenerates the Phase 2, 4 and 5 tables in `ROADMAP.md`.
6. Bump `dataVersion` in `data/roadmap.json` and add a line to `maintenance/CHANGELOG.md`.
7. If the change reflects a study-plan decision, record the decision in the Study Plan Project too (it's the master
   for decisions).
8. Commit. Once deployment is set up, pushing to `main` redeploys automatically.

Claude Code can do steps 2–6 for you from a plain request ("DEBI assigned the Google course; update the DEBI
fields"). It must show you the data diff before committing.

## Common changes
| You want to… | Do this | Progress impact |
|---|---|---|
| **Add a competency** | Add an object to `competencies.json` at its place in the learning order. Give it a new, never-used ID. Fill every field (`null` where a source says nothing). Add it to projects/certs if relevant | None; it starts "Not started" |
| **Change objectives, resources, labs, evidence, NTI/DEBI text** | Edit the fields in place | None |
| **Change prerequisites** | Edit `pre`. The validator blocks later-stage prerequisites and cycles | Some items may become locked or unlocked; statuses are kept |
| **Move a competency to another stage or lane** | Edit `stage`/`lane`; keep the ID | None |
| **Rename an ID** (avoid if you can) | Change the ID everywhere it's referenced, then add `"OLD": "NEW"` to `id-migrations.json` | Carried over automatically on the next load |
| **Retire a competency** | Remove it and its references; add `"OLD": "REPLACEMENT"` if something replaces it, or `"OLD": ["NEW-1", …]` if it splits | Without a replacement (or on a split) its progress becomes an orphan: kept and shown on the dashboard to move or delete |
| **Add or remove a project** | Edit `projects.json` (`comps` must exist) | None |
| **Update certifications** | Edit `certifications.json` (`start`/`end` as `YYYY-MM`) | None |
| **Update the NTI vs DEBI matrix** | Edit `comparison.json`; keep `cls` starting with Duplicate / Complementary / NTI exclusive / DEBI exclusive / Missing (the app colours by prefix) | None |
| **Reconcile a curriculum change** (e.g. DEBI publishes its course list, NTI changes a module) | Update `curriculum/NTI.md` or `DEBI.md` with the fact and its source; update the `nti`/`debi` fields of affected competencies, changing "(unverified)" to "(verified, <source>)"; update `comparison.json` and `ntiHours`; re-check `src` (lead source) for affected competencies | None |
| **Record your progress** | In the app. Export after meaningful changes | — |
| **Refresh evidence levels from the records** | Update the snapshot in `private/progress/`, run `python3 tools/seed_from_records.py`, then Dashboard → Import → the seed file. Preview first; statuses, notes and links are untouched | Records own level, U/E/D, last verified |
| **Update your timetable** | App → Timetable → unlock → "Create or replace" (prefilled) → Encrypt → save as `data/timetable.enc.json`, rebuild, commit. Plain text never goes in the repo | None |
| **Group or ungroup competencies in the flowchart** | Edit `groups` in `roadmap.json` (members must exist, one group each) | None |
| **Change a window (stage, project, cert)** | Edit `window` (text) and `due` (YYYY-MM-DD) in `roadmap.json`/`projects.json`, or `start`/`end` in `certifications.json` | The "late" badges follow |
| **Record a decision** | Study Plan Project first; then mirror it in `private/docs/STUDY_PLAN.md` §5 and, if it changes content, in `data/` | — |

## Rules that keep progress safe
- IDs are permanent. Never reuse a retired ID for something else.
- Never edit `dist/` by hand.
- Don't put personal progress or record IDs in `data/` (it's public once deployed).
- Every release that changes the stored-progress format needs a tested migration (see `development/ARCHITECTURE.md` §5).

## Versioning
`dataVersion` = `MAJOR.MINOR · date`. MINOR for content edits and additions; MAJOR when IDs are renamed/removed or the
structure changes (stages, lanes, paths). The app's storage version is separate and only changes with app code.
