"""Navigation helper for the browser tests (UX redesign, Nov 2026).

The app has three destinations (Today, Roadmap, Plan) plus Data. Roadmap has four lenses (List, Board,
Route, Map) and Plan has six sections. Tests name a view the way the old tabs did ("flow", "kanban",
"checklist", "dash", ...) and this opens it the way a person would: the destination, then the lens or section.
"""
VIEW = {
    "today": ("today", None),
    "flow": ("roadmap", "map"), "map": ("roadmap", "map"),
    "kanban": ("roadmap", "board"), "board": ("roadmap", "board"),
    "checklist": ("roadmap", "list"), "list": ("roadmap", "list"),
    "route": ("roadmap", "route"),
    "paths": ("plan", "paths"), "projects": ("plan", "projects"), "certs": ("plan", "certs"),
    "compare": ("plan", "compare"), "time": ("plan", "time"), "skills": ("plan", "skills"),
    "dash": ("data", None), "data": ("data", None),
}


async def open_view(pg, v):
    top, sub = VIEW[v]
    await pg.click(f'[data-nav="{top}"]')
    if sub and top == "roadmap":
        await pg.click(f'#lenses [data-lens="{sub}"]')
    elif sub:
        await pg.click(f'#plannav [data-plan="{sub}"]')
    await pg.wait_for_timeout(60)
