"""Step 1: clean the Bhopal ghat readings.

Reads every CSV in data/readings/ (one file per batch of years, same columns as the
organisers' bhopal_ghats_2023_2025.csv) and writes data/clean/bhopal_readings_clean.csv.

No scoring and no limits here: this layer only makes the data honest and complete.
- every reading gets a status: measured | bdl | missing (missing is never clean)
- every gap is a row with a reason, including whole tables missing from a report
- doubtful values get a quality_flag instead of being dropped
- every row points to its report PDF and page

Run from the repo root: python backend/clean.py
"""
import math
import warnings
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
READINGS_DIR = ROOT / "data" / "readings"
REPORTS_DIR = ROOT / "reports"
OUT = ROOT / "data" / "clean" / "bhopal_readings_clean.csv"

KEY = ["year", "festival", "site", "phase", "parameter"]
REQUIRED = ["year", "festival", "site", "water_body", "phase", "parameter", "value", "unit_assumed",
            "flag", "value_as_printed", "parameter_as_printed", "site_as_printed",
            "site_match_confidence", "source_page"]
PHASES = ["pre", "during", "after"]
METALS = ["Chromium", "Lead", "Zinc", "Copper"]
BDL_FLAGS = {"BDL", "ND"}
STAR_REASON = {"*": "kund not built yet at pre-immersion sampling (report remark)",
               "**": "kund dismantled before post-immersion sampling (report remark)"}

# Checked by hand against the 2023-2025 PDFs:
# site -> (water body, word that shows the report printed that water body, note for the officer).
# The reports print the water body only in some tables, so "printed" is decided per row.
SITES = {
    "Bairagarh (Sant Hirdaram) kund": ("Upper Lake", "upper lake", ""),
    "Malikhedi kund": ("not printed", None, "Temporary kund; no water body printed in the reports."),
    "Prempura ghat": ("Upper Lake", None, "No water body printed; Upper Lake is inferred."),
    "Khatlapura ghat": ("Lower Lake", "lower lake", ""),
    "Rani Kamlapati ghat / Kamla Park kund": (
        "Lower Lake", "lower lake",
        "Ganesh tables say Kamla Park kund, Durga tables say Rani Kamlapati ghat (Lower Lake). "
        "May be two sampling points."),
    "Hathaikheda dam / kund": (
        "Hathaikheda dam", "dam",
        "Ganesh tables say visarjan kund, Durga tables say dam ghat. May be two sampling points."),
    "Shahpura lake ghat": ("Shahpura Lake", "lake", ""),
}

OUT_COLUMNS = ["year", "festival", "site", "water_body", "water_body_printed", "site_note",
               "temporary_kund", "phase", "parameter", "value", "unit_assumed", "status",
               "missing_reason", "quality_flag", "value_as_printed", "site_as_printed",
               "site_match_confidence", "source_page", "report_file"]


def load_raw(readings_dir=READINGS_DIR):
    frames = []
    for path in sorted(Path(readings_dir).glob("*.csv")):
        df = pd.read_csv(path)
        missing = set(REQUIRED) - set(df.columns)
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        frames.append(df[REQUIRED].assign(source_file=path.name))
    if not frames:
        raise FileNotFoundError(f"no CSV files in {readings_dir}")
    raw = pd.concat(frames, ignore_index=True)
    dupes = raw[raw.duplicated(KEY, keep=False)]
    if not dupes.empty:
        first = dupes.iloc[0]
        raise ValueError(f"{len(dupes)} duplicate readings across {sorted(dupes.source_file.unique())}, "
                         f"e.g. {dict(first[KEY])}")
    unknown = sorted(set(raw.site) - set(SITES))
    if unknown:
        warnings.warn(f"new sites not in SITES (add them after checking the report): {unknown}")
    return raw.drop(columns="source_file")


def report_file(year, festival, reports_dir=REPORTS_DIR):
    """reports/<year>_*.pdf; if a year has one PDF per festival, pick the one naming the festival."""
    found = sorted(Path(reports_dir).glob(f"{int(year)}_*.pdf"))
    if len(found) > 1:
        found = [p for p in found if festival.lower() in p.name.lower()]
        if len(found) != 1:
            raise ValueError(f"cannot tell which reports/{int(year)}_*.pdf holds {festival} tables")
    return str(found[0].relative_to(Path(reports_dir).parent)) if found else ""


