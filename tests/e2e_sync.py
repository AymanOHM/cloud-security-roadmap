"""Browser tests for opt-in sync through a GitHub Gist (Nov 2026). GitHub is faked: no network is used.
Build first: python3 tools/build.py. Needs Playwright + Chromium (see tests/e2e_smoke.py).
Run: python3 tests/e2e_sync.py   (exit code 1 on any failure)

What it proves:
- With sync off, the app makes no network request at all.
- Connecting with no gist creates a secret one holding this browser's progress; a second browser
  ("device") connecting with the same account finds that gist and merges its own progress in, losing nothing.
- A change on one device reaches the other; so do cleared fields, removed sessions and a reset
  (an edit the resetting device never saw is kept, not deleted).
- Different fields changed on both devices are both kept; differing notes are joined.
- The token never appears in progress or in an export; a gist holding foreign content is never overwritten.
- A rejected token is reported and nothing local is lost.
"""
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright
from nav import open_view

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "dist" / "index.html").as_uri()
KEY = "ntidebi-roadmap-v2"
FILE = "ntidebi-roadmap-progress.json"
TOKEN = "github_pat_TEST_ONLY_0000"
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


class FakeGitHub:
    """Just enough of the Gists API: list, create, get, patch. Shared by every 'device'."""

    def __init__(self):
        self.gists = {}
        self.calls = []
        self.reject = False

    async def handle(self, route):
        req = route.request
        path = req.url.split("api.github.com", 1)[1]
        self.calls.append((req.method, path))
        cors = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "GET,POST,PATCH,OPTIONS"}
        if req.method == "OPTIONS":
            return await route.fulfill(status=204, headers=cors)
        if self.reject or req.headers.get("authorization") != "Bearer " + TOKEN:
            return await route.fulfill(status=401, headers=cors, json={"message": "Bad credentials"})
        body = json.loads(req.post_data) if req.post_data else None
        if req.method == "GET" and path.startswith("/gists?"):
            return await route.fulfill(headers=cors, json=[self.view(i) for i in self.gists])
        if req.method == "POST" and path == "/gists":
            gid = f"g{len(self.gists) + 1}"
            self.gists[gid] = {"public": body["public"], "files": {k: v["content"] for k, v in body["files"].items()}}
            return await route.fulfill(status=201, headers=cors, json=self.view(gid))
        gid = path.split("/gists/", 1)[1].split("?")[0]
        if gid not in self.gists:
            return await route.fulfill(status=404, headers=cors, json={"message": "Not Found"})
        if req.method == "PATCH":
            for k, v in body["files"].items():
                self.gists[gid]["files"][k] = v["content"]
        return await route.fulfill(headers=cors, json=self.view(gid))

    def view(self, gid):
        return {"id": gid, "files": {k: {"filename": k, "content": c, "truncated": False, "raw_url": ""}
                                     for k, c in self.gists[gid]["files"].items()}}

    def progress(self):
        (g,) = self.gists.values()
        return json.loads(g["files"][FILE])["progress"]


async def device(b, gh, name):
    ctx = await b.new_context(accept_downloads=True)
    await ctx.route("https://api.github.com/**", gh.handle)
    net = []
    ctx.on("request", lambda r: net.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
    pg = await ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(f"{name}: {e}"))
    await pg.goto(URL)
    await pg.wait_for_timeout(200)
    return pg, net, errs


async def connect(pg):
    await open_view(pg, "data")
    await pg.fill("#synctok", TOKEN)
    await pg.click("#syncform button[type=submit]")
    await pg.wait_for_selector("#syncnow", timeout=5000)


async def sync(pg):
    await pg.evaluate("syncNow()")
    await pg.wait_for_function("!syncBusy && syncState !== 'pending'")


