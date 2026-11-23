# DEPLOYMENT — GitHub Pages plan (nothing published yet)

**Nothing in this file has been executed.** Steps marked 🛑 need the owner's explicit approval in the Claude Code
session (`private/docs/CLAUDE_CODE_HANDOFF.md` Gate 5).

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

## GitHub setup (🛑 each step needs approval)
1. 🛑 Create the repo (`gh repo create <name> --public|--private --source . --remote origin`), or the owner creates it
   in the web UI.
2. ✅ Workflow moved to `.github/workflows/deploy-pages.yml` (Stage 5, approved); action versions current on 23 Nov 2026.
3. 🛑 First push: `git push -u origin main`.
4. 🛑 Repo Settings → Pages → Source: **GitHub Actions**.
5. Confirm the workflow run passes and the site loads at `https://<user>.github.io/<repo>/`.
6. Confirm a progress export from the local file imports on the Pages site (AUDIT A-05).

## Rollback
Revert the commit and push (the workflow redeploys), or disable Pages in Settings. Progress is unaffected (it lives
in browsers and export files).
