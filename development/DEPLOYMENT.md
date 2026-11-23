# DEPLOYMENT — GitHub Pages plan (nothing published yet)

**Nothing in this file has been executed.** Steps marked 🛑 need the owner's explicit approval in the Claude Code
session (`private/docs/CLAUDE_CODE_HANDOFF.md` Gate 5).

## Decisions needed first (AUDIT D-05)
- Repo name (suggestion: `cloud-security-roadmap`) and owner account.
- Visibility. GitHub Pages from a **private** repo needs a paid plan (as far as known; **verify on GitHub's docs at
  deploy time**). On a free account the repo must be public, so every committed file is public.
- What is public: recommended = app, `data/`, `tools/`, `tests/`, `development/`, `maintenance/`, `curriculum/`,
  README; personal docs (`STUDY_PLAN.md` §5 details, ROADMAP.md Phase 7 schedule) generalised or moved to `private/`.

## Local repository (allowed after Gate 1)
```bash
git init -b main
git status --ignored        # private/, archive/, dist/, build/ must show as ignored
git add -A && git commit -m "Initial import of the NTI + DEBI roadmap (data v1.2)"
```

## Pre-publish checklist (all must pass before 🛑 Gate 5)
- [ ] `git check-ignore -v private/ archive/ dist/ build/` lists all four
- [ ] `git ls-files | grep -iE "private/|archive/|\.pdf$|progress.*\.json"` returns nothing
- [ ] `grep -rnE "H-20[0-9]{6}|Records:" data/` returns nothing (AUDIT P-01)
- [ ] No NTI course material anywhere (module names and hours only) (AUDIT P-04)
- [ ] No personal schedule, names of private individuals, or contact details in committed files (AUDIT P-02)
- [ ] No secrets: `git grep -nE "(api[_-]?key|token|password)\s*[:=]"` reviewed
- [ ] validate, unit tests, build and smoke test pass locally
- [ ] The owner has read the final file list (`git ls-files`)

## GitHub setup (🛑 each step needs approval)
1. 🛑 Create the repo (`gh repo create <name> --public|--private --source . --remote origin`), or the owner creates it
   in the web UI.
2. 🛑 Move `development/github-pages-workflow.yml.draft` to `.github/workflows/deploy-pages.yml`; check the action
   versions are current.
3. 🛑 First push: `git push -u origin main`.
4. 🛑 Repo Settings → Pages → Source: **GitHub Actions**.
5. Confirm the workflow run passes and the site loads at `https://<user>.github.io/<repo>/`.
6. Confirm a progress export from the local file imports on the Pages site (AUDIT A-05).

## Rollback
Revert the commit and push (the workflow redeploys), or disable Pages in Settings. Progress is unaffected (it lives
in browsers and export files).
