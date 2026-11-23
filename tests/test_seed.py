"""Unit tests for tools/seed_from_records.py (synthetic snapshot; no real records)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from seed_from_records import main, parse_snapshot  # noqa: E402

REC = "H-" + "20990101" + "-1"   # assembled so this file holds no literal record ID
SNAP = f"""# Competency tracker snapshot

| ID | Level (E0–E4) | U | E | D | Last verified | Evidence | Notes |
|---|---|---|---|---|---|---|---|
| NET-1 | E1 (needs verification) | 🟡 | – | – | – | {REC} | private diagnostic text |
| NET-2 | E3 (partial; not the exit check) | – | 🟢 | 🔴 | 2026-11-01 | {REC} | |
| LNX-5 | ⚪ (diagnosed; below 🟡) | – | – | – | – | {REC} | logs not read |
| DB-2 … DB-4 | ⚪ | – | – | – | – | | |

## CV-defense rows (doc 02)
| Item | Level | U | E | D | Evidence | Notes |
|---|---|---|---|---|---|---|
| CV-1 Something | 🟡 | 🟡 | – | – | {REC} | weak |
"""


def test_levels_marks_and_dates():
    e = parse_snapshot(SNAP)
    assert e["NET-1"] == {"level": "E1", "levelNote": "needs verification", "u": "partial"}
    assert e["NET-2"] == {"level": "E3", "levelNote": "partial; not the exit check", "e": "verified",
                          "d": "regressed", "lastVerified": "2026-11-01"}
    assert e["LNX-5"] == {"levelNote": "diagnosed; below 🟡"}


def test_ranges_expand_to_empty_entries():
    e = parse_snapshot(SNAP)
    assert e["DB-2"] == e["DB-3"] == e["DB-4"] == {}


def test_cv_rows_and_private_columns_are_not_copied(tmp_path):
    snap = tmp_path / "records-tracker-snapshot-2099-01-01.md"
    snap.write_text(SNAP, encoding="utf-8")
    out = tmp_path / "seed.json"
    assert main([str(snap), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    seed = json.loads(text)
    assert seed["kind"] == "roadmap-progress-seed" and seed["snapshotDate"] == "2099-01-01"
    assert not any(k.startswith("CV") for k in seed["entries"])
    assert REC not in text and "diagnostic" not in text and "logs not read" not in text
    assert not any("status" in v for v in seed["entries"].values())
