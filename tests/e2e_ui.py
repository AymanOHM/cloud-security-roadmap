"""Browser tests for Stage 4: navigation, flowchart, keyboard, mobile layout and the encrypted timetable.

Build first: python3 tools/build.py. Needs Playwright + Chromium (see tests/e2e_smoke.py).
Run: python3 tests/e2e_ui.py   (exit code 1 on any failure; screenshots go to build/screens/)
"""
import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "dist" / "index.html").as_uri()
SHOTS = ROOT / "build" / "screens"
VIEWS = ["flow", "roadmap", "kanban", "checklist", "paths", "compare", "projects", "certs", "time", "dash"]
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


async def transform(pg, view="flow"):
    return await pg.get_attribute(f"#cv-{view} g.vp", "transform")


async def desktop(b, errs):
    pg = await b.new_page(viewport={"width": 1440, "height": 900})
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(URL)
    await pg.wait_for_timeout(300)

    # tabs: ARIA roles and arrow keys
    roles = await pg.evaluate("[...document.querySelectorAll('#tabs button')].map(b => b.getAttribute('role') + ':' + b.getAttribute('aria-selected'))")
    check(roles[0] == "tab:true" and all(r == "tab:false" for r in roles[1:]), "tabs use role=tab with aria-selected")
    await pg.focus("#tab-flow")
    await pg.keyboard.press("ArrowRight")
    check(await pg.get_attribute("#tab-roadmap", "aria-selected") == "true", "ArrowRight moves to the next view")
    await pg.click("#tab-flow")

    # keyboard on graph nodes: Space opens, Escape closes and returns focus
    await pg.focus('#cv-flow g.node[data-id="NET-2"]')
    await pg.keyboard.press(" ")
    check(await pg.inner_text("#panel .pid") == "NET-2", "Space on a node opens its panel")
    check(await pg.evaluate("document.activeElement.closest('#panel') !== null"), "focus moves into the panel")
    await pg.keyboard.press("Escape")
    check(not await pg.is_visible("#panel"), "Escape closes the panel")
    check(await pg.evaluate("document.activeElement.getAttribute('data-id')") == "NET-2", "focus returns to the node")
    label = await pg.get_attribute('#cv-flow g.node[data-id="NET-6"]', "aria-label")
    check("NET-6" in label and "locked" in label, f"node name includes ID and status ({label})")

    # stage map: source on each node, headers focusable
    await pg.click("#tab-roadmap")
    await pg.wait_for_timeout(150)
    texts = await pg.evaluate("""[...document.querySelectorAll('#cv-roadmap g.node[data-id="NET-1"] text')].map(t => t.textContent)""")
    check("DEBI" in texts, f"stage-map node names its source ({texts})")
    check(await pg.locator("#cv-roadmap g.stagehd[tabindex='0']").count() == 5, "stage headers are keyboard-focusable")
    await pg.click("#tab-flow")

    # search and deep links
    await pg.keyboard.press("/")
    check(await pg.evaluate("document.activeElement.classList.contains('gsearch')"), "'/' focuses the search box")
    await pg.keyboard.type("subnetting")
    await pg.keyboard.press("Enter")
    await pg.wait_for_timeout(150)
    check(await pg.inner_text("#panel .pid") == "NET-2", "search by name opens the match")
    check(pg.url.endswith("#NET-2"), "selection updates the URL hash")
    await pg.goto(URL + "#LNX-3")
    await pg.wait_for_timeout(400)
    check(await pg.inner_text("#panel .pid") == "LNX-3", "deep link #LNX-3 opens that competency")

    # clusters (D-04): groups collapsed in the flowchart, expanded on demand
    await pg.goto(URL)
    await pg.wait_for_timeout(300)
    check(await pg.locator('#cv-flow g.node[data-id="PY-1–7"]').count() == 1
          and await pg.locator('#cv-flow g.node[data-id="PY-3"]').count() == 0, "Python group is one collapsed node")
    check(await pg.locator('#cv-roadmap g.node[data-id="PY-3"]').count() == 1, "stage map shows the members individually")
    await pg.click('#cv-flow g.node[data-id="PY-1–7"]')
    check("Python core" in await pg.inner_text("#panel h2"), "clicking a group opens the group panel")
    await pg.click("#gtog")
    await pg.wait_for_timeout(150)
    check(await pg.locator('#cv-flow g.node[data-id="PY-3"]').count() == 1, "Expand shows the members in the flowchart")
    await pg.goto(URL + "#WEB-3")
    await pg.wait_for_timeout(400)
    check(await pg.locator('#cv-flow g.node[data-id="WEB-3"]').count() == 1, "a deep link to a member expands its group")
    edges = await pg.evaluate("""[...document.querySelectorAll('#cv-flow path.edge')].length""")
    check(edges > 50, f"edges still drawn ({edges})")

    # JOB band (A-19)
    await pg.goto(URL)
    await pg.wait_for_timeout(300)
    ys = await pg.evaluate("""['JOB-1','NET-1'].map(id => document.querySelector(`#cv-flow g.node[data-id="${id}"]`).transform.baseVal[0].matrix.f)""")
    check(ys[0] > ys[1], "job-readiness items sit in the ongoing band, not in 'Start here'")

    # focus chain
    await pg.click('#v-flow .chainTog')
    await pg.click('#cv-flow g.node[data-id="NET-3"]')
    dim = await pg.evaluate("""id => document.querySelector(`#cv-flow g.node[data-id="${id}"]`).classList.contains('dim')""", "CSEC-9")
    keep = await pg.evaluate("""id => document.querySelector(`#cv-flow g.node[data-id="${id}"]`).classList.contains('dim')""", "NET-1")
    check(dim and not keep, "focus chain dims everything outside the selected chain")
    await pg.click('#v-flow .chainTog')

    # background click closes the panel (A-14); resize keeps the zoom (A-15)
    box = await pg.locator("#cv-flow").bounding_box()
    await pg.mouse.click(box["x"] + 5, box["y"] + box["height"] - 5)
    check(not await pg.is_visible("#panel"), "clicking the background closes the panel")
    await pg.click("#cv-flow .zin")
    before = await transform(pg)
    await pg.set_viewport_size({"width": 1400, "height": 860})
    await pg.wait_for_timeout(150)
    check(await transform(pg) == before, "resizing keeps the user's zoom")

    # Kanban: locked card can't be dropped on Ready (A-13); cards are focusable
    await pg.click("#tab-kanban")
    await pg.wait_for_timeout(150)
    card = pg.locator('.kcol[data-col="locked"] .kcard').first
    cid = await card.get_attribute("data-id")
    await card.drag_to(pg.locator('.kcol[data-col="ns"]'))
    await pg.wait_for_timeout(150)
    check(await pg.locator(f'.kcol[data-col="locked"] .kcard[data-id="{cid}"]').count() == 1, "locked card isn't dropped on Ready")
    check(await pg.locator(".kcard[tabindex='0'][role=button]").count() > 50, "Kanban cards are keyboard-focusable")

    # cert timeline derived from data (A-20); contrast token
    await pg.click("#tab-certs")
    months = await pg.evaluate("[...document.querySelectorAll('.tlmonths div')].map(d => d.textContent)")
    check(months[0].startswith("Nov 2026") and months[-1].startswith("Dec"), f"cert timeline spans today to the last cert ({months[0]} … {months[-1]})")
    faint = await pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--faint').trim()")
    check(faint == "#8b949e", "--faint raised for contrast")
    check(await pg.evaluate("getComputedStyle(document.querySelector('#cv-flow')).touchAction") == "none", "canvas has touch-action:none")
    await pg.close()


