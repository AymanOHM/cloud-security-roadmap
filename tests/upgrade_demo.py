"""Gate 3 demo: export progress from an older build, upgrade, import, and prove nothing is lost.

Builds the old app from a git ref (default: tag v1.2-baseline, the data 1.2 app with group IDs and v1
storage) and the current app from the working tree, then in a real browser:
  1. marks progress in the OLD app through its UI (statuses, notes, evidence, incl. a group ID) and exports it;
  2. same-origin upgrade: opens the NEW app in the same browser profile, which migrates storage v1 -> v2;
  3. new-origin upgrade: opens the NEW app in a fresh profile and imports the exported file (merge);
and checks that every status, note and evidence text from the old app is present in the new one,
either on its competency or, for a split group ID, as an orphan that points at the new IDs.

Run: python3 tests/upgrade_demo.py [--ref REF]   (needs git, Playwright + Chromium; exit 1 on loss)
"""
import argparse
import asyncio
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright
from nav import open_view

ROOT = Path(__file__).resolve().parent.parent
KEY2 = "ntidebi-roadmap-v2"
OLD_MARKS = {"NET-1": ("ip", "subnetting drills", ""), "LNX-1": ("done", "", "bandit 0-20 log"),
             "PY-1–7": ("done", "python group note", "log-parser repo"), "GIT-1–4": ("ip", "", "")}


def build_old(ref, tmp):
    tar = Path(tmp) / "old.tar"
    subprocess.run(["git", "-C", str(ROOT), "archive", "-o", str(tar), ref], check=True)
    old = Path(tmp) / "old"
    with tarfile.open(tar) as t:
        t.extractall(old, filter="data")
    subprocess.run([sys.executable, str(old / "tools" / "build.py")], check=True, capture_output=True, cwd=old)
    return (old / "dist" / "index.html").as_uri()


def find(state, old_id):
    """Where did an old entry end up? Returns (place, entry)."""
    if old_id in state["progress"]:
        return "progress", state["progress"][old_id]
    if old_id in state["orphans"]:
        return "orphan", state["orphans"][old_id]
    return None, {}


def verify(label, state):
    lost = []
    for oid, (status, note, ev) in OLD_MARKS.items():
        place, e = find(state, oid)
        if place is None or e.get("status") != status or (note and e.get("notes") != note) or (ev and e.get("evidence") != ev):
            lost.append(oid)
        else:
            extra = f" → orphan, split into {', '.join(e.get('splitInto', []))}" if place == "orphan" else ""
            print(f"  {label}: {oid} kept ({status}{', notes' if note else ''}{', evidence' if ev else ''}){extra}")
    return lost


async def main(ref):
    new_url = (ROOT / "dist" / "index.html").as_uri()
    with tempfile.TemporaryDirectory() as tmp:
        old_url = build_old(ref, tmp)
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--no-sandbox"])
            ctx = await b.new_context(accept_downloads=True)
            pg = await ctx.new_page()
            await pg.goto(old_url)
            await pg.evaluate("localStorage.clear()")
            await pg.reload()
            print(f"1. old app ({ref}): marking progress through its UI")
            for oid, (status, note, ev) in OLD_MARKS.items():
                await pg.click("#tabs button[data-v=checklist]")
                await pg.click(f'#v-checklist a[data-open="{oid}"]')
                await pg.click(f"#sset button[data-s={status}]")
                if note:
                    await pg.fill("#pnotes", note)
                if ev:
                    await pg.fill("#pev", ev)
            await pg.click("#tabs button[data-v=dash]")
            async with pg.expect_download() as dl:
                await pg.click("#exp")
            exported = json.loads(Path(await (await dl.value).path()).read_text())
            print(f"   exported {len(exported['status'])} statuses (v1 format)")

            print("2. same-origin upgrade: open the new app in the same profile")
            await pg.goto(new_url)
            await pg.wait_for_timeout(300)
            s = await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY2}'))")
            lost = verify("same origin", s)
            backup = await pg.evaluate("localStorage.getItem('ntidebi-roadmap-v1-backup') !== null")
            print(f"   v1 copy kept under ntidebi-roadmap-v1-backup: {backup}")

            print("3. new-origin upgrade: fresh profile, import the exported file (merge)")
            ctx2 = await b.new_context(accept_downloads=True)
            pg2 = await ctx2.new_page()
            await pg2.goto(new_url)
            await open_view(pg2, "dash")
            await pg2.set_input_files("#imp", files=[{"name": "export.json", "mimeType": "application/json",
                                                        "buffer": json.dumps(exported).encode()}])
            await pg2.wait_for_selector("dialog#dlg[open] [data-dlg=merge]")
            preview = (await pg2.inner_text("dialog#dlg")).split("\n")
            print("   preview: " + next((l for l in preview if "competencies with progress" in l), "?"))
            async with pg2.expect_download():
                await pg2.click("dialog#dlg [data-dlg=merge]")
            await pg2.wait_for_timeout(200)
            s2 = await pg2.evaluate(f"JSON.parse(localStorage.getItem('{KEY2}'))")
            lost += verify("import", s2)
            await b.close()
    print("\nRESULT: " + ("nothing lost" if not lost and backup else f"LOST {sorted(set(lost))}"))
    return 0 if not lost and backup else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="v1.2-baseline")
    sys.exit(asyncio.run(main(ap.parse_args().ref)))
