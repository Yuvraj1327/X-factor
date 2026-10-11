"""Run from the repo root: python -m pytest tests/"""
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.brief import load_facts, make_brief, passes, reason_hi
from backend.main import app, brief
from backend.brief import ROOT as ROOT_DIR

client = TestClient(app)
FACTS = load_facts()


def test_ranking_endpoint():
    r = client.get("/ranking").json()
    assert len(r["ghats"]) == 7 and r["ghats"][0]["rank"] == 1
    assert all(g["reasons"] for g in r["ghats"])


def test_evidence_links_serve_the_pdf():
    link = next(e["pdf"] for g in client.get("/ranking").json()["ghats"] for r in g["reasons"] for e in r["evidence"])
    resp = client.get(link.split("#")[0])
    assert resp.status_code == 200 and resp.headers["content-type"] == "application/pdf"


def test_brief_is_served_without_calling_claude(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    brief.cache_clear()
    for lang in ["en", "hi"]:
        b = client.get(f"/brief?lang={lang}").json()
        assert passes(b["checks"])
        w = client.get(f"/brief?lang={lang}&format=whatsapp").json()
        assert passes(w["checks"]) and len(w["text"]) <= 1000


def test_every_reason_has_hindi():
    assert all(reason_hi(r["text"]) != r["text"] for g in FACTS["ghats"] for r in g["reasons"])


class FakeClaude:
    """Stands in for anthropic.Anthropic(); returns queued texts."""
    def __init__(self, *texts):
        self.texts = list(texts)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        text = self.texts.pop(0)
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])


def test_claude_brief_used_when_checks_pass():
    b = make_brief("en", client=FakeClaude("Bairagarh kund: oxygen 0 mg/l (2023 p.60). Visarjan 20 Oct 2026."))
    assert b["source"] == "claude"


def test_invented_number_or_health_claim_falls_back_to_template():
    b = make_brief("en", client=FakeClaude("Oxygen was 0.37 mg/l.", "The water is safe to bathe in."))
    assert b["source"] == "template" and "checks failed" in b["llm_error"]


def test_retry_fixes_a_bad_first_draft():
    b = make_brief("en", client=FakeClaude("Oxygen was 0.37 mg/l.", "Oxygen was 0 mg/l (2023 p.60)."))
    assert b["source"] == "claude"


def test_no_public_refresh():
    assert "refresh" not in client.get("/openapi.json").text


def test_root_redirects_to_docs():
    assert client.get("/", follow_redirects=False).headers["location"] == "/docs"


def test_briefs_lead_with_not_tested_and_new_claim_words_blocked():
    from backend.brief import template_brief, whatsapp_brief, banned_words
    for text in [template_brief(FACTS, "en"), whatsapp_brief(FACTS, "en")]:
        assert "Not tested in Durga" in text.split("2. ")[0]          # the #1 ghat says it
    assert banned_words("caused by idol immersion; harmful") and banned_words("पानी दूषित है")


def test_upload_preview_runs_pipeline_and_saves_nothing():
    from backend.facts import CLEAN
    before = (CLEAN / "bhopal_readings_clean.csv").read_bytes()
    demo = (ROOT_DIR / "frontend" / "demo_2026_ganesh_MADE_UP_VALUES.csv").read_bytes()
    r = client.post("/upload/preview", content=demo, headers={"content-type": "text/csv"}).json()
    assert r["ok"] and r["saved"] is False and len(r["steps"]) == 6 and all(s["ok"] for s in r["steps"])
    assert len(r["ranking"]) == 7 and any("No report PDF for [2026]" in w for w in r["warnings"])
    assert (CLEAN / "bhopal_readings_clean.csv").read_bytes() == before


def test_upload_preview_rejects_duplicates_and_bad_columns():
    old = (ROOT_DIR / "data" / "readings" / "bhopal_2023_2025.csv").read_bytes()
    r = client.post("/upload/preview", content=old).json()
    assert not r["ok"] and "already exist" in r["error"]
    r = client.post("/upload/preview", content=b"a,b\n1,2\n").json()
    assert not r["ok"] and "Missing columns" in r["error"]
