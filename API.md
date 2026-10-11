# API for the UI team

Base URL: local `http://localhost:8000`, hosted: the Render URL. Interactive docs at `/docs`.
All endpoints are `GET`, public, CORS open. Data is read-only.

## `GET /ranking`

The dashboard's main data. 7 ghats, already ranked. Nothing to compute in the UI.

```jsonc
{
  "visarjan_date": "2026-10-20",
  "how_ranked": "Ranked on dissolved oxygen only: ...",       // show under the list
  "standard": {"class": "B (organised outdoor bathing)", "why": "...", "oxygen_min": 5, "bod_max": 3, "fish_oxygen_min": 4},
  "latest_durga": 2025,
  "ghats": [
    {
      "rank": 1,
      "site": "Bairagarh (Sant Hirdaram) kund",
      "tier": "HIGH",                       // HIGH | MEDIUM | WATCH  -> red | amber | grey-blue
      "tier_note": "",                      // non-empty when a tier was raised; show it next to the tier
      "points": 29, "tied_with": [],
      "tags": ["temporary kund", "near Upper Lake, which has water-supply intake wells (lake report 2023-24 p.1-4)"],
      "site_note": "",                      // e.g. "may be two sampling points"; show as a warning
      "untested_latest_durga": true,        // show a grey "NOT TESTED Durga 2025" badge
      "reasons": [
        {
          "text": "Dissolved oxygen below the bathing limit of 5 mg/l in 11 of 13 readings",
          "pages": ["2023 p.26", "2023 p.60", "2024 p.25", "2024 p.69", "2025 p.28"],
          "evidence": [                      // every number behind the reason
            {"year": 2023, "festival": "Durga", "phase": "pre", "parameter": "Dissolved oxygen",
             "value": 0.0, "status": "measured", "page": 60,
             "pdf": "/reports/2023_MPPCB_Idol_Immersion_Report.pdf#page=60",   // open as BASE_URL + pdf
             "quality_flag": "zero oxygen: verify with MPPCB"}                 // optional; show a "verify" chip
          ]
        }
      ],
      "actions": ["Place aerators before 20 Oct ...", "..."],
      "verify": [{"text": "Lead 1.77 (Ganesh 2024, after): ...", "pdf": "...#page=69", "...": "..."}],
      "derived": {"oxygen_before_median": 4.7, "oxygen_lowest": 0.0, "oxygen_drop_median": -1.1, "oxygen_recovery_median": -1.4},
      "coverage": {"rows": 234, "measured": 143, "bdl": 23, "missing": 68,
                   "missing_reasons": {"no table for this site in the report": 36, "kund not built yet at pre-immersion sampling (report remark)": 13, "...": "..."}}
    }
  ],
  "context": {
    "kund_vs_river": {"text": "Across Madhya Pradesh, oxygen was below 4 mg/l in 11.5% of kund readings vs 2.7% ...", "...": "..."},
    "lake_baseline": [{"station": "Kalighat spill outlet", "lake": "Lower Lake", "text": "Routine lake monitoring, not at the ghats: ...", "pdf": "/reports/...#page=10"}]
  },
  "not_in_data": ["No coliform (bacteria) test at the ghats, ...", "..."],   // show as a "What this data does not cover" box
  "data_warnings": ["Zinc in Ganesh 2024 runs 16x other festivals: ...", "..."],
  "sources": ["reports/2023_MPPCB_Idol_Immersion_Report.pdf", "..."]
}
```

Values above are Bairagarh's real entry, shortened with `...`.

## `GET /brief?lang=en|hi&format=page|whatsapp`

The officer's forwardable brief.

```json
{"lang": "hi", "format": "whatsapp", "source": "template", "text": "दुर्गा विसर्जन 20 अक्टूबर: ...",
 "checks": {"unknown_numbers": [], "banned_words": []}}
```

- `source`: `claude` when the API key is set and the brief passed every check, else `template` (always works).
- `checks` are empty lists on anything returned. Show a small "numbers checked against the data" note.
- `format=whatsapp` is under 1,000 characters. Share link: `https://wa.me/?text=` + `encodeURIComponent(text)`.
- `&refresh=true` regenerates; otherwise the brief is cached per data version.

## `GET /reports/<file>.pdf`

The MPPCB source reports. Evidence `pdf` links already include `#page=N`, so browsers open the right page.

## Screens this supports

1. Ranked list: rank, site, tier colour, `NOT TESTED` badge, tags, first reason.
2. Ghat detail: all reasons; each evidence value is a link to its PDF page; verify chips; actions; coverage.
3. Brief: EN/HI toggle, copy button, WhatsApp share.
4. "What this data does not cover": `not_in_data` + `data_warnings`; context lines below.