async def mobile(b, errs):
    m = await b.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    m.on("pageerror", lambda e: errs.append("mobile: " + str(e)))
    await m.goto(URL)
    await m.wait_for_timeout(300)
    for v in VIEWS:
        await m.click(f"#tab-{v}")
        await m.wait_for_timeout(120)
        over = await m.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(over <= 0, f"390 px: {v} has no page-level horizontal overflow ({over}px)")
        await m.screenshot(path=str(SHOTS / f"m-{v}.png"))
    await m.click("#tab-flow")
    k = await m.evaluate("+document.querySelector('#cv-flow g.vp').getAttribute('transform').match(/scale\\(([\\d.]+)\\)/)[1]")
    check(k >= 0.75, f"phone flowchart scale keeps text readable (scale {k})")
    tb = await m.evaluate("document.querySelector('#v-flow .toolbar').getBoundingClientRect().height")
    check(tb < 844 * 0.2, f"phone toolbar is compact ({tb:.0f}px)")
    await m.click("#tab-kanban")
    w = await m.evaluate("document.querySelector('.kcol').getBoundingClientRect().width")
    check(w <= 390, f"Kanban columns stack at 390 px (column {w:.0f}px)")
    await m.close()


def build_with_timetable(tmp, name, blob):
    """Build the current data with the timetable replaced by `blob` (None = no timetable)."""
    data = Path(tmp) / f"data-{name}"
    subprocess.run(["cp", "-R", str(ROOT / "data"), str(data)], check=True)
    tt = data / "timetable.enc.json"
    if blob is None:
        tt.unlink(missing_ok=True)
    else:
        tt.write_text(json.dumps(blob), encoding="utf-8")
    out = Path(tmp) / name / "index.html"
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build.py"), "--data", str(data), "--out", str(out)],
                       capture_output=True, text=True)
    return r.returncode, out


