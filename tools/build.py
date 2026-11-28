#!/usr/bin/env python3
"""Build dist/index.html: validate data/*.json, then inline it into app/template.html.

The output is one self-contained file that works from file:// (offline) and on
GitHub Pages. Nothing is fetched at runtime.

Usage: python3 tools/build.py [--data DIR] [--out FILE]
  --data / --out build another dataset to another file (used by the upgrade tests).
"""
import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import load_all, validate, private_terms, privacy_scan_files, ROOT  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    d = load_all(args.data)
    terms = private_terms()
    errs = validate(d, terms) + privacy_scan_files(ROOT, terms)
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
        "migrations": d["migrations"], "groups": m.get("groups", []),
        "timetable": d["timetable"],
    }
    tpl = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
    if "/*DATA*/null" not in tpl:
        print("app/template.html has no /*DATA*/null placeholder")
        sys.exit(1)
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    # The one embedded font (Host Grotesk, SIL OFL 1.1, app/fonts/OFL.txt), inlined so the page stays offline.
    font = ROOT / "app" / "fonts" / "host-grotesk-latin-wght-normal.woff2"
    tpl = tpl.replace("__FONT_HOST_GROTESK__", base64.b64encode(font.read_bytes()).decode("ascii"))
    out = Path(args.out).resolve() if args.out else ROOT / "dist" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.replace("/*DATA*/null", blob), encoding="utf-8")
    print(f"built {out} ({out.stat().st_size // 1024} KB), data version {m['dataVersion']}")


if __name__ == "__main__":
    main()