def add_status(df):
    flag = df.flag.astype("string").str.strip()
    df["status"] = "measured"
    df.loc[df.value.isna() & flag.str.upper().isin(BDL_FLAGS), "status"] = "bdl"
    df.loc[df.value.isna() & ~flag.str.upper().isin(BDL_FLAGS).fillna(False), "status"] = "missing"

    missing = df.status.eq("missing")
    df["missing_reason"] = ""
    df.loc[missing & flag.eq("not sampled"), "missing_reason"] = "blank (_ or -) in report: not sampled or not reported"
    other = missing & flag.notna() & ~flag.isin(["not sampled", *STAR_REASON])
    df.loc[other, "missing_reason"] = "reported as " + flag[other]
    unparsed = missing & flag.isna()
    df.loc[unparsed, "missing_reason"] = "value not parsed, printed as: " + df.value_as_printed[unparsed].astype(str)
    # The report prints * / ** only once per column (on the pH row); it applies to the whole phase.
    star = flag.where(flag.isin(list(STAR_REASON))).groupby([df[c] for c in KEY[:4]]).transform("first")
    has_star = missing & star.notna()
    df.loc[has_star, "missing_reason"] = star[has_star].map(STAR_REASON)
    return df


def fill_gaps(df):
    """One row per site x event x phase x parameter from the site's first year on,
    so silent gaps become visible rows."""
    events = df[["year", "festival"]].drop_duplicates()
    grid = (events.merge(pd.DataFrame({"site": df.site.unique()}), how="cross")
            .merge(pd.DataFrame({"phase": PHASES}), how="cross")
            .merge(pd.DataFrame({"parameter": df.parameter.unique()}), how="cross"))
    first_year = df.groupby("site").year.min()
    grid = grid[grid.year >= grid.site.map(first_year)]
    full = grid.merge(df, on=KEY, how="left")

    added = full.status.isna()
    tables = set(map(tuple, df[["year", "festival", "site"]].drop_duplicates().values))
    in_event = set(map(tuple, df[["year", "festival", "parameter"]].drop_duplicates().values))

    def reason(r):
        if (r.year, r.festival, r.parameter) not in in_event:
            return "parameter not in this festival's tables"
        if (r.year, r.festival, r.site) not in tables:
            return "no table for this site in the report"
        return "not printed in the report"

    full.loc[added, "status"] = "missing"
    full.loc[added, "missing_reason"] = full[added].apply(reason, axis=1)
    # Added rows inside an existing table point to that table's page and printed site name.
    for col in ["source_page", "site_as_printed", "site_match_confidence"]:
        full[col] = full[col].fillna(full.groupby(["year", "festival", "site"])[col].transform("first"))
    units = df.dropna(subset=["unit_assumed"]).groupby("parameter").unit_assumed.first()
    full["unit_assumed"] = full.unit_assumed.fillna(full.parameter.map(units))
    return full


def add_site_info(df):
    meta = df.site.map(lambda s: SITES.get(s, (None, None, "New site: add it to SITES after checking the report.")))
    df["water_body"] = [m[0] or wb for m, wb in zip(meta, df.water_body)]
    df["site_note"] = [m[2] for m in meta]
    printed = df.site_as_printed.astype("string").str.lower()
    df["water_body_printed"] = [
        pd.NA if pd.isna(p) else (word is not None and word in p) for (_, word, _), p in zip(meta, printed)]
    df["temporary_kund"] = df.site.isin(df.loc[df.missing_reason.isin(STAR_REASON.values()), "site"])
    return df


