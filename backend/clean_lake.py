"""Lake water-quality baseline for Upper and Lower Lake, Bhopal (MPPCB monthly monitoring).

Reads two MPPCB report PDFs in reports/ and writes data/clean/lake_baseline.csv, one row per
printed number:
- lake_2025-26_Upper_Lower_monthly.pdf: every monthly value + the printed annual average
- lake_2003-2023_Upper_comparative.pdf (Upper Lake only): the printed annual average per station
  per year, plus the monthly/quarterly values for DO, BOD, Total and Fecal coliform

Rules: nothing is invented. Blank, "-", NA, ND, BDL cells produce no row (so a missing month is
simply absent, never a clean value). "<1.8" / ">1600" keep the number with a "censored" flag.
Doubtful numbers keep their value and get a quality_flag. Every row carries source_file + page.

How: pdftotext -bbox gives every word with its x/y position. Rows are anchored on the printed
serial number and each value goes to the month cell (bounded by the header words) it sits in,
so a blank cell can never shift later months left.

Run from the repo root: python backend/clean_lake.py   (needs poppler's pdftotext on PATH)
"""
import html
import re
import shutil
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
OUT = ROOT / "data" / "clean" / "lake_baseline.csv"
NEW = "lake_2025-26_Upper_Lower_monthly.pdf"
OLD = "lake_2003-2023_Upper_comparative.pdf"
OLD_MONTHLY_PARAMS = {"Dissolved oxygen", "BOD", "Total coliform", "Fecal coliform"}
COLIFORMS = {"Total coliform", "Fecal coliform", "E. coli"}

COLUMNS = ["source_file", "page", "station", "station_code", "lake", "period_type", "period",
           "sample_date", "parameter", "value", "unit", "category", "quality_flag"]
KEY = ["source_file", "station", "period_type", "period", "parameter"]

# printed parameter name (lower case, start of the name) -> clean name. First match wins.
# "Fixed Dissolved Solids", "Total Solids", "Nitrite" etc. match none of these.
PARAMS = [
    (r"p\.?\s?h\b", "pH"),
    (r"(dissolved|dis\.|d\s*\.)\s*oxygen", "Dissolved oxygen"),
    (r"b\.\s*o\.\s*d", "BOD"),
    (r"(c\.\s*o\.\s*d|chemical\s+oxygen)", "COD"),
    (r"(t\.|total)\s*coliform", "Total coliform"),
    (r"(f\.|fa?ecal)\s*coliform", "Fecal coliform"),
    (r"e\.\s*coli", "E. coli"),
    (r"(sp\.\s*)?conductivity", "Conductivity"),
    (r"turbidity", "Turbidity"),
    (r"((total|t\.)\s*dissolved|dissolved\s+solids|t\.\s*d\.\s*s|d\.\s*solids)", "Total dissolved solids"),
    (r"nitrate", "Nitrate"),
    (r"phosphate", "Phosphate"),
]
STATIONS = [  # keyword in the page heading -> station name. Sehore Naka before Bairagarh:
    ("sehore", "Sehore Naka"),  # the old file prints "Near Sehore naka,Bairagarh".
    ("kamla park", "Kamla Park intake"),
    ("yatch club", "Yacht Club"),
    ("karbala", "Karbala intake"),
    ("bairagarh", "Bairagarh intake"),
    ("khanugaon", "Khanugaon"),
    ("kalighat", "Kalighat spill outlet"),
]
MONTHS = ["april", "may", "june", "july", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "march"]
NUMBER = re.compile(r"^([<>])?(\d+(?:\.\d+)?)$")
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')


