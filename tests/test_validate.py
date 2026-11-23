"""Unit tests for tools/validate.py. Run: python3 -m pytest tests/  (or: python3 tests/test_validate.py)"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from validate import load_all, validate  # noqa: E402

BASE = load_all()


def errs_after(mutate):
    d = copy.deepcopy(BASE)
    mutate(d)
    return validate(d)


def test_current_data_is_valid():
    assert validate(copy.deepcopy(BASE)) == []


def test_duplicate_id_rejected():
    assert any("duplicate" in e for e in errs_after(lambda d: d["comps"].append(copy.deepcopy(d["comps"][0]))))


def test_missing_prerequisite_rejected():
    def m(d):
        d["comps"][1]["pre"] = ["NOPE-1"]
    assert any("does not exist" in e for e in errs_after(m))


def test_forward_stage_prerequisite_rejected():
    def m(d):
        first = d["comps"][0]                                   # a Foundation competency
        last = next(c for c in d["comps"] if c["stage"] == "CSS")
        first["pre"] = [last["id"]]
    assert any("later stage" in e for e in errs_after(m))


def test_cycle_rejected():
    def m(d):
        by = {c["id"]: c for c in d["comps"]}
        by["NET-1"]["pre"] = ["NET-2"]                        # NET-2 already needs NET-1
    assert any("cycle" in e for e in errs_after(m))


def test_unknown_project_reference_rejected():
    assert any("unknown competency" in e for e in errs_after(lambda d: d["projects"][0]["comps"].append("NOPE-9")))


def test_migration_to_missing_id_rejected():
    assert any("does not exist" in e for e in errs_after(lambda d: d["migrations"].update({"OLD-1": "NOPE-2"})))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