def add_quality_flags(df):
    flags = pd.Series([[] for _ in range(len(df))], index=df.index)

    def flag(index, text):
        for i in index:
            flags[i].append(text)

    do = df.parameter.eq("Dissolved oxygen")
    metal = df.parameter.isin(METALS) & df.status.eq("measured")
    flag(df.index[do & df.value.eq(0)], "zero oxygen: verify with MPPCB")
    flag(df.index[do & (df.value > 10)], "unusually high oxygen: verify")
    # Single high paint-pigment reading; batch-wide shifts are caught by the event check below.
    flag(df.index[df.parameter.isin(["Lead", "Chromium"]) & (df.value > 0.5)],
         "unusually high metal, unit not printed: verify")

    # Same metal value at most sites of one festival = the lab's reporting floor, not a reading.
    m = df[metal]
    sites_in_event = df[df.status.ne("missing")].groupby(["year", "festival"]).site.nunique()
    need = (m.year.astype(str) + m.festival).map(
        {f"{y}{f}": max(3, math.ceil(0.7 * n)) for (y, f), n in sites_in_event.items()})
    with_value = m.groupby(["year", "festival", "parameter", "value"]).site.transform("nunique")
    floor = with_value[with_value >= need]
    for i in floor.index:
        flags[i].append(f"likely detection limit (same value at {int(floor[i])} sites)")

    # After-one-week identical to pre-immersion at one site = possible copy in the report.
    series = m.drop(index=floor.index).pivot_table(
        index=["year", "festival", "site", "parameter"], columns="phase", values="value")
    copied = series[series.get("pre").eq(series.get("after"))].index if {"pre", "after"} <= set(series) else []
    for key in copied:
        rows = m[(m[["year", "festival", "site", "parameter"]].apply(tuple, axis=1) == key)
                 & m.phase.isin(["pre", "after"])].index
        flag(rows, "after value identical to pre: possible copy in report")

    # Whole-festival metal level far from other years = possible unit or method change.
    med = m.groupby(["year", "festival", "parameter"]).value.median()
    for (y, f, p), v in med.items():
        others = med.drop((y, f, p)).xs(p, level="parameter")
        if len(others) and v > 5 * others.median():
            flag(m.index[(m.year == y) & (m.festival == f) & (m.parameter == p)],
                 f"{p} in {f} {y} runs {v / others.median():.0f}x other festivals: possible unit or method change, verify")

    df["quality_flag"] = flags.map("; ".join)
    return df


def clean(raw):
    df = add_status(raw.copy())
    df = fill_gaps(df)
    df = add_site_info(df)
    df["report_file"] = [report_file(y, f) for y, f in zip(df.year, df.festival)]
    df["source_page"] = df.source_page.astype("Int64")
    df = add_quality_flags(df)
    order = {p: i for i, p in enumerate(PHASES)}
    df = df.sort_values(KEY, key=lambda c: c.map(order) if c.name == "phase" else c)
    return df[OUT_COLUMNS].reset_index(drop=True)


def self_check(df, raw):
    assert not df.duplicated(KEY).any(), "duplicate readings"
    assert set(df.status) <= {"measured", "bdl", "missing"}
    assert df.loc[df.status.eq("measured"), "value"].notna().all()
    assert df.loc[df.status.ne("measured"), "value"].isna().all()
    assert df.loc[df.status.eq("missing"), "missing_reason"].ne("").all(), "missing row without a reason"
    assert (df.status != "missing").sum() == (raw.value.notna() | raw.flag.astype("string").str.strip()
                                             .str.upper().isin(BDL_FLAGS).fillna(False)).sum(), "lost readings"
    measured = df[df.status.eq("measured")]
    no_source = measured[measured.source_page.isna() | measured.report_file.eq("")]
    assert no_source.empty, f"readings without a report: add reports/<year>_*.pdf for years {sorted(no_source.year.unique())}"
    assert all((ROOT / f).exists() for f in measured.report_file.unique()), "report PDF missing"


if __name__ == "__main__":
    raw = load_raw()
    df = clean(raw)
    self_check(df, raw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(raw)} raw rows -> {len(df)} clean rows -> {OUT.relative_to(ROOT)}")
    print(df.status.value_counts().to_string())
    print(df[df.status.eq("missing")].missing_reason.value_counts().to_string())
    print("rows with quality flags:", (df.quality_flag != "").sum())
