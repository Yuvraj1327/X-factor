"""Preview what a new readings file would change, without saving anything.

The officer (or MPPCB) uploads next year's CSV; the real pipeline runs on a copy:
read -> column check -> merge with existing readings -> clean -> source check -> re-rank.
Each step reports its real duration. Nothing is written to disk, so a public URL cannot alter the data.
"""
import io
import time
import warnings

import pandas as pd

from backend import clean, facts

MAX_BYTES = 2 * 1024 * 1024


def _step(steps, name_hi, name_en, fn):
    t = time.perf_counter()
    try:
        detail, ok = fn(), True
    except ValueError as e:
        detail, ok = str(e), False
    steps.append({"name": f"{name_hi} / {name_en}", "ok": ok, "ms": round((time.perf_counter() - t) * 1000, 1),
                  "detail": detail})
    return ok


def preview(data: bytes):
    steps, warn, state = [], [], {}
    if len(data) > MAX_BYTES:
        return {"ok": False, "steps": [], "warnings": [], "error": "File larger than 2 MB"}

    def read():
        try:
            state["new"] = pd.read_csv(io.BytesIO(data))
        except Exception as e:
            raise ValueError(f"Not a readable CSV: {e}")
        n = state["new"]
        return f"{len(n)} rows, {len(n.columns)} columns"

    def columns():
        missing = sorted(set(clean.REQUIRED) - set(state["new"].columns))
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}. Use the same columns as the 2023-2025 file.")
        new = state["new"][clean.REQUIRED]
        years = sorted(new.year.dropna().astype(int).unique().tolist())
        return f"All {len(clean.REQUIRED)} columns present · years {years} · {new.site.nunique()} sites"

    def merge():
        old = clean.load_raw()
        both = pd.concat([old, state["new"][clean.REQUIRED]], ignore_index=True)
        dupes = both[both.duplicated(clean.KEY, keep=False) & (both.index >= len(old))]
        if len(dupes):
            first = dupes.iloc[0]
            raise ValueError(f"{len(dupes)} readings already exist in the 2023-2025 data, e.g. "
                             f"{first.site}, {first.festival} {int(first.year)}, {first.phase}, {first.parameter}")
        state["raw"] = both
        return f"{len(old)} existing + {len(state['new'])} new = {len(both)} readings"

    def cleaning():
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            out = clean.clean(state["raw"])
        warn.extend(str(w.message) for w in caught)
        new_years = set(state["new"].year.dropna().astype(int))
        part = out[out.year.isin(new_years)]
        state["clean"] = out
        counts = part.status.value_counts().to_dict()
        return (f"New data: {counts.get('measured', 0)} measured, {counts.get('bdl', 0)} below detection, "
                f"{counts.get('missing', 0)} missing (each with a reason)")

    def sources():
        out = state["clean"]
        no_pdf = sorted(out[(out.status == "measured") & (out.report_file == "")].year.unique().tolist())
        if no_pdf:
            warn.append(f"No report PDF for {no_pdf}: add reports/<year>_*.pdf so every number links to its page.")
            return f"Report PDF missing for {no_pdf} (numbers cannot link to a page yet)"
        return "Every measured reading points to a report PDF and page"

    def rerank():
        # Round-trip through CSV so types match the committed clean file exactly.
        df = pd.read_csv(io.StringIO(state["clean"].to_csv(index=False)))
        new = facts.build(df)
        old = {g["site"]: g for g in facts.build()["ghats"]}
        state["ranking"] = [{"rank": g["rank"], "site": g["site"], "tier": g["tier"], "points": g["points"],
                             "prev_rank": old.get(g["site"], {}).get("rank"), "prev_tier": old.get(g["site"], {}).get("tier"),
                             "untested_latest_durga": g["untested_latest_durga"]} for g in new["ghats"]]
        state["latest_durga"] = new["latest_durga"]
        moved = sum(1 for r in state["ranking"] if r["prev_rank"] != r["rank"])
        return f"{len(new['ghats'])} ghats re-ranked · {moved} changed position · latest Durga now {new['latest_durga']}"

    for args in [("फ़ाइल पढ़ी", "File read", read), ("कॉलम जाँच", "Column check", columns),
                 ("पुराने डेटा से मिलान", "Merge with 2023-2025 data", merge), ("सफ़ाई", "Cleaning", cleaning),
                 ("स्रोत जाँच", "Source check", sources), ("नई रैंकिंग", "Re-rank", rerank)]:
        if not _step(steps, *args):
            return {"ok": False, "steps": steps, "warnings": warn, "error": steps[-1]["detail"]}
    return {"ok": True, "saved": False, "steps": steps, "warnings": warn,
            "latest_durga": state["latest_durga"], "ranking": state["ranking"]}
