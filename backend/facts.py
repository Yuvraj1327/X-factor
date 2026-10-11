"""Step 3: cleaned readings -> ranked, traceable facts per ghat.

All maths happens here, in plain pandas. Two outputs:
- data/clean/ranking.json   full facts for the UI (/ranking): every reason with its evidence rows
- data/clean/llm_input.json compact summary for the brief (/brief); the LLM only rewords it

Run from the repo root (after backend/clean.py): python backend/facts.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
CPCB = ROOT / "data" / "context" / "cpcb_water_quality_criteria.csv"
VISARJAN_DATE = "2026-10-20"
PHASES = ["pre", "during", "after"]

# Points per signal. Metals are left out on purpose: units are not printed and labs disagree ~1000x.
POINTS = {"oxygen_below_2_ever": 3, "oxygen_below_4": 2, "oxygen_below_5": 1, "oxygen_drop": 2, "not_recovered": 1}
# ponytail: fixed cut-offs tuned on 2023-25 data; recalibrate once 2026 readings arrive.
TIERS = [(20, "HIGH"), (12, "MEDIUM"), (0, "WATCH")]

NOT_IN_DATA = [
    "No coliform (bacteria) test at the ghats, so bathing safety from germs is unknown",
    "No water temperature and no time of sampling",
    "Units are not printed in the MPPCB immersion reports; standard units are assumed",
    "One sample per phase per festival; a single reading is not a trend",
    "No idol counts or crowd figures",
    "Newest readings are from 2025; nothing yet for 2026",
    "The data shows readings against limits; it does not show health effects",
    "The immersion reports print BOD without the test method; the lake reports use BOD (3 days, 27°C), not the "
    "5-day 20°C BOD of the CPCB limit (lake report 2025-26 p.9). BOD is shown against the limit but not scored",
    "The data cannot separate immersion from sewage as the cause of low oxygen",
]
HOW_RANKED = ("Ranked on dissolved oxygen only: readings below 5, 4 and 2 mg/l, drops of more than 2 mg/l during "
              "immersion, and no recovery a week later. BOD is shown but not scored because it is above the limit "
              "at almost every ghat. Metals are not scored because units are not printed and labs disagree. "
              "Ghats with fewer readings (temporary kunds, untested festivals) can score lower than their real risk; "
              "read the Not tested reasons. A ghat with near-zero oxygen on record that was not tested in the latest "
              "Durga is raised to HIGH. Equal points in the same tier are a tie; of tied ghats, the one near the "
              "Upper Lake water-supply intakes is listed first.")


def limits():
    c = pd.read_csv(CPCB)
    get = lambda cls, p: c[(c["class"] == cls) & (c.parameter.str.startswith(p))].limit.item()
    return {"class": "B (organised outdoor bathing)",
            "why": "People enter the water at immersion ghats, so the bathing standard applies.",
            "oxygen_min": float(get("B", "Dissolved oxygen")), "bod_max": float(get("B", "BOD")),
            "fish_oxygen_min": float(get("D", "Dissolved oxygen"))}


def evidence(r):
    page = None if pd.isna(r.source_page) else int(r.source_page)
    return {"year": int(r.year), "festival": r.festival, "phase": r.phase, "parameter": r.parameter,
            "value": None if pd.isna(r.value) else float(r.value), "status": r.status,
            "page": page, "pdf": f"/{r.report_file}#page={page}" if page else None,
            **({"quality_flag": r.quality_flag} if isinstance(r.quality_flag, str) and r.quality_flag else {})}


def pages(rows):
    return sorted({f"{int(r.year)} p.{int(r.source_page)}" for r in rows.itertuples() if pd.notna(r.source_page)})


def events_table(do):
    t = do.pivot_table(index=["year", "festival"], columns="phase", values="value")
    return t.reindex(columns=PHASES)


def is_batch_flag(flag):
    """Festival-wide problems are reported once in data_warnings, not repeated per ghat."""
    return "x other festivals" in flag or "identical to pre" in flag


def data_warnings(df):
    flagged = df.assign(flag=df.quality_flag.str.split("; ")).explode("flag")
    out = sorted({f.split(": ")[0] + ": possible unit or method change; treat these metal readings as unverified"
                  for f in flagged.flag.dropna() if "x other festivals" in f})
    copies = flagged[flagged.flag.fillna("").str.contains("identical to pre")]
    for (y, f), d in copies.groupby(["year", "festival"]):
        tested = df[(df.year == y) & (df.festival == f) & (df.status == "measured")].site.nunique()
        out.append(f"Metals in {f} {y}: after-immersion value identical to pre-immersion at {d.site.nunique()} of "
                   f"{tested} ghats ({len(d) // 2} metal series): possible copy in the report; treat as unverified")
    return out


def lower_lake_tag():
    """Tag Lower Lake ghats only if the lake report shows BOD above the bathing limit in every month."""
    path = CLEAN / "lake_baseline.csv"
    if not path.exists():
        return None
    lake = pd.read_csv(path)
    bod = lake[(lake.lake == "Lower Lake") & (lake.parameter == "BOD") & (lake.period_type == "month")]
    if bod.empty:
        return None
    above = int((bod.value > limits()["bod_max"]).sum())
    span = f"{pd.Timestamp(bod.period.min()):%b %Y} to {pd.Timestamp(bod.period.max()):%b %Y}"
    count = f"all {len(bod)}" if above == len(bod) else f"{above} of {len(bod)}"
    return (f"Lower Lake: BOD (3-day test) above 3 mg/l in {count} months sampled, {span}, festival and "
            f"non-festival months alike (lake report 2025-26 p.{int(bod.page.mode().iloc[0])})")


def ghat(site, g, lim, latest_durga, lower_tag=None):
    do = g[(g.parameter == "Dissolved oxygen") & (g.status == "measured")]
    bod = g[(g.parameter == "BOD") & (g.status == "measured")]
    ev = events_table(do)
    # Rounded to 0.1 mg/l (the reports' precision); a 0.5 mg/l tolerance keeps one-sample noise out.
    drops = ev[(ev.pre - ev.during).round(1) > 2]
    unrecovered = ev[(ev.pre - ev.after).round(1) > 0.5]
    both = ev.dropna(subset=["pre", "after"])

    below5, below4, below2 = do[do.value < lim["oxygen_min"]], do[do.value < lim["fish_oxygen_min"]], do[do.value < 2]
    latest = g[(g.year == latest_durga) & (g.festival == "Durga")]
    latest_do = latest[(latest.parameter == "Dissolved oxygen") & (latest.status == "measured")]
    star = g[g.missing_reason.fillna("").str.contains("report remark")]
    verify = g[g.quality_flag.fillna("").str.contains("verify|copy") & g.status.eq("measured")]
    verify = verify.assign(quality_flag=verify.quality_flag.str.split("; ").map(
        lambda fs: "; ".join(f for f in fs if not is_batch_flag(f))))
    verify = verify[verify.quality_flag != ""]

    counts = {"oxygen_below_2_ever": int(not below2.empty), "oxygen_below_4": len(below4),
              "oxygen_below_5": len(below5), "oxygen_drop": len(drops), "not_recovered": len(unrecovered)}
    points = sum(POINTS[k] * v for k, v in counts.items())
    tier = next(name for cut, name in TIERS if points >= cut)
    tier_note = ""
    # Missing is never clean: a known oxygen crash plus no test in the latest Durga cannot rank below HIGH.
    if not below2.empty and latest_do.empty and tier != "HIGH":
        tier = "HIGH"
        tier_note = (f"Raised to HIGH: near-zero oxygen on record and not tested in Durga {latest_durga}; "
                     "missing data is not treated as clean")

    reasons = []
    if len(do):
        # A "0 of N" claim is checked against every reading, so it cites all their pages.
        reasons.append({"text": f"Dissolved oxygen below the bathing limit of {lim['oxygen_min']:g} mg/l "
                                f"in {len(below5)} of {len(do)} readings",
                        "evidence": [evidence(r) for r in below5.itertuples()],
                        **({"pages": pages(do)} if below5.empty else {})})
    if not below2.empty:
        reasons.append({"text": f"Near-zero oxygen (below 2 mg/l) in {len(below2)} reading{'s' * (len(below2) != 1)}, "
                                f"lowest {below2.value.min():g} mg/l"
                                + (" (printed as 0 in the report; verify with MPPCB)" if (below2.value == 0).any() else ""),
                        "evidence": [evidence(r) for r in below2.itertuples()]})
    if latest_do.empty:
        why = latest.missing_reason.dropna().mode()
        reasons.append({"text": f"Not tested in Durga {latest_durga}"
                                + (f": {why.iloc[0]}" if len(why) else ""), "evidence": []})
    elif latest_do.value.min() < lim["oxygen_min"]:
        low = latest_do.sort_values("value").iloc[[0]]
        pre = latest_do[latest_do.phase == "pre"]
        already = len(pre) and pre.value.iloc[0] < lim["oxygen_min"] and low.phase.iloc[0] != "pre"
        if low.phase.iloc[0] == "pre":
            text = f"In Durga {latest_durga}, oxygen was already {low.value.iloc[0]:g} mg/l before immersion (pre-immersion sample)"
        else:
            text = (f"In Durga {latest_durga}, oxygen was {low.value.iloc[0]:g} mg/l in the {low.phase.iloc[0]}-immersion sample"
                    + (f", and already {pre.value.iloc[0]:g} mg/l before immersion" if already else ""))
        reasons.append({"text": text, "evidence": [evidence(r) for r in pd.concat([low, pre] if already else [low]).itertuples()]})
    if not drops.empty:
        names = ", ".join(f"{f} {y}" for y, f in drops.index)
        reasons.append({"text": f"Oxygen dropped by more than 2 mg/l during immersion in {names}",
                        "evidence": [evidence(r) for r in do[do.set_index(["year", "festival"]).index.isin(drops.index)
                                                             & do.phase.isin(["pre", "during"])].itertuples()]})
    if len(both):
        reasons.append({"text": f"One week after immersion, oxygen was more than 0.5 mg/l below the "
                                f"pre-immersion level in {len(unrecovered)} of {len(both)} festivals",
                        "evidence": [evidence(r) for r in do[do.set_index(["year", "festival"]).index.isin(unrecovered.index)
                                                             & do.phase.isin(["pre", "after"])].itertuples()],
                        **({"pages": pages(do[do.phase.isin(["pre", "after"])])} if unrecovered.empty else {})})
    if not star.empty:
        reasons.append({"text": "Temporary kund: no before or after sample in "
                                + ", ".join(sorted({f"{f} {y}" for y, f in zip(star.year, star.festival)}))
                                + " because the kund was not built yet or already dismantled (report remark)",
                        "evidence": [], "pages": pages(star)})
    if len(bod):
        reasons.append({"text": f"BOD above the bathing limit of {lim['bod_max']:g} mg/l (report does not print "
                                f"the BOD test method) "
                                f"in {int((bod.value > lim['bod_max']).sum())} of {len(bod)} readings",
                        "evidence": [evidence(r) for r in bod[bod.value > lim["bod_max"]].itertuples()]})
    for r in reasons:
        r.setdefault("pages", pages(pd.DataFrame(r["evidence"]).rename(columns={"page": "source_page"}))
                     if r["evidence"] else [])

    temporary = bool(g.temporary_kund.any())
    water_body = g.water_body.mode().iloc[0]
    tags = (["temporary kund"] if temporary else []) \
        + (["near Upper Lake, which has water-supply intake wells (lake report 2023-24 p.1-4)"
            + ("" if g.water_body_printed.eq(True).any() else "; Upper Lake inferred, not printed")]
           if water_body == "Upper Lake" else []) \
        + ([lower_tag] if water_body == "Lower Lake" and lower_tag else [])

    actions = []
    if tier != "WATCH" or not below4.empty:
        actions.append("Place aerators before 20 Oct and keep them running for the week after immersion")
    if latest_do.empty or temporary:
        actions.append("Ask MPPCB to sample before (by 18 Oct), during, and one week after (about 27 Oct)"
                       + ("; for a temporary kund, sample inside the kund while it stands" if temporary else ""))
    if not unrecovered.empty or not drops.empty:
        actions.append("Collect idols, flowers and left-over material within 48 hours "
                       "(CPCB guideline, 2025 report p.23)")
    if len(bod) and (bod.value > lim["bod_max"]).mean() > 0.5:
        actions.append("Keep separate bins for flowers and puja material so they stay out of the water")
    if temporary:
        actions.append("Line the temporary kund with a removable synthetic liner (CPCB guideline, 2025 report p.14)")
    if water_body == "Upper Lake":
        actions.append("Keep immersion out of the open Upper Lake, which has water-supply intake wells (lake report "
                       "2023-24 p.1-4); CPCB guidelines under NGT order OA 673/2018 call for temporary confined ponds "
                       "(2025 report p.2 and p.14)")
    if not verify.empty:
        actions.append("Ask MPPCB to confirm the flagged readings (see verify) and their units")

    coverage = g.groupby("status").size().to_dict()
    return {
        "site": site, "water_body": water_body, "points": points, "tier": tier, "tier_note": tier_note, "score_parts": counts,
        "tags": tags, "site_note": g.site_note.dropna().iloc[0] if g.site_note.notna().any() else "",
        "reasons": reasons, "actions": actions,
        "verify": [{"text": f"{r.parameter} {r.value:g} ({r.festival} {r.year}, {r.phase}): {r.quality_flag}",
                    **evidence(r)} for r in verify.itertuples()],
        "derived": {
            "oxygen_before_median": None if ev.pre.dropna().empty else round(float(ev.pre.median()), 2),
            "oxygen_lowest": None if do.empty else float(do.value.min()),
            "oxygen_drop_median": None if ev.dropna(subset=["pre", "during"]).empty
            else round(float((ev.during - ev.pre).median()), 2),
            "oxygen_recovery_median": None if both.empty else round(float((both.after - both.pre).median()), 2),
        },
        "coverage": {"rows": len(g), "measured": coverage.get("measured", 0), "bdl": coverage.get("bdl", 0),
                     "missing": coverage.get("missing", 0),
                     "missing_reasons": g[g.status == "missing"].missing_reason.value_counts().to_dict()},
        "untested_latest_durga": bool(latest_do.empty),
    }


def kund_vs_river():
    path = CLEAN / "statewide_clean.csv"
    if not path.exists():
        return None
    s = pd.read_csv(path)
    do = s[(s.parameter == "Dissolved oxygen") & (s.status == "measured") & s.quality_flag.isna()
           & s.site_type.isin(["kund_or_pond", "river"])]
    share = lambda d: round(float((d.value < 4).mean() * 100), 1)
    by_type = {t: {"readings": len(d), "below_4_pct": share(d),
                   **{f"{p}_below_4_pct": share(d[d.phase == p]) for p in PHASES}}
               for t, d in do.groupby("site_type")}
    k, r = by_type["kund_or_pond"], by_type["river"]
    return {"text": f"Across Madhya Pradesh, oxygen was below 4 mg/l in {k['below_4_pct']}% of kund readings "
                    f"vs {r['below_4_pct']}% of river readings. In kunds, {k['pre_below_4_pct']}% of pre-immersion samples "
                    f"were below 4 mg/l vs {k['after_below_4_pct']}% of samples one week after "
                    f"(site type read from site names; implausible readings left out).",
            "source": "MPPCB reports 2023-2025, statewide tables (site type from site names)", **by_type}


def lake_baseline():
    path = CLEAN / "lake_baseline.csv"
    if not path.exists():
        return []
    lake = pd.read_csv(path)
    year = lake[lake.source_file.str.contains("2025-26") & (lake.period_type == "annual_avg")]
    lines = []
    for (name, lk), d in year.groupby(["station", "lake"]):
        vals = {p: d[d.parameter == p] for p in ["Dissolved oxygen", "BOD", "Fecal coliform"]}
        if any(v.empty for v in vals.values()):
            continue
        months = lake[(lake.station == name) & (lake.period_type == "month") & lake.source_file.str.contains("2025-26")]

        def get(p):
            # Months at the test ceiling make the printed average a floor, not the true mean.
            capped = months[(months.parameter == p) & months.quality_flag.fillna("").str.contains("ceiling|censored: >")]
            return ("at least " if len(capped) else "") + f"{vals[p].value.iloc[0]:g}"

        lines.append({"station": name, "lake": lk,
                      "text": f"Routine lake monitoring, not at the ghats: {lk}, {name} (2025-26 average): oxygen {get('Dissolved oxygen')} mg/l, "
                              f"BOD {get('BOD')} mg/l, fecal coliform {get('Fecal coliform')} MPN/100 ml",
                      "pdf": f"/reports/{d.source_file.iloc[0]}#page={int(vals['BOD'].page.iloc[0])}"})
    return lines


def build():
    df = pd.read_csv(CLEAN / "bhopal_readings_clean.csv")
    lim = limits()
    latest_durga = int(df[(df.festival == "Durga") & (df.status == "measured")].year.max())
    lower_tag = lower_lake_tag()
    ghats = [ghat(site, g, lim, latest_durga, lower_tag) for site, g in df.groupby("site")]
    tier_order = {name: i for i, (_, name) in enumerate(TIERS)}
    ghats.sort(key=lambda x: (-tier_order[x["tier"]], x["points"], any("intake" in t for t in x["tags"])), reverse=True)
    for rank, x in enumerate(ghats, 1):
        x["rank"] = rank
        x["tied_with"] = [y["site"] for y in ghats if (y["points"], y["tier"]) == (x["points"], x["tier"]) and y is not x]
    return {"visarjan_date": VISARJAN_DATE, "how_ranked": HOW_RANKED, "standard": lim, "scoring": {"points": POINTS, "tiers": dict(
        (n, c) for c, n in TIERS)}, "latest_durga": latest_durga, "ghats": ghats,
        "context": {"kund_vs_river": kund_vs_river(), "lake_baseline": lake_baseline()},
        "not_in_data": NOT_IN_DATA, "data_warnings": data_warnings(df),
        "sources": sorted(df.report_file.dropna().unique().tolist())}


def llm_input(ranking):
    """The only thing the LLM sees: no raw rows, every number already computed and paged."""
    return {
        "visarjan_date": ranking["visarjan_date"],
        "how_ranked": ranking["how_ranked"],
        "standard": {k: ranking["standard"][k] for k in ["class", "why", "oxygen_min", "bod_max", "fish_oxygen_min"]},
        "ghats": [{"rank": g["rank"], "site": g["site"], "tier": g["tier"], "points": g["points"],
                   "tied_with": g["tied_with"], "tier_note": g["tier_note"], "tags": g["tags"],
                   "reasons": [{"text": r["text"], "pages": r["pages"]} for r in g["reasons"]],
                   "actions": g["actions"], "verify": [v["text"] for v in g["verify"]],
                   "site_note": g["site_note"]} for g in ranking["ghats"]],
        "context": [c for c in [ranking["context"]["kund_vs_river"] and ranking["context"]["kund_vs_river"]["text"]]
                    if c] + [l["text"] for l in ranking["context"]["lake_baseline"]],
        "not_in_data": ranking["not_in_data"],
        "data_warnings": ranking["data_warnings"],
    }


def to_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False, default=lambda o: o.item())


if __name__ == "__main__":
    ranking = build()
    (CLEAN / "ranking.json").write_text(to_json(ranking))
    (CLEAN / "llm_input.json").write_text(to_json(llm_input(ranking)))
    for g in ranking["ghats"]:
        print(f"{g['rank']}. {g['tier']:6} {g['points']:3}  {g['site']:40} {', '.join(g['tags'])}")
    print("context lines:", len(llm_input(ranking)["context"]))
