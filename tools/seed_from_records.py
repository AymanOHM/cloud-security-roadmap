#!/usr/bin/env python3
"""Turn a Study Plan records snapshot into a progress seed the app can import (AUDIT D-06).

Reads the "Competency tracker" table of a snapshot such as
private/progress/records-tracker-snapshot-2026-11-23.md and writes a seed JSON:

  {"kind": "roadmap-progress-seed", "seedVersion": 1, "snapshotDate": "...", "source": "...",
   "entries": {"NET-1": {"level": "E1", "levelNote": "needs verification", "u": "partial"}, ...}}

What is copied: evidence level (E0–E4), its qualifier, the U/E/D marks and the last-verified date.
What is not: statuses (the seed never marks anything Completed), the Evidence and Notes columns (raw
handoff IDs and diagnostics stay in the records), and the CV-defense rows (D-08).
Every tracker row becomes an entry, even an empty one, so a re-import clears what the records no
longer show. Ranges such as "DB-2 … DB-6" are expanded.

The seed is personal: it is written under private/ by default and is gitignored.

Usage: python3 tools/seed_from_records.py [SNAPSHOT.md] [--out FILE]
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "private" / "progress"
MARKS = {"⚪": "none", "🟡": "partial", "🟢": "verified", "🔴": "regressed"}
ID_RE = re.compile(r"^[A-Z]+-\d+$")
RANGE_RE = re.compile(r"^([A-Z]+)-(\d+)\s*(?:…|\.\.\.|–|-)\s*\1-(\d+)$")


def mark(cell):
    for sym, name in MARKS.items():
        if sym in cell:
            return name
    return None


def parse_level(cell):
    """'E3 (partial; not the exit check)' -> ('E3', 'partial; not the exit check'); '⚪' -> (None, None)."""
    m = re.search(r"\bE([0-4])\b", cell)
    note = re.search(r"\(([^)]*)\)", cell)
    return (f"E{m.group(1)}" if m else None), (note.group(1).strip()[:120] if note else None)


def expand(cell):
    cell = cell.strip()
    if ID_RE.match(cell):
        return [cell]
    m = RANGE_RE.match(cell)
    if m and int(m.group(2)) <= int(m.group(3)):
        return [f"{m.group(1)}-{n}" for n in range(int(m.group(2)), int(m.group(3)) + 1)]
    return []


def parse_snapshot(text):
    """Return {id: entry} from the competency tracker table only."""
    entries = {}
    in_tracker = False
    for line in text.splitlines():
        if line.startswith("#"):
            in_tracker = "competency tracker" in line.lower()
            continue
        if not in_tracker or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] in ("ID", "") or set(cells[0]) <= set("-: "):
            continue
        ids = expand(cells[0])
        if not ids:
            continue
        level, note = parse_level(cells[1])
        e = {}
        if level:
            e["level"] = level
        if note:
            e["levelNote"] = note
        for key, cell in zip(("u", "e", "d"), cells[2:5]):
            m = mark(cell)
            if m:
                e[key] = m
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[5]):
            e["lastVerified"] = cells[5]
        for i in ids:
            entries[i] = dict(e)
    return entries


def latest_snapshot():
    snaps = sorted(PROGRESS.glob("records-tracker-snapshot-*.md"))
    return snaps[-1] if snaps else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("snapshot", nargs="?", help="records snapshot (default: newest in private/progress/)")
    ap.add_argument("--out", help="output file (default: private/progress/roadmap-progress-seed-<date>.json)")
    args = ap.parse_args(argv)
    src = Path(args.snapshot) if args.snapshot else latest_snapshot()
    if not src or not src.exists():
        print("No records snapshot found (expected private/progress/records-tracker-snapshot-YYYY-MM-DD.md)")
        return 1
    entries = parse_snapshot(src.read_text(encoding="utf-8"))
    if not entries:
        print(f"No competency tracker rows found in {src}")
        return 1
    m = re.search(r"(\d{4}-\d{2}-\d{2})", src.name)
    date = m.group(1) if m else ""
    seed = {"kind": "roadmap-progress-seed", "seedVersion": 1, "snapshotDate": date,
            "source": f"Study Plan records snapshot {src.name}",
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "entries": entries}
    out = Path(args.out) if args.out else PROGRESS / f"roadmap-progress-seed-{date or 'undated'}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(seed, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    sys.path.insert(0, str(ROOT / "tools"))
    from validate import load_all  # noqa: E402
    d = load_all()
    known = {c["id"] for c in d["comps"]} | set(d["migrations"])
    skipped = sorted(i for i in entries if i not in known)
    levels = sum(1 for e in entries.values() if "level" in e)
    print(f"wrote {out} ({len(entries)} entries, {levels} with a level)")
    if skipped:
        print(f"not in the roadmap, skipped by the app: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
