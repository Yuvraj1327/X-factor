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


def reason_texts(site):
    return [r["text"] for r in BY_SITE[site]["reasons"]]


def test_latest_durga_reason_names_phase_and_pre_immersion_state():
    rk = next(t for t in reason_texts("Rani Kamlapati ghat / Kamla Park kund") if t.startswith("In Durga"))
    assert "2.4 mg/l in the during-immersion sample" in rk and "already 2.5 mg/l before immersion" in rk
    sh = next(t for t in reason_texts("Shahpura lake ghat") if t.startswith("In Durga"))
    assert sh.startswith("In Durga 2025, oxygen was already 2.5 mg/l before immersion")
    pr = next(t for t in reason_texts("Prempura ghat") if t.startswith("In Durga"))
    assert "4.9 mg/l in the during-immersion sample" in pr and "already" not in pr


def test_zero_of_n_claims_cite_the_pages_checked():
    zero = [r for g in RANKING["ghats"] for r in g["reasons"] if re.search(r"\bin 0 of \d+", r["text"])]
    assert zero and all(r["pages"] and not r["evidence"] for r in zero)


def test_thresholds_use_rounded_values():
    # Bairagarh Durga 2024: 4.2 -> 2.2 is exactly 2.0, not "more than 2"; Malikhedi Durga 2024: 4.5 -> 4.0 is not "> 0.5".
    assert BY_SITE["Bairagarh (Sant Hirdaram) kund"]["score_parts"]["oxygen_drop"] == 0
    assert BY_SITE["Malikhedi kund"]["score_parts"]["not_recovered"] == 1


def test_aerator_action_follows_tier_or_low_oxygen():
    for g in RANKING["ghats"]:
        want = g["tier"] != "WATCH" or g["derived"]["oxygen_lowest"] < 4
        assert any("aerators" in a for a in g["actions"]) == want, g["site"]


def test_ties_and_points_are_explicit():
    for g in LLM["ghats"]:
        assert isinstance(g["points"], int)
        for other in g["tied_with"]:
            o = next(x for x in LLM["ghats"] if x["site"] == other)
            assert (o["points"], o["tier"]) == (g["points"], g["tier"]) and g["site"] in o["tied_with"]
    assert "tie" in LLM["how_ranked"] and "dissolved oxygen" in LLM["how_ranked"].lower()


def test_flags_and_sources_reach_the_llm():
    mk = next(g for g in LLM["ghats"] if g["site"] == "Malikhedi kund")
    assert any("10.4" in v and "unusually high oxygen" in v for v in mk["verify"])
    bg = next(g for g in LLM["ghats"] if g["site"] == "Bairagarh (Sant Hirdaram) kund")
    assert any("printed as 0" in r["text"] for r in bg["reasons"])
    assert any("lake report 2023-24 p.1-4" in t for t in bg["tags"])
    assert any("OA 673/2018" in a and "p.14" in a for a in bg["actions"])
    lower = [t for g in LLM["ghats"] for t in g["tags"] if t.startswith("Lower Lake")]
    assert lower and all("festival and non-festival months" in t and "before any" not in t for t in lower)


def test_lake_context_is_marked_and_statewide_junk_is_excluded():
    lake = [c for c in LLM["context"] if "Lake" in c and "Routine" in c]
    assert len(lake) == len(RANKING["context"]["lake_baseline"]) and all(c.startswith("Routine lake monitoring, not at the ghats") for c in lake)
    assert any("3 days, 27" in n and "lake report 2025-26 p.9" in n for n in LLM["not_in_data"])
    statewide = pd.read_csv(ROOT / "data" / "clean" / "statewide_clean.csv")
    assert statewide.quality_flag.fillna("").str.contains("implausible").sum() > 0
    assert "implausible readings left out" in LLM["context"][0]
