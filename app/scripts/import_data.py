"""
app/scripts/import_data.py
────────────────────────────
Import official dataset CSVs into the database.

Usage:
    python -m app.scripts.import_data

Looks for files in the data/ directory:
  - data/bhopal_ghats_2023_2025.csv
  - data/cpcb_water_quality_criteria.csv
  - data/sample_bhopal_2025.csv

IMPORTANT:
  - Only imports data from the files listed above.
  - Does NOT fabricate any readings.
  - Clearly labels sample data vs. official data.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

from app.analysis.data_import import (
    DATA_DIR,
    check_available_datasets,
    load_cpcb_thresholds_from_csv,
    load_readings_from_csv,
)
from app.core.logging import configure_logging, get_logger
from app.database.session import AsyncSessionLocal
from app.models.ghat import DataSource, WaterQualityReading
from app.repositories.ghat_repo import GhatRepository

configure_logging()
logger = get_logger(__name__)


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


async def import_data() -> None:
    available = check_available_datasets()
    logger.info("Dataset availability", **{k: "✓ found" if v else "✗ missing" for k, v in available.items()})

    if not any(available.values()):
        logger.error(
            "No dataset files found in data/ directory. "
            "Please place the official CSVs there before running import."
        )
        sys.exit(1)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            repo = GhatRepository(session)

            # ── CPCB thresholds ───────────────────────────────────────────────
            cpcb_file = DATA_DIR / "cpcb_water_quality_criteria.csv"
            thresholds = load_cpcb_thresholds_from_csv(cpcb_file)
            for t in thresholds:
                await repo.upsert_threshold(
                    parameter=t["parameter"],
                    water_class=t.get("water_class", "B"),
                    min_value=t.get("min_value"),
                    max_value=t.get("max_value"),
                    unit=t.get("unit", ""),
                    description=t.get("description"),
                )
            logger.info("CPCB thresholds imported", count=len(thresholds))

            # ── Readings from official dataset ────────────────────────────────
            for fname in ("bhopal_ghats_2023_2025.csv", "sample_bhopal_2025.csv"):
                fpath = DATA_DIR / fname
                is_official = fname == "bhopal_ghats_2023_2025.csv"
                records = load_readings_from_csv(fpath)
                if not records:
                    continue

                # Create data source record
                source = DataSource(
                    title=f"Dataset: {fname}",
                    publisher="CPCB / State PCB (official)" if is_official else "Sample data (not official)",
                    notes=(
                        "Official CPCB/PCB monitoring data" if is_official
                        else "SAMPLE DATA — not official government readings"
                    ),
                )
                session.add(source)
                await session.flush()

                imported = 0
                for rec in records:
                    ghat_name = rec.get("name") or rec.get("ghat_name") or "Unknown Ghat"
                    slug = _slugify(ghat_name)
                    ghat = await repo.upsert_ghat(
                        name=ghat_name,
                        slug=slug,
                        name_hi=rec.get("name_hi"),
                        location_description=rec.get("location_description"),
                        latitude=rec.get("latitude"),
                        longitude=rec.get("longitude"),
                    )
                    if not rec.get("sampling_date"):
                        continue
                    session.add(WaterQualityReading(
                        ghat_id=ghat.id,
                        source_id=source.id,
                        sampling_date=rec["sampling_date"],
                        dissolved_oxygen=rec.get("dissolved_oxygen"),
                        bod=rec.get("bod"),
                        ph=rec.get("ph"),
                        fecal_coliform=rec.get("fecal_coliform"),
                        total_coliform=rec.get("total_coliform"),
                        nitrate=rec.get("nitrate"),
                        turbidity=rec.get("turbidity"),
                        conductivity=rec.get("conductivity"),
                        temperature=rec.get("temperature"),
                        is_verified=is_official,
                        notes="Sample data — not official" if not is_official else None,
                    ))
                    imported += 1
                await session.flush()
                logger.info(f"Imported {imported} readings from {fname}")


if __name__ == "__main__":
    asyncio.run(import_data())
