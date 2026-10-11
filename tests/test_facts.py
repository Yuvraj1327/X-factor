"""Run from the repo root: python -m pytest tests/"""
import json
import re

import pandas as pd

from backend.facts import ROOT, build, llm_input, to_json

CLEAN = pd.read_csv(ROOT / "data" / "clean" / "bhopal_readings_clean.csv")
RANKING = build()
LLM = llm_input(RANKING)
BY_SITE = {g["site"]: g for g in RANKING["ghats"]}


def test_ranking_order_and_tiers():
    top = RANKING["ghats"][:2]
    assert [g["site"] for g in top] == ["Bairagarh (Sant Hirdaram) kund", "Malikhedi kund"]
    assert all(g["tier"] == "HIGH" for g in top)
    assert [g["rank"] for g in RANKING["ghats"]] == list(range(1, 8))


def test_every_evidence_number_matches_clean_data():
    keyed = CLEAN.set_index(["year", "festival", "site", "phase", "parameter"])
    for g in RANKING["ghats"]:
        for r in g["reasons"]:
            for e in r["evidence"]:
                row = keyed.loc[(e["year"], e["festival"], g["site"], e["phase"], e["parameter"])]
                assert row.value == e["value"] and row.source_page == e["page"]
                assert (ROOT / e["pdf"].lstrip("/").split("#")[0]).exists()


def test_counts_in_reason_text_match_evidence():
    for g in RANKING["ghats"]:
        for r in g["reasons"]:
            m = re.search(r"in (\d+) of \d+ readings", r["text"])
            if m and r["evidence"]:
                assert int(m.group(1)) == len(r["evidence"]), r["text"]


def test_untested_is_never_clean():
    for site in ["Bairagarh (Sant Hirdaram) kund", "Malikhedi kund"]:
        g = BY_SITE[site]
        assert g["untested_latest_durga"]
        assert any(r["text"].startswith("Not tested in Durga") for r in g["reasons"])
        assert any("MPPCB to sample" in a for a in g["actions"])


def test_metals_do_not_change_points():
    no_metals = CLEAN[~CLEAN.parameter.isin(["Chromium", "Lead", "Zinc", "Copper"])]
    from backend import facts
    lim, latest = facts.limits(), RANKING["latest_durga"]
    for site, g in no_metals.groupby("site"):
        assert facts.ghat(site, g, lim, latest)["points"] == BY_SITE[site]["points"]


def test_llm_input_has_no_new_numbers_and_no_health_words():
    numbers = lambda obj: set(re.findall(r"\d+(?:\.\d+)?", to_json(obj)))
    assert numbers(LLM) <= numbers(RANKING) | {"0"}
    text = to_json(LLM).lower()
    for word in ["disease", "illness", "poison", "toxic", "cancer", "unsafe to drink", "infection"]:
        assert word not in text, word


def test_untested_crash_is_raised_not_hidden():
    g = BY_SITE["Malikhedi kund"]
    assert g["tier"] == "HIGH" and g["tier_note"].startswith("Raised to HIGH")
    assert all(not x["tier_note"] for x in RANKING["ghats"] if not x["untested_latest_durga"])
