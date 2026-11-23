# DEPLOYMENT — GitHub Pages

**Deployed 23 Nov 2026** after the owner's Gate 5 approval: repo https://github.com/AymanOHM/cloud-security-roadmap
(public), site https://aymanohm.github.io/cloud-security-roadmap/. Every push to `main` redeploys through the workflow.

## Decisions (AUDIT D-05, D-10; Gate 1 and Stage 5)
- Repo: **`cloud-security-roadmap`**, **public**, under the owner's account (GitHub Free serves Pages only from public
  repos; the Pages site is public on any plan). Every committed file is public.
- Public: app, `data/` (incl. the encrypted timetable), `tools/`, `tests/`, `development/`, `maintenance/`,
  `curriculum/`, `ROADMAP.md`, `README.md`, `CLAUDE.md`. Personal and meta docs live in `private/` (gitignored).
- Commit author email: the owner's GitHub no-reply address (history rewritten 23 Nov 2026 before any push).
- Workflow: `.github/workflows/deploy-pages.yml` (activated in Stage 5; action versions checked 23 Nov 2026).

## Pre-publish checklist (all must pass before 🛑 Gate 5)
- [ ] `git check-ignore -v private/ archive/ dist/ build/` lists all four
- [ ] `git ls-files | grep -iE "private/|archive/|\.pdf$|progress.*\.json"` returns nothing
- [ ] `python3 tools/validate.py` passes **with** `private/privacy-terms.txt` present (privacy lint over `data/` and every public file; AUDIT P-01, A-21). CI runs it without the terms file, so the name check only happens locally
- [ ] No NTI course material anywhere (module names and hours only) (AUDIT P-04)
- [ ] No personal schedule, names of private individuals, or contact details in committed files (AUDIT P-02). The only exception is the encrypted timetable blob (AUDIT D-10): confirm it's ciphertext, not plain text
- [ ] Also scan history, not just the tree: `git log -p | grep -nE "H-20[0-9]{6}-[0-9]"` returns nothing
- [ ] No secrets: `git grep -nE "(api[_-]?key|token|password)\s*[:=]"` reviewed
- [ ] validate, unit tests, build and smoke test pass locally
- [ ] The owner has read the final file list (`git ls-files`)

### Results, 23 Nov 2026 (Stage 5)
| Check | Result |
|---|---|
| `private/`, `archive/`, `dist/`, `build/` ignored | ✅ all four |
| No tracked private, archive, PDF or progress files | ✅ 0 of 34 tracked files |
| `validate.py` with private terms | ✅ passes (data, 34 public files, timetable is ciphertext) |
| NTI course material | ✅ none: module names, hours, terms and the owner's own rating only |
| Personal data in the tree | ✅ none besides the encrypted timetable; owner name appears only as the GitHub handle |
| History (every commit): record IDs, private terms, timetable text, personal email | ✅ 0 hits; author email rewritten to the GitHub no-reply address |
| Secrets | ✅ none (`id-token: write` is a workflow permission) |
| CI dry run in a clean clone without `private/` | ✅ validate, docgen check, 24 unit tests, build, smoke, persistence and UI tests |
| Owner has read the file list | ✅ approved at Gate 5 |

## GitHub setup (🛑 each step needs approval)
1. ✅ Repo created: `gh repo create AymanOHM/cloud-security-roadmap --public --source . --remote origin`.
2. ✅ Workflow moved to `.github/workflows/deploy-pages.yml` (Stage 5, approved); action versions current on 23 Nov 2026.
3. ✅ First push of `main` and the `v1.2-baseline` tag.
4. ✅ Pages source set to GitHub Actions (`gh api -X POST repos/AymanOHM/cloud-security-roadmap/pages -f build_type=workflow`).
5. ✅ First workflow run passed (build 54 s, deploy 10 s); the live page is byte-identical to the local build.
6. ✅ A progress export from `file://` imported on the Pages site (merge preview, status and notes kept).

## Rollback
Revert the commit and push (the workflow redeploys), or disable Pages in Settings. Progress is unaffected (it lives
in browsers and export files).
