"""
app/models/ghat.py
───────────────────
Ghat, water-quality readings, data sources, and CPCB thresholds.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Index,
    Integer, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class GhatStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Ghat(Base):
    __tablename__ = "ghats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name_hi: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    location_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[GhatStatus] = mapped_column(
        Enum(GhatStatus), default=GhatStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    readings: Mapped[List["WaterQualityReading"]] = relationship(
        "WaterQualityReading", back_populates="ghat", cascade="all, delete-orphan"
    )
    advisories: Mapped[List["Advisory"]] = relationship(
        "Advisory", back_populates="ghat"
    )

    def __repr__(self) -> str:
        return f"<Ghat id={self.id} name={self.name!r}>"


class DataSource(Base):
    """References to official source reports."""
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    report_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    pdf_page: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    readings: Mapped[List["WaterQualityReading"]] = relationship(
        "WaterQualityReading", back_populates="source"
    )


class WaterQualityReading(Base):
    """
    A single water-quality measurement at a ghat.
    Readings are historical; they are NEVER claimed to represent current conditions
    unless the sampling_date is within the DATA_FRESHNESS_THRESHOLD_DAYS window.
    """
    __tablename__ = "water_quality_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ghat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ghats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True
    )
    sampling_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Core CPCB parameters
    dissolved_oxygen: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # mg/L
    bod: Mapped[Optional[float]] = mapped_column(Float, nullable=True)                 # mg/L
    ph: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fecal_coliform: Mapped[Optional[float]] = mapped_column(Float, nullable=True)      # MPN/100mL
    total_coliform: Mapped[Optional[float]] = mapped_column(Float, nullable=True)      # MPN/100mL
    nitrate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)             # mg/L
    turbidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)           # NTU
    conductivity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)        # µS/cm
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)         # °C

    # Metadata
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ghat: Mapped["Ghat"] = relationship("Ghat", back_populates="readings")
    source: Mapped[Optional["DataSource"]] = relationship("DataSource", back_populates="readings")

    __table_args__ = (
        Index("ix_wqr_ghat_date", "ghat_id", "sampling_date"),
    )


class CPCBThreshold(Base):
    """
    Configurable CPCB water-quality criteria.
    Class B = bathing/outdoor contact.
    Stored in DB so admins can update without redeployment.
    """
    __tablename__ = "cpcb_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parameter: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    water_class: Mapped[str] = mapped_column(String(10), default="B", nullable=False)
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
