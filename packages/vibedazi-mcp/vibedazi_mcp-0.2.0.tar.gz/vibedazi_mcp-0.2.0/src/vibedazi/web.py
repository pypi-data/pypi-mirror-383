import json
import os
from pathlib import Path
from typing import Any, Dict
import importlib.resources as resources

from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
import uvicorn


ROOT = Path(os.getcwd()).resolve()
VIBE = ROOT / ".vibe-dazi"


async def api_index(request):
    index = VIBE / "index.jsonl"
    rows = []
    if index.exists():
        with index.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
    return JSONResponse({"items": rows})


async def api_round(request):
    # path like rounds/2025-10/round-...json
    path = request.path_params.get("path")
    fp = VIBE / path
    if not fp.exists() or not fp.is_file():
        return JSONResponse({"error": "not_found"}, status_code=404)
    return FileResponse(str(fp))


async def api_flight_log(request):
    fp = VIBE / "flight-log.md"
    if not fp.exists():
        return JSONResponse({"items": []})
    date = None
    items = []
    try:
        with fp.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if line.startswith("## "):
                    date = line[3:].strip()
                    continue
                if line.startswith("- "):
                    # entry headline line
                    rest = line[2:].strip()
                    # format: "HH:MM:SSZ [BADGE] headline — scope"
                    time_part = rest.split(" ", 1)[0]
                    rem = rest[len(time_part):].strip()
                    badge = None
                    if rem.startswith("["):
                        b_end = rem.find("]")
                        if b_end != -1:
                            badge = rem[1:b_end]
                            rem = rem[b_end+1:].strip()
                    headline = rem
                    scope = None
                    if " — " in headline:
                        headline, scope = headline.split(" — ", 1)
                    items.append({
                        "date": date,
                        "time": time_part,
                        "badge": badge,
                        "headline": headline,
                        "scope": scope,
                        "details": [],
                    })
                elif line.startswith("  - ") and items:
                    items[-1]["details"].append(line[4:].strip())
    except Exception:
        items = []
    return JSONResponse({"items": items})


routes = [
    Route("/api/index", api_index),
    Route("/api/round/{path:path}", api_round),
    Route("/api/flight-log", api_flight_log),
]


def _static_dir() -> Path:
    """Return path to packaged static assets.

    Prefer package resources (installed with the distribution). If not found,
    fall back to `ROOT/vibeDazi/static` for local dev.
    """
    try:
        pkg_static = resources.files("vibedazi").joinpath("static")
        p = Path(str(pkg_static))
        if p.exists():
            return p
    except Exception:
        pass
    # Local dev fallback
    return ROOT / "vibeDazi" / "static"


def main() -> None:
    app = Starlette(routes=routes)
    static_dir = _static_dir()
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    uvicorn.run(app, host="127.0.0.1", port=8787)


if __name__ == "__main__":
    main()

