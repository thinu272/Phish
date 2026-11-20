"""PhishGuard API.  Run:  uvicorn app.main:app --reload --port 8000"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import analytics as an
from .filters import Filters, get_filters
from .store import ROOT, get_store

app = FastAPI(title="PhishGuard SOC Dashboard API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])


def clean(o):
    """Make numpy / pandas values JSON-safe (NaN -> null)."""
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, pd.Timestamp): return o.strftime("%Y-%m-%d")
    return o


def respond(fn):
    def handler(f: Filters = Depends(get_filters)):
        return JSONResponse(clean(fn(get_store(), f)))
    return handler


@app.on_event("startup")
def _warm() -> None:
    get_store()  # load CSVs (and generate them on first run)


@app.get("/api/health")
def health():
    s = get_store()
    return {"status": "ok", "emails": len(s.E), "incidents": len(s.I)}


@app.get("/api/meta")
def meta():
    return JSONResponse(clean(an.meta(get_store())))


for _name, _fn in [("summary", an.summary), ("executive", an.executive), ("trends", an.trends),
                   ("threats", an.threats), ("users", an.users), ("incidents", an.incidents),
                   ("awareness", an.awareness)]:
    app.get(f"/api/{_name}", name=_name)(respond(_fn))

# --- serve the built React app (production mode): npm run build, then just run uvicorn ---
DIST = ROOT.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = DIST / path
        return FileResponse(f if f.is_file() else DIST / "index.html")
