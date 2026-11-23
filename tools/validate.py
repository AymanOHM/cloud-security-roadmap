#!/usr/bin/env python3
"""Validate the roadmap data in data/*.json. Exit code 1 on any error.

Checks: required fields, allowed enum values, unique IDs, every reference resolves
(prerequisites, projects, certifications, paths, migrations), prerequisites never
point to a later stage, the prerequisite graph has no cycles, `core` is exclusive
of career-path tags, and the privacy lint (no learning-record notes, evidence-level
status or private terms in data/ or the public docs).

Private terms (e.g. the owner's name) are read from private/privacy-terms.txt, one per
line, when that file exists, so the terms themselves never enter the public repo.

Usage: python3 tools/validate.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

REQUIRED_COMP = ["id", "name", "stage", "lane", "src", "desc", "why", "obj", "pre", "nti", "debi",
                 "res", "labs", "ev", "hours", "pri", "existing", "paths"]
PRI = {"H", "M", "L"}
EXISTING = {None, "have", "refresh"}

# Privacy lint (AUDIT P-01, A-21). A record ID looks like H-, an 8-digit date and a sequence number.
RECORD_ID = re.compile(r"\bH-20\d{6}-\d+\b")
RECORDS_NOTE = re.compile(r"\brecords?\s*(:|show)", re.I)
# `ev` defines what proves mastery; it must not report a current level or status.
EV_STATUS = re.compile(r"\bE[0-4]\b|[\u26aa\U0001f7e1\U0001f7e2\U0001f534]|\bpartial\b", re.I)
TERMS_FILE = ROOT / "private" / "privacy-terms.txt"
PUBLIC_SKIP = {"private", "archive", "dist", "build", ".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
PUBLIC_EXT = {".md", ".json", ".html", ".py", ".yml", ".yaml", ".draft", ".txt", ".js", ".css"}


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


def load_all():
    meta = load("roadmap.json")
    return {
        "meta": meta,
        "comps": load("competencies.json"),
        "projects": load("projects.json"),
        "certs": load("certifications.json"),
        "compare": load("comparison.json"),
        "migrations": load("id-migrations.json").get("migrations", {}),
    }


def private_terms(path=TERMS_FILE):
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]


def _strings(obj, where):
    if isinstance(obj, str):
        yield where, obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _strings(v, f"{where}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, f"{where}.{k}")


def privacy_errors(d, terms=()):
    """Lint every string in the data for personal record notes and private terms."""
    errors = []
    term_res = [re.compile(re.escape(t), re.I) for t in terms]
    for key in ("meta", "comps", "projects", "certs", "compare", "migrations"):
        for where, s in _strings(d[key], key):
            if RECORD_ID.search(s):
                errors.append(f"privacy: record ID in {where}")
            if RECORDS_NOTE.search(s):
                errors.append(f"privacy: records note in {where}")
            if any(r.search(s) for r in term_res):
                errors.append(f"privacy: private term in {where}")
    for c in d["comps"]:
        if isinstance(c.get("ev"), str) and EV_STATUS.search(c["ev"]):
            errors.append(f"{c.get('id', '?')}: 'ev' must define evidence of mastery, not report a level or status")
    return errors


def public_files(root=ROOT):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in PUBLIC_SKIP for part in rel.parts) or not p.is_file() or p.suffix not in PUBLIC_EXT:
            continue
        yield p


def privacy_scan_files(root=ROOT, terms=()):
    """Scan the files that would be published for record IDs and private terms."""
    errors = []
    term_res = [re.compile(re.escape(t), re.I) for t in terms]
    for p in public_files(root):
        text = p.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if RECORD_ID.search(line):
                errors.append(f"privacy: record ID in {p.relative_to(root)}:{n}")
            if any(r.search(line) for r in term_res):
                errors.append(f"privacy: private term in {p.relative_to(root)}:{n}")
    return errors


def validate(d, terms=()):
    errors = []
    meta, comps = d["meta"], d["comps"]
    stage_ids = [s["id"] for s in meta["stages"]]
    stage_order = {s: i for i, s in enumerate(stage_ids)}
    lane_ids = {l["id"] for l in meta["lanes"]}
    src_ids = set(meta["sources"])
    path_ids = {p["id"] for p in meta["paths"]}

    ids = [c.get("id") for c in comps]
    seen = set()
    for i in ids:
        if i in seen:
            errors.append(f"duplicate competency id {i}")
        seen.add(i)
    by = {c["id"]: c for c in comps if "id" in c}

    for c in comps:
        cid = c.get("id", "?")
        for k in REQUIRED_COMP:
            if k not in c:
                errors.append(f"{cid}: missing field '{k}'")
        if c.get("stage") not in stage_order:
            errors.append(f"{cid}: unknown stage {c.get('stage')}")
        if c.get("lane") not in lane_ids:
            errors.append(f"{cid}: unknown lane {c.get('lane')}")
        if c.get("src") not in src_ids:
            errors.append(f"{cid}: unknown source {c.get('src')}")
        if c.get("pri") not in PRI:
            errors.append(f"{cid}: priority must be H/M/L")
        if c.get("existing") not in EXISTING:
            errors.append(f"{cid}: existing must be null, 'have' or 'refresh'")
        for p in c.get("paths", []):
            if p != "core" and p not in path_ids:
                errors.append(f"{cid}: unknown path {p}")
        if "core" in c.get("paths", []) and len(c["paths"]) > 1:
            errors.append(f"{cid}: 'core' is exclusive; drop the path tags {[p for p in c['paths'] if p != 'core']}")
        if not c.get("paths"):
            errors.append(f"{cid}: needs at least one path tag ('core' or a career path)")
        for p in c.get("pre", []):
            if p not in by:
                errors.append(f"{cid}: prerequisite {p} does not exist")
            elif stage_order[by[p]["stage"]] > stage_order.get(c.get("stage"), 0):
                errors.append(f"{cid}: prerequisite {p} is in a later stage")
        for k in ("obj", "res", "labs"):
            if not isinstance(c.get(k), list):
                errors.append(f"{cid}: '{k}' must be a list")

    # cycle check
    state = {}

    def visit(n, stack):
        if state.get(n) == 1:
            errors.append("prerequisite cycle: " + " -> ".join(stack + [n]))
            return
        if state.get(n) == 2:
            return
        state[n] = 1
        for p in by[n]["pre"]:
            if p in by:
                visit(p, stack + [n])
        state[n] = 2
    for n in by:
        visit(n, [])

    for p in d["projects"]:
        for cid in p.get("comps", []):
            if cid not in by:
                errors.append(f"project {p['id']}: unknown competency {cid}")
        if p.get("stage") not in stage_order:
            errors.append(f"project {p['id']}: unknown stage {p.get('stage')}")
    for k in d["certs"]:
        for cid in k.get("comps", []):
            if cid not in by:
                errors.append(f"cert {k['id']}: unknown competency {cid}")
    # A migration is a rename ("OLD": "NEW") or a split ("OLD": ["NEW-1", "NEW-2", ...]).
    for old, new in d["migrations"].items():
        if old in by:
            errors.append(f"migration: retired id {old} is still in use")
        targets = new if isinstance(new, list) else [new]
        if not targets or not all(isinstance(x, str) for x in targets):
            errors.append(f"migration: {old} must map to an ID or a non-empty list of IDs")
            continue
        for x in targets:
            if x not in by:
                errors.append(f"migration: {old} -> {x}, but {x} does not exist")
    errors += privacy_errors(d, terms)
    return errors


if __name__ == "__main__":
    d = load_all()
    terms = private_terms()
    errs = validate(d, terms) + privacy_scan_files(ROOT, terms)
    if errs:
        print(f"{len(errs)} error(s):")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"OK: {len(d['comps'])} competencies, {len(d['projects'])} projects, "
          f"{len(d['certs'])} certifications, data version {d['meta']['dataVersion']}"
          + ("" if TERMS_FILE.exists() else " (no private/privacy-terms.txt: private-term lint skipped)"))