async def timetable(b, errs):
    pg = await b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
    pg.on("pageerror", lambda e: errs.append("timetable: " + str(e)))
    if (ROOT / "data" / "timetable.enc.json").exists():
        await pg.goto(URL)
        await pg.click("#tab-time")
        check(await pg.locator("#ttunlock #ttpw").count() == 1, "the published timetable shows the unlock form")
    tmp_none = tempfile.mkdtemp()  # removed at the end of the test
    _, none_out = build_with_timetable(tmp_none, "none", None)
    await pg.goto(none_out.as_uri())
    await pg.click("#tab-time")
    check("No timetable is published" in await pg.inner_text("#v-time"), "timetable view explains when none is published")
    await pg.click("#v-time details summary")
    await pg.fill("#ttrows", "Mon 18:00–18:45 | Course item\nThu 16:00–19:00 | Project block")
    await pg.fill("#ttnew", "short")
    check("⚠" in await pg.inner_text("#ttstrength"), "short password warns")
    pw = "correct horse battery staple"
    await pg.fill("#ttnew", pw)
    await pg.fill("#ttnew2", pw)
    await pg.click("#ttenc")
    await pg.wait_for_selector("#ttout", timeout=20000)
    blob = json.loads(await pg.input_value("#ttout"))
    check(set(blob) == {"v", "kdf", "iter", "cipher", "salt", "iv", "ct"} and "Project block" not in json.dumps(blob),
          "encrypt panel produces ciphertext only")
    with tempfile.TemporaryDirectory() as tmp:
        code, out = build_with_timetable(tmp, "t", blob)
        check(code == 0, "build accepts the encrypted timetable")
        await pg.goto(out.as_uri())
        await pg.click("#tab-time")
        await pg.fill("#ttpw", "wrong password")
        await pg.click("#ttunlock button[type=submit]")
        await pg.wait_for_selector("#ttunlock [role=alert]", timeout=20000)
        check("doesn't open" in await pg.inner_text("#ttunlock"), "wrong password is refused")
        await pg.fill("#ttpw", pw)
        await pg.click("#ttunlock button[type=submit]")
        await pg.wait_for_selector("#ttlock", timeout=20000)
        txt = await pg.inner_text("#v-time")
        check("Project block" in txt and "Thu 16:00–19:00" in txt, "right password shows the timetable")
        html = out.read_text(encoding="utf-8")
        check("Project block" not in html, "the built page holds no plain-text timetable")
    await pg.close()
    shutil.rmtree(tmp_none, ignore_errors=True)


async def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        errs = []
        await desktop(b, errs)
        await mobile(b, errs)
        await timetable(b, errs)
        check(errs == [], f"no JS errors ({errs})")
        await b.close()
    print(f"\n{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


asyncio.run(main())
