# Data Directory

This directory contains official water-quality datasets for Bhopal ghats.

## Expected Files

Place the following **official** CSV files here before running `import_data`:

| File | Description | Status |
|------|-------------|--------|
| `bhopal_ghats_2023_2025.csv` | Official CPCB/State PCB monitoring data | **Required for official analysis** |
| `cpcb_water_quality_criteria.csv` | CPCB Class B water-quality criteria | **Required for threshold configuration** |
| `sample_bhopal_2025.csv` | Sample/reference dataset | Optional — labelled as sample data |

## CSV Column Format

For `bhopal_ghats_2023_2025.csv` and `sample_bhopal_2025.csv`:

```
ghat_name, date, do_mgl, bod_mgl, ph, fecal_coliform, total_coliform, nitrate_mgl, turbidity_ntu, conductivity, temperature_c
Bhoj Talaab Ghat, 2024-06-15, 6.2, 2.1, 7.4, 210, 1500, 8.5, 4.2, 320, 28.5
```

For `cpcb_water_quality_criteria.csv`:

```
parameter, water_class, min_value, max_value, unit, description
dissolved_oxygen, B, 5.0, , mg/L, Min 5 mg/L for Class B bathing water
bod, B, , 3.0, mg/L, Max 3 mg/L for Class B
ph, B, 6.5, 8.5, , pH range for Class B
```

## Important Notes

- **Sample data is NOT official.** It is clearly labelled in the database and API responses.
- Missing columns are imported as NULL — never substituted with assumed values.
- See `app/analysis/data_import.py` for full column mapping documentation.
- Run `python -m app.scripts.import_data` after placing files here.
