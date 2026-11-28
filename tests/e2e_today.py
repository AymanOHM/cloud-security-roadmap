"""Browser tests for the UX redesign (Nov 2026): Today, the session log, the Track/Learn drawer and the Route lens.
Build first: python3 tools/build.py. Needs Playwright + Chromium (see tests/e2e_smoke.py).
Run: python3 tests/e2e_today.py   (exit code 1 on any failure)

What it proves:
- Today is the landing view: Start moves a ready competency onto the line; a session logs in one step.
- A session records only what was typed: no status change unless "Also mark in progress" is ticked.
- Sessions survive an import merge (both sides kept), and a crafted log is cleaned, never executed.
- The drawer separates Track from Learn; the Route lens draws a competency's chain and moves along it.
- At 390 px the destinations sit in a bottom bar and the drawer fills the screen.
"""
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "dist" / "index.html").as_uri()
KEY = "ntidebi-roadmap-v2"
DAY = "2026-11-28"
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


async def state(pg):
    return await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}') || 'null')")


async def fresh(b, **kw):
    ctx = await b.new_context(accept_downloads=True, **kw)
    await ctx.add_init_script(f"window.ROADMAP_TODAY = '{DAY}'")
    pg = await ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(URL)
    await pg.wait_for_timeout(300)
    return ctx, pg, errs


async def today_flow(b):
    ctx, pg, errs = await fresh(b, viewport={"width": 1440, "height": 900})
    check(await pg.is_visible("#v-today") and "Nothing in progress" in await pg.inner_text("#v-today"), "Today is the landing view, empty state first")
    first = await pg.get_attribute("#v-today [data-start]", "data-start")
    await pg.click(f'#v-today [data-start="{first}"]')
    s = await state(pg)
    check(s["progress"][first]["status"] == "ip", f"Start sets {first} to In progress")
    check(await pg.locator(f'#v-today form.logf[data-log="{first}"]').count() == 1, "the started competency is on the line with a log form")

    form = f'#v-today form.logf[data-log="{first}"]'
    await pg.click(f"{form} button[type=submit]")
    check(await pg.get_attribute(f"{form} textarea", "aria-invalid") == "true" and not (await state(pg))["progress"][first].get("log"),
          "an empty session is refused and nothing is saved")
    await pg.fill(f"{form} textarea", "Layers drill, cold, no notes")
    await pg.click(f'{form} [data-min="25"]')
    await pg.select_option(f"{form} select[name=lv]", "E1")
    await pg.click(f"{form} button[type=submit]")
    e = (await state(pg))["progress"][first]
    check(e.get("log") == [{"d": DAY, "min": 25, "text": "Layers drill, cold, no notes", "lv": "E1"}], f"one step logs the session ({e.get('log')})")
    check(e.get("level") == "E1" and e["status"] == "ip", "the level is the one chosen; the status is unchanged")
    check("Logged 25 min" in await pg.inner_text(f"{form} .logok"), "the form confirms what was logged")
    check("Layers drill" in await pg.inner_text("#v-today"), "This week lists the session")

    # drawer: Track is the default; logging on a Not started competency never changes its status unless asked
    await pg.evaluate("document.activeElement.blur()")
    await pg.keyboard.press("/")
    await pg.keyboard.type("NET-3")
    await pg.keyboard.press("Enter")
    await pg.wait_for_timeout(150)
    check(await pg.get_attribute("#pt-track", "aria-selected") == "true" and await pg.is_visible("#pnotes"), "the drawer opens on Track")
    await pg.fill("#panel form.logf textarea", "Read the ARP chapter")
    await pg.click("#panel form.logf button[type=submit]")
    e = (await state(pg))["progress"]["NET-3"]
    check(e.get("status") is None and len(e["log"]) == 1, "a session alone leaves the status at Not started")
    await pg.fill("#panel form.logf textarea", "NAT lab")
    await pg.check("#panel form.logf input[name=mark]")
    await pg.click("#panel form.logf button[type=submit]")
    e = (await state(pg))["progress"]["NET-3"]
    check(e.get("status") == "ip" and len(e["log"]) == 2, "ticking 'Also mark in progress' starts it")
    await pg.click('#panel [data-rmlog="0"]')
    check(len((await state(pg))["progress"]["NET-3"]["log"]) == 2, "Remove asks for a second click")
    await pg.click('#panel [data-rmlog="0"]')
    check([x["text"] for x in (await state(pg))["progress"]["NET-3"]["log"]] == ["Read the ARP chapter"], "the second click removes that session only")
    await pg.click("#pt-learn")
    check(not await pg.is_visible("#pnotes") and "Learning objectives" in await pg.inner_text("#pp-learn"), "Learn holds the reference, Track the tracking")
    await pg.keyboard.press("ArrowLeft")
    check(await pg.get_attribute("#pt-track", "aria-selected") == "true", "arrow keys switch Track and Learn")
    await pg.keyboard.press("Escape")

    # import merge keeps sessions from both sides; a crafted log is cleaned
    s = await state(pg)
    other = {"app": "nti-debi-roadmap", "storageVersion": 2, "progress": {
        "NET-3": {"log": [{"d": "2026-11-20", "min": 30, "text": "<img src=x onerror=window.__x=1>"},
                          {"d": "not a date", "text": "dropped"}, {"d": "2026-11-21", "min": "40"}],
                  "updated": "2026-11-20T00:00:00Z"}}, "orphans": {}}
    await pg.click("#datalink")
    await pg.set_input_files("#imp", files=[{"name": "o.json", "mimeType": "application/json", "buffer": json.dumps(other).encode()}])
    await pg.wait_for_selector("dialog#dlg[open] [data-dlg=merge]")
    async with pg.expect_download():
        await pg.click("dialog#dlg [data-dlg=merge]")
    await pg.wait_for_timeout(150)
    log = (await state(pg))["progress"]["NET-3"]["log"]
    check([x["d"] for x in log] == [DAY, "2026-11-20"], f"merge keeps the sessions from both sides, newest first ({[x['d'] for x in log]})")
    await pg.goto(URL + "#NET-3")
    await pg.wait_for_timeout(300)
    check(await pg.evaluate("window.__x") is None and "<img" in await pg.inner_text("#panel .sessions"), "a crafted session is shown as text and runs nothing")
    check(errs == [], f"no JS errors ({errs})")
    await ctx.close()


