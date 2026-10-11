# Visarjan Ghat Watch

**Team:** X-factor · **Members:** Muiz Khan, Aradhya Jain, Gargi Dixit, Harsh Shrivastava, Yuvraj Gupta · **Track:** 2, Visarjan Ghat Watch (Bhopal Impact Lab, 11 Oct 2026)

**User:** the Bhopal Municipal Corporation officer who plans Durga visarjan at the ghats (20 October 2026) and
decides where to send aerators, cleaning crews and water testing.

**Problem:** MPPCB tests the water at every immersion ghat before, during and one week after each festival, then files
90-120 page PDFs nobody lines up against the limits. Bairagarh kund hit 0 mg/l dissolved oxygen four times; it sat on
page 60 of an 87-page report.

**What it gives the officer:** the 7 Bhopal ghats ranked by risk, each reason in plain words with every number linked to
its report page, actions per ghat, and a one-page brief in English and Hindi to forward on WhatsApp.

**Live app:** https://visarjan-ghat-watch-dusky.vercel.app · **Live API:** https://api-production-9a4c9.up.railway.app (docs: `/docs`)

## Run it (5 steps)

```bash
git clone https://github.com/Yuvraj1327/X-factor.git && cd X-factor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # optional: only needed to regenerate briefs (python backend/brief.py)
uvicorn backend.main:app            # open http://localhost:8000/docs
```

Rebuild the data after adding readings: `python backend/clean.py && python backend/clean_statewide.py &&
python backend/clean_lake.py && python backend/facts.py`. Tests: `python -m pytest tests/`.

**Deploy (Railway):** `railway init`, `railway add --service api`, set `ANTHROPIC_API_KEY` with
`railway variable set ANTHROPIC_API_KEY --stdin --service api`, then `railway up --service api` and `railway domain`.
Start command and health check are in `railway.json`.

## How it works

```
reports/*.pdf  ->  data/readings/*.csv  ->  backend/clean.py  ->  data/clean/bhopal_readings_clean.csv
                   data/statewide/      ->  clean_statewide.py ->  data/clean/statewide_clean.csv
reports/lake_*.pdf                      ->  clean_lake.py      ->  data/clean/lake_baseline.csv
                                            backend/facts.py   ->  ranking.json (UI)  +  llm_input.json (LLM)
                                            backend/verify_llm.py -> Claude re-reads every report page (second reader)
                                            backend/brief.py   ->  English / Hindi brief, checked
                                            backend/main.py    ->  GET /ranking, GET /brief, /reports/*.pdf
```

- **All maths is code (pandas), never the LLM.** The LLM only rewords `llm_input.json`. Any brief with a number not in
  that file, or with health / "safe" wording, is rejected and the deterministic template is served instead.
- **Missing is never clean.** Every gap is a row with a reason (no table in the report, temporary kund not built yet or
  dismantled, parameter not tested). A ghat with near-zero oxygen on record that was not tested in the latest Durga is
  raised to HIGH, and says so.
- **Standard:** CPCB Class B (organised outdoor bathing: dissolved oxygen at least 5 mg/l, BOD at most 3 mg/l), because
  people enter the water at ghats. Class D (fish, oxygen at least 4) as a second line.
- **Ranking:** dissolved oxygen only: readings below 5, 4 and 2 mg/l, drops of more than 2 mg/l during immersion, no
  recovery a week later. BOD is shown but not scored (above the limit almost everywhere); metals are not scored (units not
  printed, labs disagree ~1000x).

## What the data shows

- **Temporary kunds are the worst and the least tested.** Bairagarh and Malikhedi are built for the festival and taken
  down after (2025 report p.62, p.92), so they never get a before or after sample; neither had a Durga 2025 table.
- **Kunds fail far more often than rivers.** Across MP, oxygen was below 4 mg/l in 11.5% of kund readings vs 2.7% of river
  readings; in kunds, 3.5% of pre-immersion samples vs 16.8% one week after. With the NGT ban moving immersion into kunds,
  that is where aerators, liners and 48-hour cleanup matter most.
- **The Lower Lake is poor before any idol arrives:** BOD (3-day test) above 3 mg/l in all 11 months sampled in 2025-26
  (lake report p.9). Immersion is not the only cause, and the data cannot separate the two.

## What works and what doesn't

Works:
- Cleaned data verified against the PDFs: 2023 (546/546 rows), 2024 (546/546), 2025 (all rows); lake baseline ~970 values.
- Every printed cell read twice: Claude read all 19 report pages independently (`backend/verify_llm.py`) and code
  compared its reading with the parser's: 1,476 of 1,476 cells agree (`data/clean/llm_verification.csv`).
- `/ranking`, `/brief` (English, Hindi, WhatsApp), PDF page links, 35 tests. Briefs are generated once with Claude,
  read by a person, and served frozen (`data/clean/briefs.json`): no model call at request time.

Doesn't / not covered:
- No coliform test at the ghats, no temperature, no sampling time, no idol counts; units are assumed (not printed).
- One sample per phase per festival; newest data is 2025.
- Metal readings are unverified (Ganesh 2024 runs 7-16x other festivals; Durga 2025 after-values copy pre-values).
- Two sites may each be two sampling points (Rani Kamlapati / Kamla Park; Hathaikheda kund / dam).
- This branch is the backend (data pipeline + API). The web UI lives on branch `Aradhya-frontend`, live at
  https://visarjan-ghat-watch-dusky.vercel.app; it only calls the API described in `API.md`.

## Data

All from the event pack (public): MPPCB Ganesh and Durga visarjan reports
[2023](https://www.mppcb.mp.gov.in/proc/mon/Idol_immer._Report_23_CPCB.pdf),
[2024](https://www.mppcb.mp.gov.in/proc/mon/Ganesh_and_Durga_visarjan_report-2024.pdf),
[2025](https://www.mppcb.mp.gov.in/proc/mon/Ganesh_and_Durga_visarjan_report-2025.pdf);
lake reports [2025-26](https://xgn.mp.nic.in/File_Upload/MONITORING//Yearly%20Water%20Quality%20Status/2026/July/UPPER%20LAKE-2025-26..pdf),
[2023-24](https://www.mppcb.mp.gov.in/proc/mon/Bhopal-2023-24_upper_lake.pdf),
[2003-2023](https://www.mppcb.mp.gov.in/proc/mon/comparatives-uppe-lak-lower-lake-2003-2023.pdf);
[CPCB water quality criteria](https://cpcb.gov.in/water-quality-criteria/). No personal data. No extra data added.

**Next year:** add `data/readings/bhopal_2026.csv` (same columns) and `reports/2026_<name>.pdf`, rerun the four scripts,
then `python backend/brief.py`. Still hard-coded for 2026: the visarjan and sampling dates in `facts.py` / `brief.py`,
and the tier cut-offs (tuned on 2023-2025 data).

**Caveat on the statewide comparison:** site type is read from site names, and the pre-immersion and one-week-after
samples are not the same set of sites (temporary kunds have no pre sample).

License: MIT.
