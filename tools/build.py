#!/usr/bin/env python3
"""Build dist/index.html: validate data/*.json, then inline it into app/template.html.

The output is one self-contained file that works from file:// (offline) and on
GitHub Pages. Nothing is fetched at runtime.

Usage: python3 tools/build.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import load_all, validate, ROOT  # noqa: E402


def main():
    d = load_all()
    errs = validate(d)
    if errs:
        print("Data validation failed; nothing built:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    m = d["meta"]
    payload = {
        "version": m["dataVersion"], "schemaVersion": m["schemaVersion"],
        "stages": m["stages"], "lanes": m["lanes"], "sources": m["sources"], "paths": m["paths"],
        "ntiHours": m["ntiHours"], "ntiPart2Hours": m.get("ntiPart2Hours", {}),
        "comps": d["comps"], "projects": d["projects"], "certs": d["certs"], "compare": d["compare"],
        "migrations": d["migrations"],
    }
    tpl = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
    if "/*DATA*/null" not in tpl:
        print("app/template.html has no /*DATA*/null placeholder")
        sys.exit(1)
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    out = ROOT / "dist" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(tpl.replace("/*DATA*/null", blob), encoding="utf-8")
    print(f"built {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB), data version {m['dataVersion']}")


if __name__ == "__main__":
    main()
