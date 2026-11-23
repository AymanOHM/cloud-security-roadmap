"""Browser smoke test of dist/index.html (build first: python3 tools/build.py).

Needs Playwright with a Chromium: pip install playwright && python3 -m playwright install chromium
Run: python3 tests/e2e_smoke.py   (exit code 1 on any failure; screenshots go to build/screens/)

Checks: no JS errors on load; every view renders; a node opens its detail panel and its ID is shown there
(not as the node headline); a status change persists across reload; Kanban drag changes status;
export produces JSON; reset clears progress; a crafted or malformed import is sanitized and runs no
script (AUDIT A-12); the phone-size layout loads.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "dist" / "index.html").as_uri()
SHOTS = ROOT / "build" / "screens"
KEY = "ntidebi-roadmap-v2"
VIEWS = ["flow", "roadmap", "kanban", "checklist", "paths", "compare", "projects", "certs", "dash"]
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


async def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        exe = os.environ.get("CHROME_PATH")
        b = await p.chromium.launch(**({"executable_path": exe} if exe else {}), args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, accept_downloads=True)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto(URL)
        await pg.wait_for_timeout(400)
        for v in VIEWS:
            await pg.click(f"#tabs button[data-v={v}]")
            await pg.wait_for_timeout(150)
            await pg.screenshot(path=str(SHOTS / f"{v}.png"))
        await pg.click("#tabs button[data-v=flow]")
        node = pg.locator("#cv-flow g.node[aria-label]").first
        label = await node.get_attribute("aria-label")
        texts = await node.evaluate("n => [...n.querySelectorAll('text')].map(t => t.textContent)")
        check(not any((t or "").strip().startswith(("NET-", "LNX-")) for t in texts), "node headline shows the name, not the ID")
        await node.click()
        await pg.wait_for_timeout(150)
        pid = await pg.locator("#panel .pid").inner_text()
        check(bool(pid.strip()), f"detail panel shows the ID ({pid.strip()}) for '{label}'")
        await pg.click("#sset button[data-s=ip]")
        await pg.reload()
        await pg.wait_for_timeout(300)
        saved = await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
        check(saved and saved["progress"].get(pid.strip(), {}).get("status") == "ip", "status persists across reload")
        await pg.click("#tabs button[data-v=kanban]")
        await pg.wait_for_timeout(200)
        card = pg.locator('.kcol[data-col="ns"] .kcard').first
        cid = await card.get_attribute("data-id")
        await card.drag_to(pg.locator('.kcol[data-col="done"]'))
        await pg.wait_for_timeout(200)
        saved = await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
        check(saved["progress"].get(cid, {}).get("status") == "done", f"kanban drag sets {cid} to done")
        await pg.click("#tabs button[data-v=dash]")
        async with pg.expect_download() as dl:
            await pg.click("#exp")
        path = await (await dl.value).path()
        exported = json.loads(Path(path).read_text())
        check(exported["progress"][cid]["status"] == "done" and exported["storageVersion"] == 2, "export contains progress")
        pg.once("dialog", lambda d: asyncio.ensure_future(d.accept()))
        async with pg.expect_download() as dl:
            await pg.click("#rst")
        backup = json.loads(Path(await (await dl.value).path()).read_text())
        check(backup["progress"][cid]["status"] == "done", "reset downloads a backup first")
        await pg.wait_for_timeout(200)
        saved = await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
        check(saved["progress"] == {}, "reset clears progress")
        evil = {"status": {"NET-1": 'done"><img src=x onerror="window.__x=1">', "NET-2": "banana",
                           "NOPE-1": "done", "NET-3": "ip"},
                "notes": "not an object", "evidence": {"NET-3": 5, "NET-4": "repo link"}}
        for _ in range(2):  # the same file twice must import twice (A-22)
            await pg.set_input_files("#imp", files=[{"name": "evil.json", "mimeType": "application/json",
                                                       "buffer": json.dumps(evil).encode()}])
            await pg.wait_for_selector("dialog#dlg[open] [data-dlg=replace]")
            async with pg.expect_download():
                await pg.click("dialog#dlg [data-dlg=replace]")
            await pg.wait_for_timeout(150)
        for v in VIEWS:
            await pg.click(f"#tabs button[data-v={v}]")
            await pg.wait_for_timeout(60)
        check(await pg.evaluate("window.__x") is None, "crafted import runs no script")
        saved = await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
        prog = {k: {f: v for f, v in e.items() if f != "updated"} for k, e in saved["progress"].items()}
        check(prog == {"NET-3": {"status": "ip"}, "NET-4": {"evidence": "repo link"}},
              f"import keeps only valid statuses and string fields ({prog})")
        check(list(saved["orphans"]) == ["NOPE-1"], "an unknown ID is kept as an orphan, not dropped")
        await pg.click("#tabs button[data-v=flow]")
        await pg.locator("#cv-flow g.node[aria-label]").first.click()
        await pg.fill("#pnotes", "a note")
        saved = await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
        check(any(e.get("notes") == "a note" for e in saved["progress"].values()), "notes still editable after a malformed import")
        m = await b.new_page(viewport={"width": 390, "height": 844})
        m.on("pageerror", lambda e: errs.append("mobile: " + str(e)))
        await m.goto(URL)
        await m.wait_for_timeout(300)
        await m.screenshot(path=str(SHOTS / "mobile.png"))
        check(errs == [], f"no JS errors ({errs})")
        await b.close()
    print(f"\n{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


asyncio.run(main())
