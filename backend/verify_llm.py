"""Second reader: Claude reads each MPPCB report page and checks our extracted values.

The parser and the LLM read the page independently; code compares the two. Nothing is changed
automatically: disagreements go to data/clean/llm_verification.csv for a person to check on the page.
Run after clean.py, with ANTHROPIC_API_KEY set: python backend/verify_llm.py   (about 20 pages, under $1)
"""
import base64
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
OUT = CLEAN / "llm_verification.csv"
MODEL = "claude-opus-5-5"

PROMPT = """This is one page of a Madhya Pradesh Pollution Control Board idol-immersion water-quality report.
Its tables have columns for pre-immersion, during-immersion and after-one-week samples.
For each row in ROWS, find the table for that site, the line for that parameter, and the column for that phase,
and copy exactly what is printed in that cell (a number, BDL, ND, _, -, * or blank).
Read the page yourself; ROWS deliberately does not tell you our value. If you cannot find the cell, say unreadable.
ROWS:
"""
SCHEMA = {
    "type": "object",
    "properties": {"rows": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "printed": {"type": "string"},
                       "found": {"type": "boolean"}, "note": {"type": "string"}},
        "required": ["id", "printed", "found", "note"], "additionalProperties": False}}},
    "required": ["rows"], "additionalProperties": False,
}


def page_pdf(report, page):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "page.pdf"
        subprocess.run(["pdfseparate", "-f", str(page), "-l", str(page), str(ROOT / report), str(out)], check=True)
        return base64.standard_b64encode(out.read_bytes()).decode()


def same(ours, printed):
    """Compare as numbers when both are numbers, else as text (BDL, _, ...)."""
    a, b = (str(x).replace(" ", "").upper() for x in (ours, printed))  # "* *" is how a PDF spaces "**"
    try:
        return float(a) == float(b)
    except ValueError:
        return a == b


def check_page(client, report, page, rows):
    ask = [{"id": int(i), "site": r.site_as_printed, "parameter": r.parameter, "phase": r.phase}
           for i, r in rows.iterrows()]
    resp = client.messages.create(
        model=MODEL, max_tokens=16000,
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf",
                                            "data": page_pdf(report, page)}},
            {"type": "text", "text": PROMPT + json.dumps(ask, ensure_ascii=False)}]}],
    )
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"{report} p.{page}: stop_reason {resp.stop_reason}")
    read = {r["id"]: r for r in json.loads(next(b.text for b in resp.content if b.type == "text"))["rows"]}
    out = rows.copy()
    out["llm_printed"] = [read.get(i, {}).get("printed", "") for i in rows.index]
    out["llm_note"] = [read.get(i, {}).get("note", "") for i in rows.index]
    found = [read.get(i, {}).get("found", False) for i in rows.index]
    out["verdict"] = ["unreadable" if not f else "match" if same(v, p) else "mismatch"
                      for f, v, p in zip(found, out.value_as_printed, out.llm_printed)]
    return out


def main():
    df = pd.read_csv(CLEAN / "bhopal_readings_clean.csv")
    # Every cell that is printed in a report: measured, BDL, and blanks printed as _ or -.
    rows = df[df.source_page.notna() & df.value_as_printed.notna()]
    client = anthropic.Anthropic()
    groups = list(rows.groupby(["report_file", "source_page"]))
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda kv: check_page(client, kv[0][0], int(kv[0][1]), kv[1]), groups))
    out = pd.concat(results)[["year", "festival", "site", "phase", "parameter", "value_as_printed",
                              "llm_printed", "verdict", "llm_note", "report_file", "source_page"]]
    out.to_csv(OUT, index=False)
    print(f"{len(groups)} pages, {len(out)} cells -> {OUT.relative_to(ROOT)}")
    print(out.verdict.value_counts().to_string())
    bad = out[out.verdict != "match"]
    if len(bad):
        print(bad[["year", "festival", "site", "phase", "parameter", "value_as_printed", "llm_printed",
                   "source_page", "llm_note"]].to_string())


if __name__ == "__main__":
    main()
