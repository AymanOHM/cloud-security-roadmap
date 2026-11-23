"""Unit tests for tools/validate.py. Run: python3 -m pytest tests/  (or: python3 tests/test_validate.py)"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from validate import load_all, validate, privacy_scan_files  # noqa: E402

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


# Record IDs are assembled at runtime so this file never contains one literally.
REC = "H-" + "20261012" + "-2"


def test_split_migration_accepted():
    def m(d):
        d["migrations"]["OLD-1–2"] = ["NET-1", "NET-2"]
    assert errs_after(m) == []


def test_split_migration_to_missing_id_rejected():
    assert any("does not exist" in e for e in errs_after(lambda d: d["migrations"].update({"OLD-1–2": ["NET-1", "NOPE-3"]})))


def test_empty_split_rejected():
    assert any("non-empty list" in e for e in errs_after(lambda d: d["migrations"].update({"OLD-1": []})))


def test_core_is_exclusive():
    def m(d):
        d["comps"][0]["paths"] = ["core", "DSO"]
    assert any("'core' is exclusive" in e for e in errs_after(m))


def test_missing_path_tag_rejected():
    def m(d):
        d["comps"][0]["paths"] = []
    assert any("at least one path tag" in e for e in errs_after(m))


def test_record_id_anywhere_in_data_rejected():
    def m(d):
        d["projects"][0]["arch"] += f" ({REC})"
    assert any("record ID" in e for e in errs_after(m))


def test_records_note_rejected():
    def m(d):
        d["comps"][3]["res"].append("Records show a gap here")
    assert any("records note" in e for e in errs_after(m))


def test_ev_reporting_a_level_rejected():
    for bad in ("E2 partial.", "Below \U0001f7e1, fix it", "Partial: pass the exit check"):
        def m(d, bad=bad):
            d["comps"][0]["ev"] = bad
        assert any("'ev' must define evidence" in e for e in errs_after(m)), bad


def test_private_term_in_data_rejected():
    def m(d):
        d["comps"][0]["why"] = "Because Testname said so"
    assert any("private term" in e for e in validate_with_terms(m, ["testname"]))


def validate_with_terms(mutate, terms):
    d = copy.deepcopy(BASE)
    mutate(d)
    return validate(d, terms)


def test_public_file_scan(tmp_path):
    (tmp_path / "ok.md").write_text("Nothing personal here.\n", encoding="utf-8")
    (tmp_path / "leak.md").write_text(f"line one\nsee {REC}\nby Testname\n", encoding="utf-8")
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "notes.md").write_text(f"{REC} Testname\n", encoding="utf-8")
    errs = privacy_scan_files(tmp_path, ["testname"])
    assert "privacy: record ID in leak.md:2" in errs
    assert "privacy: private term in leak.md:3" in errs
    assert not any("private/" in e or "ok.md" in e for e in errs)


GOOD_TT = {"v": 1, "kdf": "PBKDF2-SHA256", "iter": 600000, "cipher": "AES-256-GCM",
           "salt": "AAAAAAAAAAAAAAAAAAAAAA==", "iv": "AAAAAAAAAAAAAAAA", "ct": "AAAAAAAAAAAAAAAAAAAAAAAA"}


def test_encrypted_timetable_shape_accepted():
    assert errs_after(lambda d: d.update(timetable=dict(GOOD_TT))) == []


def test_plain_text_timetable_rejected():
    assert any("plain text" in e for e in errs_after(lambda d: d.update(timetable={"rows": [{"when": "Mon", "what": "x"}]})))


def test_weak_timetable_kdf_rejected():
    assert any("iter" in e for e in errs_after(lambda d: d.update(timetable=dict(GOOD_TT, iter=1000))))


def test_group_member_must_exist():
    def m(d):
        d["meta"]["groups"] = [{"id": "X-1–2", "name": "X", "members": ["NET-1", "NOPE-1"]}]
    assert any("unknown member" in e for e in errs_after(m))


if __name__ == "__main__":
    import inspect
    import tempfile
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            if "tmp_path" in inspect.signature(fn).parameters:
                with tempfile.TemporaryDirectory() as tmp:
                    fn(Path(tmp))
            else:
                fn()
            print("ok", name)
