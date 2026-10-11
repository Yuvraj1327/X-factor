"""Step 4: HTTP API for the officer dashboard.

GET /ranking            ranked ghats with reasons, evidence rows and PDF page links (data/clean/ranking.json)
GET /brief?lang=en|hi&format=page|whatsapp   forwardable brief, checked; Claude if ANTHROPIC_API_KEY is set
GET /reports/<file>.pdf the MPPCB source reports; evidence links add #page=N
GET /health

Run from the repo root: uvicorn backend.main:app --reload   (docs at /docs)
"""
import json
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.brief import ROOT, make_brief

RANKING = ROOT / "data" / "clean" / "ranking.json"

app = FastAPI(title="Visarjan Ghat Watch API",
              description="Bhopal immersion ghats ranked by MPPCB water-quality readings, for the BMC visarjan officer.")
# Public, read-only data: any UI origin may call it.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])
app.mount("/reports", StaticFiles(directory=ROOT / "reports"), name="reports")


@lru_cache
def ranking(mtime):
    return json.loads(RANKING.read_text())


@lru_cache
def brief(lang, fmt, mtime):
    # ponytail: one cached brief per data version; Claude is called at most once per language per deploy.
    return make_brief(lang, fmt)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ranking")
def get_ranking():
    return ranking(RANKING.stat().st_mtime)


@app.get("/brief")
def get_brief(lang: Literal["en", "hi"] = "en", format: Literal["page", "whatsapp"] = "page",
              refresh: bool = Query(False, description="Regenerate instead of using the cached brief")):
    mtime = RANKING.stat().st_mtime
    if refresh:
        brief.cache_clear()
    return brief(lang, format, mtime)
