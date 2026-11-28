"""Browser tests for progress persistence (Stage 3): progress survives data updates and imports.

Build first: python3 tools/build.py. Needs Playwright + Chromium (see tests/e2e_smoke.py).
Run: python3 tests/e2e_persistence.py   (exit code 1 on any failure)

Checks:
- v1 storage (the pre-Stage-3 app) migrates to the v2 envelope; a copy of v1 is kept; a split group ID
  becomes an orphan pointing at its parts, and nothing is copied to the parts.
- A data update that **renames, removes and adds** competencies keeps every piece of progress: the renamed
  ID carries status, notes and evidence; the removed one becomes an orphan; the added one starts empty; the
  "changed since your last visit" notice lists all three.
- An orphan can be moved to a competency.
- Export from one origin and import on a fresh origin (file:// vs Pages) restores everything (merge).
- A records seed sets level and U/E/D only, never a status; an empty seed entry clears old record fields.
- The "Completed without evidence" warning shows until E4 + a link.
- Lateness: a project whose window has passed shows "Late"; the backup reminder and first-run notice show.
"""
import asyncio
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright
from nav import open_view

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate import load_all  # noqa: E402

KEY1, KEY2 = "ntidebi-roadmap-v1", "ntidebi-roadmap-v2"
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def build_variant(tmp):
    """Data B = current data with NET-1 renamed to NET-1R, COMM-2 removed and NEW-1 added."""
    d = load_all()
    ren = lambda ids: ["NET-1R" if x == "NET-1" else x for x in ids]  # noqa: E731
    comps = []
    for c in copy.deepcopy(d["comps"]):
        if c["id"] == "COMM-2":
            continue
        if c["id"] == "NET-1":
            c["id"] = "NET-1R"
        c["pre"] = ren(c["pre"])
        comps.append(c)
    new = copy.deepcopy(comps[0])
    new.update(id="NEW-1", name="A competency added in data B", pre=[])
    comps.insert(1, new)
    meta = copy.deepcopy(d["meta"])
    meta["dataVersion"] = "test-B"
    projects = copy.deepcopy(d["projects"])
    for p in projects:
        p["comps"] = ren([x for x in p["comps"] if x != "COMM-2"])
    certs = copy.deepcopy(d["certs"])
    for k in certs:
        k["comps"] = ren([x for x in k["comps"] if x != "COMM-2"])
    mig = dict(d["migrations"], **{"NET-1": "NET-1R"})
    data = Path(tmp) / "data"
    data.mkdir()
    for name, obj in [("roadmap.json", meta), ("competencies.json", comps), ("projects.json", projects),
                      ("certifications.json", certs), ("comparison.json", d["compare"]),
                      ("id-migrations.json", {"migrations": mig})]:
        (data / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    out = Path(tmp) / "b" / "index.html"
    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py"), "--data", str(data), "--out", str(out)],
                   check=True, capture_output=True)
    return out.as_uri()


async def stored(pg):
    return await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY2}'))")


async def import_file(pg, obj, button):
    await open_view(pg, 'dash')
    await pg.set_input_files("#imp", files=[{"name": "in.json", "mimeType": "application/json",
                                               "buffer": json.dumps(obj).encode()}])
    await pg.wait_for_selector(f"dialog#dlg[open] [data-dlg={button}]")
    async with pg.expect_download():
        await pg.click(f"dialog#dlg [data-dlg={button}]")
    await pg.wait_for_timeout(150)


