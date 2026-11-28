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
from nav import open_view

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "dist" / "index.html").as_uri()
SHOTS = ROOT / "build" / "screens"
VIEWS = ["today", "checklist", "kanban", "route", "flow", "paths", "projects", "certs", "compare", "time", "skills", "dash"]
fails = []


# Resolve two colour tokens to sRGB through a canvas (computed styles may stay in oklch) and return contrast ratios.
CONTRAST_JS = """mode => {
  const root = document.documentElement, prev = root.dataset.mode;
  root.dataset.mode = mode;
  const cs = getComputedStyle(root), cx = document.createElement('canvas').getContext('2d', {willReadFrequently: true});
  const rgb = tok => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = cs.getPropertyValue(tok).trim(); cx.fillRect(0, 0, 1, 1); return [...cx.getImageData(0, 0, 1, 1).data].slice(0, 3) };
  const lum = c => { const [r, g, b] = c.map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4 }); return 0.2126 * r + 0.7152 * g + 0.0722 * b };
  const ratio = (a, b) => { const [x, y] = [lum(rgb(a)), lum(rgb(b))].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05) };
  const out = {};
  for (const bg of ['--color-paper', '--color-paper-2', '--color-paper-3']) out[bg] = +ratio('--color-muted', bg).toFixed(2);
  if (prev) root.dataset.mode = prev; else delete root.dataset.mode;
  return out }"""


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

    # navigation: Today is the landing view; the current destination and lens are marked and kept in the URL
    check(await pg.get_attribute('#nav [data-nav="today"]', "aria-current") == "page", "Today is the landing view, marked aria-current")
    await open_view(pg, "flow")
    check(await pg.get_attribute('#nav [data-nav="roadmap"]', "aria-current") == "page"
          and await pg.get_attribute('#lenses [data-lens="map"]', "aria-current") == "page", "the open destination and lens are marked aria-current")
    check(pg.url.endswith("#roadmap/map"), f"the view is kept in the URL ({pg.url.split('#')[-1]})")

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

    # list (replaces the stage map): each row names its source and line; each stage opens its gate from the keyboard
    await open_view(pg, "checklist")
    row = await pg.evaluate("""document.querySelector('#v-checklist a[data-open="NET-1"]').closest('tr').textContent""")
    check("DEBI" in row and "Networking" in row, "list row names its source and line")
    check(await pg.locator("#v-checklist button[data-stage]").count() == 5, "each stage's gate opens from a button")
    # filters live in the URL and survive a reload
    await pg.select_option("#fstage", "FND")
    await pg.select_option("#fstatus", "ready")
    check("stage=FND" in pg.url and "status=ready" in pg.url, f"filters are kept in the URL ({pg.url.split('#')[-1]})")
    await pg.reload()
    await pg.wait_for_timeout(300)
    check(await pg.input_value("#fstatus") == "ready" and await pg.locator("#v-checklist tbody tr").count() > 0, "a filtered link reopens with its filters")
    await open_view(pg, "board")
    check(await pg.locator('.kcol[data-col="locked"] .kcard').count() == 0, "the board uses the same filters")
    await pg.click("#fclear")
    await open_view(pg, "flow")

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
    await pg.goto(URL + "#roadmap/map")
    await pg.wait_for_timeout(300)
    check(await pg.locator('#cv-flow g.node[data-id="PY-1–7"]').count() == 1
          and await pg.locator('#cv-flow g.node[data-id="PY-3"]').count() == 0, "Python group is one collapsed node")
    check(await pg.locator('#v-checklist a[data-open="PY-3"]').count() == 1, "the list shows the members individually")
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
    await pg.goto(URL + "#roadmap/map")
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
    await open_view(pg, "kanban")
    await pg.wait_for_timeout(150)
    card = pg.locator('.kcol[data-col="locked"] .kcard').first
    cid = await card.get_attribute("data-id")
    await card.drag_to(pg.locator('.kcol[data-col="ns"]'))
    await pg.wait_for_timeout(150)
    check(await pg.locator(f'.kcol[data-col="locked"] .kcard[data-id="{cid}"]').count() == 1, "locked card isn't dropped on Ready")
    check(await pg.locator(".kcard[tabindex='0'][role=button]").count() > 50, "Kanban cards are keyboard-focusable")

    # cert timeline derived from data (A-20); contrast token
    await open_view(pg, "certs")
    months = await pg.evaluate("[...document.querySelectorAll('.tlmonths div')].map(d => d.textContent)")
    check(months[0].startswith("Nov 2026") and months[-1].startswith("Dec"), f"cert timeline spans today to the last cert ({months[0]} … {months[-1]})")
    # the quietest text colour stays readable on every surface it sits on, in both colour modes (WCAG AA 4.5:1)
    for mode in ("light", "dark"):
        ratios = await pg.evaluate(CONTRAST_JS, mode)
        worst = min(ratios.values())
        check(worst >= 4.5, f"{mode} mode: muted text contrast {worst:.2f}:1 or better ({ratios})")
    check(await pg.evaluate("getComputedStyle(document.querySelector('#cv-flow')).touchAction") == "none", "canvas has touch-action:none")
    await pg.close()


async def mobile(b, errs):
    m = await b.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    m.on("pageerror", lambda e: errs.append("mobile: " + str(e)))
    await m.goto(URL)
    await m.wait_for_timeout(300)
    for v in VIEWS:
        await open_view(m, v)
        await m.wait_for_timeout(120)
        over = await m.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(over <= 0, f"390 px: {v} has no page-level horizontal overflow ({over}px)")
        await m.screenshot(path=str(SHOTS / f"m-{v}.png"))
    await open_view(m, "flow")
    k = await m.evaluate("+document.querySelector('#cv-flow g.vp').getAttribute('transform').match(/scale\\(([\\d.]+)\\)/)[1]")
    check(k >= 0.75, f"phone flowchart scale keeps text readable (scale {k})")
    tb = await m.evaluate("document.querySelector('#v-flow .toolbar').getBoundingClientRect().height")
    check(tb < 844 * 0.2, f"phone toolbar is compact ({tb:.0f}px)")
    await open_view(m, "kanban")
    w = await m.evaluate("document.querySelector('.kcol.mshow').getBoundingClientRect().width")
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
        await open_view(pg, "time")
        check(await pg.locator("#ttunlock #ttpw").count() == 1, "the published timetable shows the unlock form")
    tmp_none = tempfile.mkdtemp()  # removed at the end of the test
    _, none_out = build_with_timetable(tmp_none, "none", None)
    await pg.goto(none_out.as_uri())
    await open_view(pg, "time")
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
        await open_view(pg, "time")
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