async def prog(pg, cid):
    return await pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}')).progress[{json.dumps(cid)}] || null")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        gh = FakeGitHub()
        a, net_a, errs = await device(b, gh, "A")
        ids = await a.evaluate("ALL.slice(0,6)")
        c1, c2, c3, c4 = ids[:4]

        # Sync off: no network at all, even after edits.
        await a.evaluate(f"setStatus('{c1}','ip'); setField('{c1}','notes','from A')")
        await a.wait_for_timeout(3000)
        check(net_a == [], "sync off: no network request")

        # A connects: a secret gist is created holding A's progress.
        await connect(a)
        check(len(gh.gists) == 1 and list(gh.gists.values())[0]["public"] is False, "connect creates one secret gist")
        check(gh.progress().get(c1, {}).get("notes") == "from A", "gist holds this browser's progress")
        tok_in_state = await a.evaluate(f"localStorage.getItem('{KEY}').includes('{TOKEN}')")
        check(not tok_in_state, "token is not stored in progress")

        # B has its own local progress, connects, finds the same gist; both sides kept.
        bb, _, errs_b = await device(b, gh, "B")
        await bb.evaluate(f"setStatus('{c2}','done')")
        await connect(bb)
        check(len(gh.gists) == 1, "second device finds the existing gist instead of making another")
        check((await prog(bb, c1) or {}).get("notes") == "from A", "B pulled A's progress")
        check(gh.progress().get(c2, {}).get("status") == "done", "B's own progress went to the gist")
        await sync(a)
        check((await prog(a, c2) or {}).get("status") == "done", "A pulled B's progress")

        # Edit on A travels to B automatically (debounced push), then B pulls.
        await a.evaluate(f"logSession('{c3}',{{min:30,text:'subnets'}})")
        await a.wait_for_function("syncState === 'ok' && !syncBusy", timeout=8000)
        await sync(bb)
        log = (await prog(bb, c3) or {}).get("log", [])
        check(len(log) == 1 and log[0]["text"] == "subnets", "a logged session reaches the other device")

        # Deletions travel: clear notes on B, remove the session on B.
        await bb.evaluate(f"setField('{c1}','notes','')")
        await bb.evaluate(f"removeSession('{c3}',0)")
        await sync(bb)
        await sync(a)
        check("notes" not in (await prog(a, c1) or {}), "a cleared field stays cleared on the other device")
        check(await prog(a, c3) is None, "a removed session stays removed on the other device")

        # Concurrent edits to different fields of one competency: both kept; differing notes joined.
        await a.evaluate(f"setField('{c4}','level','E2'); setField('{c4}','notes','A note')")
        await bb.evaluate(f"setField('{c4}','link','https://example.com/x'); setField('{c4}','notes','B note')")
        await sync(a)
        await sync(bb)
        await sync(a)
        ea, eb = await prog(a, c4), await prog(bb, c4)
        check(ea == eb, "both devices converge on the same entry")
        check(ea.get("level") == "E2" and ea.get("link") == "https://example.com/x", "different fields from both devices kept")
        check("A note" in ea.get("notes", "") and "B note" in ea.get("notes", ""), "conflicting notes are joined, not lost")

        # Export never contains the token.
        await open_view(a, "data")
        async with a.expect_download() as dl:
            await a.click("#exp")
        exported = Path(await (await dl.value).path()).read_text()
        check(TOKEN not in exported, "export does not contain the token")

        # Rejected token: reported, nothing local lost.
        gh.reject = True
        await a.evaluate(f"setStatus('{c1}','done')")
        await sync(a)
        st = await a.evaluate("SY.lastError || ''")
        check("rejected the token" in st, "a rejected token is reported")
        check(await a.locator('.notice[data-n="sync"]').count() == 1, "a sync problem shows a notice")
        check((await prog(a, c1) or {}).get("status") == "done", "local change kept while sync fails")
        gh.reject = False
        await sync(a)
        check(gh.progress().get(c1, {}).get("status") == "done", "the change syncs once the token works again")

        # Reset on one device resets the others (it's confirmed in the dialog). B first pulls A's latest:
        # an edit B has never seen is kept rather than deleted by B's reset.
        await sync(bb)
        bb.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await open_view(bb, "data")
        async with bb.expect_download():
            await bb.click("#rst")
        await bb.wait_for_function("syncState === 'ok' && !syncBusy", timeout=8000)
        await sync(a)
        check(await a.evaluate("Object.keys(S.progress).length") == 0, "a reset reaches the other device")

        # Foreign content in the gist is never overwritten.
        (g,) = gh.gists.values()
        g["files"][FILE] = '{"hello":"not progress"}'
        await a.evaluate(f"setStatus('{c2}','ip')")
        await sync(a)
        check(g["files"][FILE] == '{"hello":"not progress"}', "a gist with foreign content is left untouched")
        check("isn't tracker progress" in await a.evaluate("SY.lastError || ''"), "and the problem is reported")

        # Disconnect removes the token, keeps progress.
        a.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await open_view(a, "data")
        await a.click("#syncoff")
        check(await a.evaluate("localStorage.getItem('ntidebi-sync')") is None, "disconnect removes the token")
        check((await prog(a, c2) or {}).get("status") == "ip", "disconnect keeps local progress")

        check(not errs and not errs_b, "no page errors " + "; ".join(errs + errs_b))
        await b.close()
    print(f"\n{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


asyncio.run(main())
