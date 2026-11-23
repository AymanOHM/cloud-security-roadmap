#!/usr/bin/env python3
"""Validate the roadmap data in data/*.json. Exit code 1 on any error.

Checks: required fields, allowed enum values, unique IDs, every reference resolves
(prerequisites, projects, certifications, paths, migrations), prerequisites never
point to a later stage, and the prerequisite graph has no cycles.

Usage: python3 tools/validate.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

REQUIRED_COMP = ["id", "name", "stage", "lane", "src", "desc", "why", "obj", "pre", "nti", "debi",
                 "res", "labs", "ev", "hours", "pri", "existing", "paths"]
PRI = {"H", "M", "L"}
EXISTING = {None, "have", "refresh"}


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


def validate(d):
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
    for old, new in d["migrations"].items():
        if old in by:
            errors.append(f"migration: retired id {old} is still in use")
        if new not in by:
            errors.append(f"migration: {old} -> {new}, but {new} does not exist")
    return errors


if __name__ == "__main__":
    d = load_all()
    errs = validate(d)
    if errs:
        print(f"{len(errs)} error(s):")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"OK: {len(d['comps'])} competencies, {len(d['projects'])} projects, "
          f"{len(d['certs'])} certifications, data version {d['meta']['dataVersion']}")
