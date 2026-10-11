"""Run from the repo root: python -m pytest tests/"""
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.brief import load_facts, make_brief, passes, reason_hi
from backend.main import app, brief

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


def test_brief_without_key_uses_checked_template(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    brief.cache_clear()
    for lang in ["en", "hi"]:
        b = client.get(f"/brief?lang={lang}").json()
        assert b["source"] == "template" and passes(b["checks"])
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