def pdf_pages(pdf):
    """Every page as a list of words: dicts with x (centre), y (centre), x0, x1 and text."""
    out = subprocess.run([shutil.which("pdftotext") or "/opt/homebrew/bin/pdftotext", "-bbox", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    pages = []
    for chunk in out.split("<page ")[1:]:
        words = []
        for x0, y0, x1, y1, t in WORD.findall(chunk):
            x0, y0, x1, y1 = map(float, (x0, y0, x1, y1))
            words.append({"x": (x0 + x1) / 2, "y": (y0 + y1) / 2, "x0": x0, "x1": x1, "text": html.unescape(t)})
        pages.append(words)
    return pages


def lines(words, tol=3.0):
    """Group words into text lines by y, each line sorted left to right."""
    out = []
    for w in sorted(words, key=lambda w: w["y"]):
        if out and abs(out[-1][-1]["y"] - w["y"]) <= tol:
            out[-1].append(w)
        else:
            out.append([w])
    return [sorted(line, key=lambda w: w["x"]) for line in out]


def text_of(words):
    return " ".join(w["text"] for w in words)


def fiscal_year(words):
    """'Year - 2003-2004' / 'Year-2025-26' -> '2003-04'."""
    m = re.search(r"Year\s*-?\s*(\d{4})\s*-\s*(\d{2,4})", text_of(words))
    return f"{m.group(1)}-{m.group(2)[-2:]}" if m else None


def month_period(fy, month_index):
    """Fiscal year '2025-26' + column index (0 = April) -> '2025-09'."""
    start = int(fy[:4])
    year = start if month_index < 9 else start + 1
    return f"{year}-{(month_index + 3) % 12 + 1:02d}"


def header_columns(words):
    """Column cells from the header line, or None if the page has no header.

    Returns sorted [(month index 0-11 or 'avg', left x, right x)]. Cell borders are taken halfway
    across the gap between neighbouring header words: that is inside the true border whether a
    header is left-aligned or centred, and whether values are centred or left-aligned.
    """
    av = next((w for w in words if re.match(r"^Av\.?$", w["text"])), None)
    if not av:
        return None
    band = [w for w in words if abs(w["y"] - av["y"]) < 9]
    heads = {}
    for w in band:
        t = w["text"].lower()
        i = next((i for i, m in enumerate(MONTHS) if t.startswith(m)), None)
        if i is not None:
            heads[i] = (w["x0"], w["x1"])
    # Old-format tables print all 12 month headers; on p5 and p9 of the comparative file the
    # July header cell is blank (the column is still there), so put it between June and Aug.
    if len(heads) == 11:
        gap = (set(range(12)) - set(heads)).pop()
        if 0 < gap < 11:
            mid = (heads[gap - 1][1] + heads[gap + 1][0]) / 2
            heads[gap] = (mid, mid)
    heads["avg"] = (av["x0"], av["x1"])
    maxi = next((w for w in band if w["text"].lower().startswith("max")), None)
    order = sorted(heads.items(), key=lambda h: h[1][0])
    xs = [h[1] for h in order] + [(maxi["x0"], maxi["x1"]) if maxi else (av["x1"] + 30, None)]
    borders = [order[0][1][0] - 12] + [(a[1] + b[0]) / 2 for a, b in zip(xs, xs[1:])]
    return [(key, borders[n], borders[n + 1]) for n, (key, _) in enumerate(order)]


def column_of(cols, x):
    """Column key whose cell contains x, or None (left of April, or Maxi./Mini.)."""
    return next((key for key, left, right in cols if left <= x < right), None)


def header_dates(words, cols):
    """2025-26 style headers print the date inside the month cell, e.g. 'Sep(03-09-' / '2025)'."""
    av_y = next(w["y"] for w in words if re.match(r"^Av\.?$", w["text"]))
    near = sorted((w for w in words if av_y - 9 < w["y"] < av_y + 25), key=lambda w: (round(w["y"]), w["x"]))
    dates = {}
    for key, _, _ in cols:
        cell = "".join(w["text"] for w in near if column_of(cols, w["x"]) == key)
        m = re.search(r"\((\d{1,2})-(\d{1,2})-?(\d{4})\)", cell)
        if m and key != "avg":
            dates[key] = m.groups()
    return dates


def iso_date(parts, fy, month_index, fix_april_year=False):
    """(d, m, y) or a printed date string -> ISO date, only if it agrees with the column's month."""
    want_y, want_m = map(int, month_period(fy, month_index).split("-"))
    if isinstance(parts, str):
        nums = re.findall(r"\d+", parts)
        if len(nums) != 3:
            return ""
        a, b, y = map(int, nums)
        candidates = [(a, b, y), (b, a, y)]  # 2021-22 tables mix d/m/y and m/d/y
    else:
        d, m, y = map(int, parts)
        candidates = [(d, m, y)]
    for d, m, y in candidates:
        y = y + 2000 if y < 100 else y
        # The 2025-26 report prints the April 2025 sample as "01-04-2026"; April of FY 2025-26 is 2025.
        if fix_april_year and month_index == 0 and y == want_y + 1:
            y = want_y
        if m == want_m and y == want_y and 1 <= d <= 31:
            return f"{y}-{m:02d}-{d:02d}"
    return ""


def station_of(words):
    """Station name, station code and lake from the page heading."""
    head = text_of([w for w in words if w["y"] < min(w2["y"] for w2 in words) + 90]).lower()
    name = next((n for k, n in STATIONS if k in head), None)
    # 2025-26 prints "(Sta. code- 1373)"; some 2020-23 comparative pages print the bare code.
    code = re.search(r"sta\.\s*code-?\s*(\d+)|\b(1373|1374|2137|2138|2139)\b", head)
    lake = "Lower Lake" if "lower lake" in head else "Upper Lake" if "upper lake" in head else None
    return name, next(g for g in code.groups() if g) if code else "", lake


def category_of(words, cols):
    """MPPCB category from the 'Cat. B' / 'CAT-C' / 'Category - A' line under the table.

    Returns (table category, {column: category}). A few tables print one letter per sample
    under the month columns instead (p20, p72 of the comparative file: B B B D), so a row takes
    its own column's letter when there is one.
    """
    cat_lines = [line for line in lines(words) if re.search(r"\bCat", text_of(line), re.I)]
    if not cat_lines:
        return "", {}
    line = cat_lines[-1]  # the one under the table, not the station description
    label = text_of([w for w in line if w["x1"] < cols[0][1]])
    m = re.search(r"\bCat(?:egory)?\b\.?[\s.\-]*([A-E])\b", label, re.I)
    per_column = {column_of(cols, w["x"]): w["text"] for w in line if re.fullmatch(r"[A-E]", w["text"])}
    return (m.group(1).upper() if m else ""), {k: v for k, v in per_column.items() if k is not None}


def table_rows(words, cols):
    """Yield (serial, y, name words, unit, value words) per printed row, anchored on the serial."""
    left_edge = cols[0][1]
    unit_left = min(w["x0"] for w in words if w["text"] in ("mg/l", "mg/1")) - 2
    sno_hdr = next((w for w in words if re.match(r"^(S\.?\s?No\.?|Sr\.?)$", w["text"])), None)
    sno_x1 = sno_hdr["x1"] + 4 if sno_hdr else 66
    serials = [w for w in words if re.match(r"^\d{1,2}$", w["text"]) and w["x1"] < sno_x1
               and (not sno_hdr or w["y"] > sno_hdr["y"] + 3)]
    rows = {id(s): (s, [], [], []) for s in serials}  # serial, name, unit, values
    near = lambda w, pool: min(pool, key=lambda s: abs(s["y"] - w["y"]), default=None)
    others = [w for w in words if w not in serials] if serials else []
    for w in others:
        s = near(w, serials)
        if abs(s["y"] - w["y"]) > 10:
            continue
        if w["x"] >= left_edge:
            rows[id(s)][3].append(w)
        elif w["x0"] >= unit_left:
            rows[id(s)][2].append(w)
        elif abs(s["y"] - w["y"]) <= 3:
            rows[id(s)][1].append(w)
    # A wrapped name line belongs to a row with no name on its own line (the cell is centred on
    # the serial); only if there is none nearby does it go to the nearest row.
    bare = [s for s, name, _, _ in rows.values() if not name]
    for w in others:
        s = near(w, serials)
        if w["x0"] < unit_left and 3 < abs(s["y"] - w["y"]) <= 10:
            b = near(w, bare)
            rows[id(b if b and abs(b["y"] - w["y"]) <= 10 else s)][1].append(w)
    for s, name, unit, values in rows.values():
        unit = " ".join(w["text"] for w in sorted(unit, key=lambda w: (round(w["y"]), w["x"])))
        yield int(s["text"]), s["y"], name, unit, values


def parameter_of(name_words, row_y):
    """Clean parameter name or None. Long names wrap onto a line above and/or below the serial,
    so try the serial's own line first, then add the neighbouring lines."""
    ordered = sorted(name_words, key=lambda w: (round(w["y"]), w["x"]))
    above = " ".join(w["text"] for w in ordered if w["y"] < row_y - 3)
    own = " ".join(w["text"] for w in ordered if abs(w["y"] - row_y) <= 3)
    below = " ".join(w["text"] for w in ordered if w["y"] > row_y + 3)
    for candidate in (own, f"{above} {own}", f"{own} {below}"):
        low = candidate.strip().lower()
        clean = next((c for pattern, c in PARAMS if low and re.match(pattern, low)), None)
        if clean:
            return clean
    return None


def split_glued(w):
    """'1instrument' / 'order1.8' (a note overflowing into the next cell) -> two pieces, each
    placed at its share of the word's width. 'covid-19' and the like stay whole."""
    m = re.match(r"^(\d+(?:\.\d+)?)([A-Za-z]{3,}.*)$", w["text"]) or re.match(r"^(.*[A-Za-z]{3})(\d+(?:\.\d+)?)$", w["text"])
    if not m:
        return [w]
    per_char = (w["x1"] - w["x0"]) / len(w["text"])
    return [{**w, "text": m.group(g), "x": w["x0"] + per_char * (m.start(g) + m.end(g)) / 2} for g in (1, 2)]


def place_values(value_words, cols, where):
    """Column -> (number match or None, printed text) for one row. Two numbers in one cell fail loudly."""
    cells = {}
    for w in (p for w in value_words for p in split_glued(w)):
        key = column_of(cols, w["x"])
        if key is not None:
            cells.setdefault(key, []).append(w["text"])
    out = {}
    for key, texts in cells.items():
        numbers = [m for m in map(NUMBER.match, texts) if m]
        assert len(numbers) <= 1, f"two numbers in one cell: {where} column {key}: {texts}"
        out[key] = (numbers[0] if numbers else None, " ".join(texts))
    return out


def value_flags(parameter, value, sign):
    flags = []
    if sign == "<":
        flags.append("censored: <")
    if sign == ">":
        flags.append("censored: > (test upper limit)")
    if (parameter == "Dissolved oxygen" and value > 14) or (parameter == "BOD" and value > 50) \
            or (parameter == "pH" and not 4 <= value <= 11):
        flags.append("implausible, likely typo: verify")
    return flags


def average_flags(parameter, avg_match, cells):
    """Compare the printed average with the printed months. MPPCB's spreadsheet averages only
    plain numbers, so BDL/ND and "<x"/">x" months are silently left out of the printed average."""
    months = [c for k, c in cells.items() if k != "avg"]
    left_out = sum(1 for m, t in months if (m and m.group(1)) or t.upper() in ("BDL", "ND", "NIL"))
    plain = [float(m.group(2)) for m, _ in months if m and not m.group(1)]
    flags = []
    if left_out:
        flags.append(f"printed average leaves out {left_out} BDL/ND/censored month(s)")
    if any(value_flags(parameter, v, None) for v in plain):
        flags.append("printed average includes a likely-typo month: verify")
    if plain:
        avg, mean = float(avg_match.group(2)), sum(plain) / len(plain)
        decimals = len(avg_match.group(2).partition(".")[2])
        if abs(avg - mean) > max(0.02 * mean, 10 ** -decimals):  # allow for printed rounding
            flags.append(f"printed average differs from mean of printed months ({mean:.2f}): verify")
    return flags


def parse_page(source, page_no, words, cols, fy, station, code, lake, dates):
    """All kept rows of one printed table page."""
    category, column_category = category_of(words, cols)
    dates = dict(dates)
    parsed = []
    for serial, y, name, unit, values in table_rows(words, cols):
        cells = place_values(values, cols, f"{source} p{page_no} row {serial}")
        param = parameter_of(name, y)
        if text_of(name).lower().startswith("date"):
            dates.update({k: iso_date(t, fy, k) for k, (_, t) in cells.items() if k != "avg"})
        if param:
            parsed.append((param, unit, cells))
    rows = []
    for param, unit, cells in parsed:
        for k, (m, _) in cells.items():
            if not m:
                continue  # blank, "-", NA, ND, BDL, #DIV/0!, notes: no row
            monthly = k != "avg"
            if source == OLD and monthly and param not in OLD_MONTHLY_PARAMS:
                continue
            value = float(m.group(2))
            flags = value_flags(param, value, m.group(1)) + ([] if monthly else average_flags(param, m, cells))
            # 2025-26 prints the same test's ceiling as ">1600" in one cell and "1600" in the next.
            if source == NEW and param in COLIFORMS and value == 1600 and not m.group(1):
                flags.append("at the 1600 MPN test ceiling, true count may be higher")
            rows.append({
                "source_file": source, "page": page_no, "station": station, "station_code": code,
                "lake": lake, "period_type": "month" if monthly else "annual_avg",
                "period": month_period(fy, k) if monthly else fy,
                "sample_date": dates.get(k, "") if monthly else "",
                "parameter": param, "value": value, "unit": unit,
                "category": column_category.get(k, category),
                "quality_flag": "; ".join(flags),
            })
    return rows


def parse_pdf(source):
    rows, header, meta = [], None, None
    for page_no, words in enumerate(pdf_pages(REPORTS / source), 1):
        if not words:
            continue
        cols = header_columns(words)
        if cols:
            fy = fiscal_year(words)
            dates = {i: iso_date(d, fy, i, fix_april_year=source == NEW) for i, d in header_dates(words, cols).items()}
            header, meta = cols, (fy, *station_of(words), dates)
        # else: 2025-26 tables run onto a second page with no title or header; the template is
        # identical, so that page reuses the previous page's columns, station and year.
        rows += parse_page(source, page_no, words, header, *meta)
    return rows


def flag_copy_errors(df):
    """Turbidity printed with the same number as that month's conductivity (Kalighat Aug 2025:
    472.9 in both rows, on different pages) is a copy error, and it drags the printed average."""
    month = df[df.period_type == "month"]
    cond = month[month.parameter == "Conductivity"].set_index(["source_file", "station", "period"])["value"]
    for i, r in month[month.parameter == "Turbidity"].iterrows():
        if cond.get((r.source_file, r.station, r.period)) != r.value:
            continue
        add_flag(df, df.index == i, "same number as conductivity that month, likely copy error: verify")
        add_flag(df, (df.source_file == r.source_file) & (df.station == r.station) & (df.parameter == "Turbidity")
                 & (df.period_type == "annual_avg") & (df.page == r.page),
                 "printed average includes a likely-typo month: verify")
    return df


def add_flag(df, mask, note):
    df.loc[mask, "quality_flag"] = [f"{old}; {note}" if old else note for old in df.loc[mask, "quality_flag"]]


def self_check(df):
    assert not df.duplicated(KEY).any(), df[df.duplicated(KEY, keep=False)].sort_values(KEY).head(20)
    assert df["page"].notna().all() and df["value"].notna().all()
    assert set(df["lake"]) <= {"Upper Lake", "Lower Lake"}, set(df["lake"])
    assert set(df.loc[df.lake == "Lower Lake", "station"]) == {"Kalighat spill outlet"}
    assert (df.loc[df.source_file == OLD, "lake"] == "Upper Lake").all()
    assert df["station"].notna().all()
    assert set(df["period_type"]) == {"month", "annual_avg"}
    # Sep 2025 at Kamla Park, checked by hand against p1 of the 2025-26 report.
    kp = df[(df.station == "Kamla Park intake") & (df.period == "2025-09")].set_index("parameter")["value"]
    assert kp["Dissolved oxygen"] == 7.2 and kp["BOD"] == 1.2 and kp["Fecal coliform"] == 21


def main():
    df = flag_copy_errors(pd.DataFrame(parse_pdf(NEW) + parse_pdf(OLD), columns=COLUMNS))
    df = df.sort_values(["source_file", "station", "parameter", "period_type", "period"], ignore_index=True)
    self_check(df)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"wrote {len(df)} rows to {OUT.relative_to(ROOT)}")
    print(df.groupby(["source_file", "station"]).size().to_string())


if __name__ == "__main__":
    main()