async def main():
    url_a = (ROOT / "dist" / "index.html").as_uri()
    with tempfile.TemporaryDirectory() as tmp:
        url_b = build_variant(tmp)
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--no-sandbox"])
            errs = []

            # 1. v1 -> v2 migration
            ctx = await b.new_context(accept_downloads=True)
            pg = await ctx.new_page()
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(url_a)
            v1 = {"status": {"NET-1": "ip", "PY-1–7": "done", "LNX-1": "done"},
                  "notes": {"NET-1": "my note", "PY-1–7": "group note"},
                  "evidence": {"LNX-1": "bandit 0-20"}, "updated": {"NET-1": "2026-11-20T10:00:00Z"}}
            await pg.evaluate("([k, v]) => { localStorage.clear(); localStorage.setItem(k, v) }", [KEY1, json.dumps(v1)])
            await pg.reload()
            s = await stored(pg)
            check(s and s["storageVersion"] == 2, "v1 storage migrates to the v2 envelope")
            check(s["progress"]["NET-1"] == {"status": "ip", "notes": "my note", "updated": "2026-11-20T10:00:00Z"},
                  "v1 status, notes and timestamp carried over")
            check(s["progress"]["LNX-1"].get("evidence") == "bandit 0-20", "v1 evidence text carried over")
            o = s["orphans"].get("PY-1–7", {})
            check(o.get("reason") == "split" and o.get("splitInto", [])[:1] == ["PY-1"] and o.get("status") == "done",
                  "split group ID becomes an orphan pointing at its parts")
            check(not any(k.startswith("PY-") for k in s["progress"]), "a split never copies progress to the parts")
            check(await pg.evaluate(f"localStorage.getItem('{KEY1}-backup') !== null"), "a copy of the v1 data is kept")

            # 2. evidence warning and seed import
            await pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('ntidebi-roadmap-v2'));
                s.progress['NET-2'] = {status: 'done', level: 'E3', link: 'https://x', updated: new Date().toISOString()};
                s.progress['NET-3'] = {status: 'done', level: 'E4', link: 'https://y', u: 'partial', updated: new Date().toISOString()};
                localStorage.setItem('ntidebi-roadmap-v2', JSON.stringify(s)) }""")
            await pg.reload()
            await open_view(pg, 'checklist')
            warned = await pg.evaluate("[...document.querySelectorAll('#v-checklist tr')].filter(r => r.textContent.includes('no evidence')).map(r => r.querySelector('[data-open]').textContent)")
            check("NET-2" in warned and "LNX-1" in warned and "NET-3" not in warned,
                  f"'Completed without evidence' until E4 + link ({warned})")
            seed = {"kind": "roadmap-progress-seed", "seedVersion": 1, "snapshotDate": "2026-11-23",
                    "entries": {"NET-1": {"level": "E1", "levelNote": "needs verification", "u": "partial"},
                                "NET-3": {}, "AI-1": {"level": "E0"}}}
            await import_file(pg, seed, "seed")
            s = await stored(pg)
            check(s["progress"]["NET-1"].get("level") == "E1" and s["progress"]["NET-1"].get("status") == "ip"
                  and s["progress"]["NET-1"].get("notes") == "my note", "seed sets level and U/E/D, keeps status and notes")
            check("u" not in s["progress"]["NET-3"] and "level" not in s["progress"]["NET-3"]
                  and s["progress"]["NET-3"]["link"] == "https://y", "an empty seed entry clears record fields, keeps the link")
            check("AI-1" not in s["progress"], "seed IDs that aren't in the roadmap are skipped")

            # 3. data update: rename, remove, add
            await pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('ntidebi-roadmap-v2'));
                s.progress['COMM-2'] = {status: 'ip', notes: 'mock interview notes', updated: new Date().toISOString()};
                s.progress['NET-1'].evidence = 'dig +trace output';
                localStorage.setItem('ntidebi-roadmap-v2', JSON.stringify(s)) }""")
            await pg.reload()
            before = await stored(pg)
            await pg.goto(url_b)
            await pg.wait_for_timeout(200)
            s = await stored(pg)
            r = s["progress"].get("NET-1R", {})
            check(r.get("status") == "ip" and r.get("notes") == "my note" and r.get("level") == "E1"
                  and r.get("evidence") == "dig +trace output", "renamed ID keeps status, notes, level and evidence")
            check("NET-1" not in s["progress"], "old ID is gone after the rename")
            check(s["orphans"].get("COMM-2", {}).get("notes") == "mock interview notes"
                  and s["orphans"]["COMM-2"]["reason"] == "removed", "removed competency's progress kept as an orphan")
            check("NEW-1" not in s["progress"], "added competency starts empty")
            kept = {k: v for k, v in before["progress"].items() if k not in ("NET-1", "COMM-2")}
            check(all(s["progress"].get(k) == v for k, v in kept.items()), "every other entry is unchanged")
            note = await pg.inner_text("#notice")
            check("1 added" in note and "1 removed" in note and "1 renamed" in note, f"data-change notice ({note[:140]!r})")
            await pg.click("#notice [data-act=seen]")
            await pg.reload()
            check("changed since" not in await pg.inner_text("#notice"), "notice stays dismissed after 'Got it'")
            await open_view(pg, 'dash')
            await pg.select_option('select[data-orphto="COMM-2"]', "COMM-1")
            await pg.click('[data-orph="COMM-2"][data-a=move]')
            s = await stored(pg)
            check("COMM-2" not in s["orphans"] and s["progress"]["COMM-1"].get("notes") == "mock interview notes",
                  "an orphan can be moved to a competency")

            # 4. export here, import on a fresh origin (new context = empty storage)
            async with pg.expect_download() as dl:
                await pg.click("#exp")
            exported = json.loads(Path(await (await dl.value).path()).read_text())
            ctx2 = await b.new_context(accept_downloads=True)
            pg2 = await ctx2.new_page()
            pg2.on("pageerror", lambda e: errs.append(str(e)))
            await pg2.goto(url_b)
            check("No saved progress" in await pg2.inner_text("#notice"), "first run on a new origin offers import")
            await import_file(pg2, exported, "merge")
            s2 = await stored(pg2)
            check(s2["progress"] == exported["progress"] and s2["orphans"] == exported["orphans"],
                  "export → import on a fresh origin restores everything")
            check("No saved progress" not in await pg2.inner_text("#notice"), "first-run notice gone after import")

            # 5. lateness and backup reminder
            ctx3 = await b.new_context(accept_downloads=True)
            await ctx3.add_init_script("window.ROADMAP_TODAY = '2027-01-05'")
            pg3 = await ctx3.new_page()
            await pg3.goto(url_a)
            await pg3.evaluate("""() => { localStorage.setItem('ntidebi-roadmap-v2', JSON.stringify({app: 'nti-debi-roadmap',
                storageVersion: 2, createdAt: '2026-11-01T00:00:00Z', lastChangeAt: '2026-11-20T00:00:00Z',
                progress: {'NET-1': {status: 'ip'}}, orphans: {}})) }""")
            await pg3.reload()
            await open_view(pg3, 'projects')
            proj = await pg3.inner_text("#v-projects")
            check("Late: window ended" in proj, "a project past its window shows Late")
            await open_view(pg3, "today")
            check("Late: window ended" in await pg3.inner_text("#v-today"), "Today lists items past their window")
            check("Back up your progress" in await pg3.inner_text("#notice"), "backup reminder after 7 days without export")
            check(errs == [], f"no JS errors ({errs})")
            await b.close()
    print(f"\n{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


asyncio.run(main())
