"""Step 4: HTTP API for the officer dashboard.

GET /ranking            ranked ghats with reasons, evidence rows and PDF page links (data/clean/ranking.json)
GET /brief?lang=en|hi&format=page|whatsapp   forwardable brief: the reviewed, frozen brief (briefs.json) or the
                        checked template; never calls Claude at request time
GET /reports/<file>.pdf the MPPCB source reports; evidence links add #page=N
POST /upload/preview    run the pipeline on an uploaded readings CSV and show the new ranking (nothing is saved)
GET /health

Run from the repo root: uvicorn backend.main:app --reload   (docs at /docs)
"""
import json
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.brief import ROOT, served_brief
from backend.upload import MAX_BYTES, preview

RANKING = ROOT / "data" / "clean" / "ranking.json"

app = FastAPI(title="Visarjan Ghat Watch API",
              description="Bhopal immersion ghats ranked by MPPCB water-quality readings, for the BMC visarjan officer.")
# Public, read-only data: any UI origin may call it.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])
app.mount("/reports", StaticFiles(directory=ROOT / "reports"), name="reports")


@lru_cache
def ranking(mtime):
    return json.loads(RANKING.read_text())


@lru_cache
def brief(lang, fmt, mtime):
    return served_brief(lang, fmt)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ranking")
def get_ranking():
    return ranking(RANKING.stat().st_mtime)


@app.get("/brief")
def get_brief(lang: Literal["en", "hi"] = "en", format: Literal["page", "whatsapp"] = "page"):
    # Frozen briefs from data/clean/briefs.json: fast, identical every time, and no API spend on an open URL.
    return brief(lang, format, RANKING.stat().st_mtime)


@app.post("/upload/preview")
async def upload_preview(request: Request):
    """Body: a readings CSV (same columns as the 2023-2025 file). Runs the pipeline on a copy; saves nothing."""
    data = await request.body()
    if len(data) > MAX_BYTES:
        return {"ok": False, "steps": [], "warnings": [], "error": "File larger than 2 MB"}
    return preview(data)