async def route(b):
    ctx, pg, errs = await fresh(b, viewport={"width": 1440, "height": 900})
    await pg.goto(URL + "#roadmap/route/NET-6")
    await pg.wait_for_timeout(300)
    col = lambda i: pg.evaluate(f"[...document.querySelectorAll('#route .rcol')[{i}].querySelectorAll('[data-route]')].map(e => e.dataset.route)")
    check(await pg.inner_text("#route .here .hid") == "NET-6", "the route centres on the station in the URL")
    check(set(await col(1)) == {"NET-3", "NET-4"} and "NET-7" in await col(3), "Needs and Unlocks list the direct neighbours")
    check(await pg.locator("#rlines path").count() >= 3, "the lines between stations are drawn")
    await pg.click('#route [data-route="NET-3"]')
    await pg.wait_for_timeout(200)
    check(pg.url.endswith("#roadmap/route/NET-3") and await pg.inner_text("#route .here .hid") == "NET-3", "selecting a station moves along the line")
    await pg.go_back()
    await pg.wait_for_timeout(200)
    check(await pg.inner_text("#route .here .hid") == "NET-6", "Back returns to the previous station")
    check(errs == [], f"no JS errors ({errs})")
    await ctx.close()


async def phone(b):
    ctx, pg, errs = await fresh(b, viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    nav = await pg.locator("#nav").bounding_box()
    check(nav and nav["y"] + nav["height"] >= 840 and nav["width"] >= 389, "390 px: the destinations sit in a bottom bar")
    await pg.click("#v-today [data-start]")
    await pg.click("#v-today form.logf [data-min='40']")
    await pg.fill("#v-today form.logf textarea", "On the bus: flashcards")
    await pg.click("#v-today form.logf button[type=submit]")
    s = await state(pg)
    check(any(x.get("log") for x in s["progress"].values()), "390 px: start and log a session from Today in four taps")
    await pg.click("#v-today .livecard [data-open]")
    box = await pg.locator("#panel").bounding_box()
    check(box["width"] >= 389 and box["y"] <= 1, "390 px: the drawer fills the screen")
    over = await pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check(over <= 0, f"390 px: no horizontal overflow ({over}px)")
    check(errs == [], f"no JS errors ({errs})")
    await ctx.close()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        await today_flow(b)
        await route(b)
        await phone(b)
        await b.close()
    print(f"\n{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
