#!/usr/bin/env python3
"""Generate the data-driven sections of ROADMAP.md (Phase 2, 4 and 5) from data/*.json.

Always writes the fragments to build/docgen/ (gitignored).
  --write   also replace those sections in ROADMAP.md
  --check   exit 1 if ROADMAP.md differs from the data (for CI)
The other sections of ROADMAP.md are hand-written prose and are not generated.

Usage: python3 tools/docgen.py [--write | --check]
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import load_all, ROOT  # noqa: E402

_d = load_all()
d = dict(stages=_d["meta"]["stages"], comps=_d["comps"], projects=_d["projects"], compare=_d["compare"])
by = {c["id"]: c for c in d["comps"]}
SRC = {"NTI": "NTI", "DEBI": "DEBI", "IND": "Independent", "SHARED": "Shared", "EXIST": "Existing"}
PRI = {"H": "High", "M": "Medium", "L": "Low"}


def ids(lst):
    """Join IDs, compressing runs like PY-1, PY-2, PY-3 into PY-1–3."""
    out, i = [], 0
    while i < len(lst):
        pre, _, n = lst[i].rpartition("-")
        j = i
        while (n.isdigit() and j + 1 < len(lst) and lst[j + 1].rpartition("-")[0] == pre
               and lst[j + 1].rpartition("-")[2] == str(int(n) + (j + 1 - i))):
            j += 1
        out.append(f"{lst[i]}–{lst[j].rpartition('-')[2]}" if j - i >= 2 else ", ".join(lst[i:j + 1]))
        i = j + 1
    return ", ".join(out)


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ")


out = {}

# ---------------- Phase 2
cls = Counter(r["cls"].split(" (")[0] for r in d["compare"])
rows = "\n".join(f"| {cell(r['area'])} | {cell(r['nti'])} | {cell(r['debi'])} | {cell(r['cls'])} | {cell(r['lead'])} | {cell(r['action'])} |" for r in d["compare"])
out["phase2"] = f"""## Phase 2 — Overlap and gap matrix

NTI is a full DevOps curriculum (420 h) with thin security. DEBI supplies the security fundamentals NTI lacks. Neither teaches AWS security services, so that part is independent work. Of {len(d['compare'])} areas: {cls['Duplicate']} duplicate, {cls['Complementary']} complementary, {cls['NTI exclusive']} NTI-exclusive, {cls['DEBI exclusive']} DEBI-exclusive, {cls['Missing']} missing from both.

NTI hours are from doc 19 §C. DEBI entries marked \"unverified\" depend on the assigned course list, which hasn't been published.

| Area | NTI | DEBI | Class | Lead | What to do |
| --- | --- | --- | --- | --- | --- |
{rows}

Overlap only costs you time twice in networking, Python, Linux, security operations and AppSec. In each, one program leads and the other's version is revision at most."""

# ---------------- Phase 4
_cnt = Counter(c["stage"] for c in d["comps"]); _t = len(d["comps"])
core = round(100*(_cnt["FND"]+_cnt["CDE"]+_cnt["SEN"])/_t); spec = round(100*_cnt["CSS"]/_t); job = 100-core-spec
parts = [f"""## Phase 4 — Unified roadmap

There are five stages, each closed by a gate that needs evidence. Finishing a course doesn't pass a gate. **Every competency has an ID.** The IDs reuse the Study Plan's doc 06 scheme (NET, LNX, PY, DB, WEB, GIT, TST, CI, CTR, SEC, APPSEC, WIN, CLD, OPS, COMM, DSA), so your records (doc 15) track the same rows. New IDs cover the cloud-security part: IAC, K8S, DSO, VM, NSEC, LOG, IR, TM, CSEC, JOB. The HTML dashboard uses exactly these IDs, in this order.

The split, counted by competencies: core (Stages 1–3) about {core}%, specialization (Stage 4) about {spec}%, job readiness and revision about {job}%. Core is above your 60–70% target because NTI's 420 h *is* the core while it runs. Doc 19 §F already replaced the old split for that reason.

Source legend: **NTI** leads · **DEBI** leads · **Independent** · **Shared** (both cover it; the Lead column in Phase 2 decides) · **Existing** (you already have it; claim it with evidence instead of re-studying). \"Refresh\" in the Competency column means partly existing, per doc 19 and the records."""]
for s in d["stages"]:
    L = [c for c in d["comps"] if c["stage"] == s["id"]]
    rows = []
    for c in L:
        name = c["name"] + (f" ({c['existing']})" if c["existing"] else "")
        pre = ids(c["pre"]) or "—"
        obj = "; ".join(c["obj"])
        labs = "; ".join(c["labs"]) or "—"
        rows.append(f"| {c['id']} | {cell(name)} | {SRC[c['src']]} | {pre} | {cell(obj)} | {cell(labs)} | {cell(c['ev'])} | {PRI[c['pri']]} |")
    parts.append(f"""### Stage {s['n']} — {s['name']}

{s['window']}. **{s['gate']}**

| ID | Competency | Source | Prerequisites | Learning objectives | Practical work | Evidence | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(rows))
parts.append("""If you switch direction at the Stage 4 decision point, the core stays the same. SecOps leans on LOG-1, IR-1 and CSEC-3/4/7. Cloud infrastructure leans on K8S-1, IAC-3 and OPS-3/4. Each competency's path tags are in the HTML's Career paths view.""")
out["phase4"] = "\n\n".join(parts)

# ---------------- Phase 5
pp = ["""## Phase 5 — Project progression

One app (your graduation project) is built up in layers, so each stage deploys onto the previous one. PS-1 to PS-5 are doc 19 §G's project stages 1–5, unchanged. PS-7 adds the cloud-security layer after NTI. Every stage must stand on its own and be CV-ready when it's done (doc 19).

**Cost rule before PS-3:** set the budget alarm (CLD-1). NAT gateways, an EKS control plane and GuardDuty after its trial are where lab bills come from. Run Kubernetes locally."""]
for p in d["projects"]:
    pp.append(f"""### {p['id']} — {p['name']}

_{p['doc19'][0].upper()+p['doc19'][1:]} · {p['window']}_

- **Competencies:** {ids(p['comps'])}
- **Architecture:** {p['arch']}
- **Steps:** {' → '.join(p['steps'])}
- **Security goal:** {p['goal']}
- **Deliverables:** {p['deliv']}
- **Why it gets you hired:** {p['value']}""")
out["phase5"] = "\n\n".join(pp)

OUT = ROOT / "build" / "docgen"
OUT.mkdir(parents=True, exist_ok=True)
for k, v in out.items():
    (OUT / f"{k}.md").write_text(v, encoding="utf-8")
    print(f"wrote build/docgen/{k}.md ({len(v)} chars)")


def sync(text):
    """Return ROADMAP.md text with each generated section replaced (heading to next '## ')."""
    for v in out.values():
        heading = v.split("\n", 1)[0]
        start = text.index(heading)
        nxt = text.find("\n## ", start + len(heading))
        end = len(text) if nxt == -1 else nxt + 1
        text = text[:start] + v.rstrip() + "\n\n" + text[end:]
    return text


if "--write" in sys.argv or "--check" in sys.argv:
    rm = ROOT / "ROADMAP.md"
    cur = rm.read_text(encoding="utf-8")
    new = sync(cur)
    if "--check" in sys.argv:
        if new != cur:
            print("ROADMAP.md is out of date with data/: run python3 tools/docgen.py --write")
            sys.exit(1)
        print("ROADMAP.md matches data/")
    elif new != cur:
        rm.write_text(new, encoding="utf-8")
        print("updated ROADMAP.md (Phase 2, 4, 5)")
