"""Clean the MPPCB statewide idol-immersion water tests (2023-2025).

Reads data/statewide/mp_immersion_sites_2023_2025.csv, drops unreadable sites,
removes page-split duplicates, adds status / site_type / bhopal_city / quality_flag,
and writes data/clean/statewide_clean.csv.

Run from the repo root:  .venv/bin/python backend/clean_statewide.py
"""
import re
from pathlib import Path

import pandas as pd

# Units are not printed in the source reports. Metal values differ ~1000x between
# regional labs (some print chromium 0.001-0.005, others lead flat 2-4.95), so
# metals (Lead, Zinc, Chromium, Copper) are NOT comparable across regional offices.
# Values are kept as printed; nothing is converted.

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/statewide/mp_immersion_sites_2023_2025.csv"
OUT = ROOT / "data/clean/statewide_clean.csv"
KEY = ["year", "festival", "site_as_printed", "phase", "parameter"]
COLUMNS = ["year", "festival", "regional_office", "site_as_printed", "site_type", "bhopal_city",
           "phase", "parameter", "value", "unit_assumed", "status", "quality_flag",
           "value_as_printed", "source_page"]

# "XL/W.comp/Ganesh" is a PDF header the parser used as the site name for ~20 unrelated
# tables in Indore/Dhar/Shahdol/Mandideep; the real site is unknown, same as needs_check.
JUNK_SITES = {"XL/W.comp/Ganesh"}

# Order matters: first match wins, so kund beats river beats lake.
SITE_TYPES = [
    # taal/tal = Hindi tank (Katora Taal, Hanumantal); bavdi = stepwell; sarover is a common misspelling
    ("kund_or_pond", r"kund|pond|tank|talab|talav|talai|sarovar|sarover|artificial|taal|tal\b|bavdi"),
    # "Chonda pool" is pul = bridge on the Asan river, not a pool
    ("river", r"river|nadi|sangam|narmada|tapti|pool"),
    # sagar = large tank (Karan Sagar, Gopi Kishan Sagar); bandh = embanked reservoir
    ("lake_or_dam", r"lake|dam|reservoir|jheel|jhil|jalashay|bandh|sagar"),
]
BHOPAL_GHATS = r"hirdaram|bairagarh|khatlapura|prempura|kamlapati|kamla park|hathaikheda|malikhedi|maalikhedi|shahpura"
NOT_BHOPAL = r"vidisha|sehore|rajgarh"


def site_type(name):
    name = name.lower()
    return next((t for t, pat in SITE_TYPES if re.search(pat, name)), "other")


def status(flag):
    if flag == "":
        return "measured"
    return "bdl" if flag in ("BDL", "ND") else "missing"  # not sampled, *, **, NA, na, DRY


def clean(raw):
    counts = {"rows_in": len(raw)}
    df = raw[(raw.needs_check != "yes") & ~raw.site_as_printed.isin(JUNK_SITES)].copy()
    counts["dropped_unreadable_site"] = counts["rows_in"] - len(df)

    df["source_page"] = df.source_page.astype(int)
    df = df.sort_values("source_page").drop_duplicates(KEY + ["value_as_printed"])
    counts["identical_dupes_removed"] = counts["rows_in"] - counts["dropped_unreadable_site"] - len(df)
    conflict = df.duplicated(KEY, keep=False)
    counts["conflicting_dupes_kept"] = int(conflict.sum())

    df["year"] = df.year.astype(int)
    df["value"] = pd.to_numeric(df.value, errors="coerce")
    df["regional_office"] = (df.regional_office.str.replace(r"^R\.\s*O\.\s*", "R.O. ", regex=True)
                             .replace({"R.O. Singrouli": "R.O. Singrauli", "R.O. Chhindwada": "R.O. Chhindwara"}))
    df["status"] = df.flag.map(status)
    df["site_type"] = df.site_as_printed.map(site_type)
    low = df.site_as_printed.str.lower()
    df["bhopal_city"] = low.str.contains(BHOPAL_GHATS) & ~low.str.contains(NOT_BHOPAL)

    high_do = (df.parameter == "Dissolved oxygen") & (df.value > 14)
    df["quality_flag"] = ""
    df.loc[high_do, "quality_flag"] = "DO above 14, implausible"
    bad_ph = (df.parameter == "pH") & ~df.value.between(4, 11) & df.value.notna()
    df.loc[bad_ph, "quality_flag"] = "pH outside 4-11, implausible"
    high_bod = (df.parameter == "BOD") & (df.value > 500)
    df.loc[high_bod, "quality_flag"] = "BOD above 500, implausible"
    df.loc[conflict, "quality_flag"] = (df.loc[conflict, "quality_flag"] + "; conflicting duplicate").str.lstrip("; ")

    df = df.sort_values(["year", "festival", "regional_office", "site_as_printed", "parameter", "phase"])
    df.attrs["counts"] = counts
    return df


def self_check(df):
    c = df.attrs["counts"]
    assert (df.needs_check != "yes").all() and not df.site_as_printed.isin(JUNK_SITES).any()
    dup = df.duplicated(KEY, keep=False)
    assert (df.loc[dup, "quality_flag"].str.contains("conflicting duplicate")).all()
    assert set(df.status) <= {"measured", "bdl", "missing"}
    assert df.loc[df.status == "measured", "value"].notna().all()
    assert df.loc[df.status != "measured", "value"].isna().all()
    assert c["rows_in"] - c["dropped_unreadable_site"] - c["identical_dupes_removed"] == len(df)
    assert df.bhopal_city.sum() > 0 and not df.loc[df.bhopal_city, "site_as_printed"].str.lower().str.contains(NOT_BHOPAL).any()


if __name__ == "__main__":
    out = clean(pd.read_csv(SRC, dtype=str, keep_default_na=False))
    self_check(out)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out[COLUMNS].to_csv(OUT, index=False)
    print(out.attrs["counts"], "rows_out:", len(out))
