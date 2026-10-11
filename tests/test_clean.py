"""Run from the repo root: python -m pytest tests/"""
import pandas as pd
import pytest

from backend.clean import KEY, clean, load_raw, report_file, self_check

RAW = load_raw()
DF = clean(RAW)
BAIRAGARH, MALIKHEDI = "Bairagarh (Sant Hirdaram) kund", "Malikhedi kund"


def rows(year, festival, site, **where):
    r = DF[(DF.year == year) & (DF.festival == festival) & (DF.site == site)]
    for col, val in where.items():
        r = r[r[col] == val]
    return r


def test_structure():
    self_check(DF, RAW)


def test_totals_match_problem_statement():
    # Pinned to the organisers' 2023-2025 file so new years don't break it.
    old = DF[DF.year.between(2023, 2025) & DF.status.eq("measured")]
    do, bod = old[old.parameter == "Dissolved oxygen"].value, old[old.parameter == "BOD"].value
    assert (len(do), (do < 5).sum()) == (116, 42)
    assert (len(bod), (bod > 3).sum()) == (112, 100)


def test_raw_values_unchanged():
    merged = RAW.merge(DF, on=KEY, suffixes=("_raw", ""))
    assert len(merged) == len(RAW)
    for col in ["value", "value_as_printed", "source_page"]:
        a, b = merged[col + "_raw"], merged[col]
        assert ((a == b) | (a.isna() & b.isna())).all(), col


def test_missing_durga_2025_tables_are_visible_rows():
    n_params = RAW.parameter.nunique()
    for site in [BAIRAGARH, MALIKHEDI]:
        r = rows(2025, "Durga", site)
        assert len(r) == 3 * n_params and set(r.status) == {"missing"}


def test_star_remark_covers_phase_but_not_during():
    assert set(DF[DF.temporary_kund].site) == {BAIRAGARH, MALIKHEDI}
    assert rows(2025, "Ganesh", MALIKHEDI, phase="pre").missing_reason.str.startswith("kund not built").all()
    assert rows(2025, "Ganesh", MALIKHEDI, phase="during").status.eq("measured").any()


def test_bdl_rows_are_bdl_not_missing():
    raw_bdl = RAW[RAW.flag.eq("BDL")].merge(DF, on=KEY)
    assert len(raw_bdl) == (RAW.flag == "BDL").sum() and raw_bdl.status.eq("bdl").all()


def test_water_body_printed_is_per_table():
    assert rows(2023, "Durga", BAIRAGARH).water_body_printed.eq(True).all()
    assert rows(2025, "Ganesh", BAIRAGARH, status="measured").water_body_printed.eq(False).all()
    assert rows(2023, "Durga", "Prempura ghat").water_body_printed.eq(False).all()


def test_doubtful_values_flagged_not_dropped():
    spike = rows(2024, "Ganesh", BAIRAGARH, phase="after", parameter="Lead")
    assert spike.value.item() == 1.77 and "verify" in spike.quality_flag.item()
    floor = DF[(DF.year == 2025) & (DF.festival == "Ganesh") & (DF.parameter == "Lead") & (DF.value == 0.031)]
    assert floor.quality_flag.str.contains("detection limit").all()
    copy = rows(2025, "Durga", "Hathaikheda dam / kund", parameter="Copper", phase="after")
    assert "identical to pre" in copy.quality_flag.item()
    zinc = rows(2024, "Ganesh", "Khatlapura ghat", parameter="Zinc", status="measured")
    assert zinc.quality_flag.str.contains("unit or method change").all()


def test_report_file_per_festival(tmp_path):
    (tmp_path / "reports").mkdir()
    for name in ["2026_Ganesh_report.pdf", "2026_Durga_report.pdf", "2027_both.pdf"]:
        (tmp_path / "reports" / name).touch()
    assert report_file(2026, "Durga", tmp_path / "reports") == "reports/2026_Durga_report.pdf"
    assert report_file(2027, "Ganesh", tmp_path / "reports") == "reports/2027_both.pdf"
    (tmp_path / "reports" / "2026_extra.pdf").touch()
    (tmp_path / "reports" / "2026_Durga_annex.pdf").touch()
    with pytest.raises(ValueError):
        report_file(2026, "Durga", tmp_path / "reports")


def test_next_year_file(tmp_path):
    new = RAW[(RAW.year == 2025) & (RAW.site == "Khatlapura ghat")].assign(year=2026)
    new = pd.concat([new, new.head(1).assign(site="Bhadbhada ghat")])
    RAW.to_csv(tmp_path / "a.csv", index=False)
    new.to_csv(tmp_path / "b.csv", index=False)
    with pytest.warns(UserWarning, match="Bhadbhada"):
        both = load_raw(tmp_path)
    out = clean(both)
    # A new site gets gap rows only from its first year, not invented 2023-2025 history.
    assert set(out[out.site == "Bhadbhada ghat"].year) == {2026}
    RAW.head(3).to_csv(tmp_path / "c.csv", index=False)
    with pytest.raises(ValueError, match="duplicate"):
        load_raw(tmp_path)
