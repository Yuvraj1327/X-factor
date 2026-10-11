"""Initial schema — all tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-11
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ── ghats ─────────────────────────────────────────────────────────────────
    op.create_table(
        "ghats",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("name_hi", sa.String(120), nullable=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("location_description", sa.Text, nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ghats_slug", "ghats", ["slug"])

    # ── data_sources ──────────────────────────────────────────────────────────
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("publisher", sa.String(120), nullable=True),
        sa.Column("report_year", sa.Integer, nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("pdf_page", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── water_quality_readings ────────────────────────────────────────────────
    op.create_table(
        "water_quality_readings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ghat_id", sa.Integer, sa.ForeignKey("ghats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sampling_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dissolved_oxygen", sa.Float, nullable=True),
        sa.Column("bod", sa.Float, nullable=True),
        sa.Column("ph", sa.Float, nullable=True),
        sa.Column("fecal_coliform", sa.Float, nullable=True),
        sa.Column("total_coliform", sa.Float, nullable=True),
        sa.Column("nitrate", sa.Float, nullable=True),
        sa.Column("turbidity", sa.Float, nullable=True),
        sa.Column("conductivity", sa.Float, nullable=True),
        sa.Column("temperature", sa.Float, nullable=True),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_wqr_ghat_date", "water_quality_readings", ["ghat_id", "sampling_date"])

    # ── cpcb_thresholds ───────────────────────────────────────────────────────
    op.create_table(
        "cpcb_thresholds",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("parameter", sa.String(60), nullable=False, unique=True),
        sa.Column("water_class", sa.String(10), nullable=False, server_default="B"),
        sa.Column("min_value", sa.Float, nullable=True),
        sa.Column("max_value", sa.Float, nullable=True),
        sa.Column("unit", sa.String(30), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── admin_users ───────────────────────────────────────────────────────────
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="bmc_officer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"])

    # ── advisories ────────────────────────────────────────────────────────────
    op.create_table(
        "advisories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ghat_id", sa.Integer, sa.ForeignKey("ghats.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("admin_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("approved_by_id", sa.Integer, sa.ForeignKey("admin_users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("language", sa.String(10), nullable=False, server_default="both"),
        sa.Column("title_en", sa.String(255), nullable=False),
        sa.Column("title_hi", sa.String(255), nullable=True),
        sa.Column("body_en", sa.Text, nullable=False),
        sa.Column("body_hi", sa.Text, nullable=True),
        sa.Column("recommended_action_en", sa.Text, nullable=True),
        sa.Column("recommended_action_hi", sa.Text, nullable=True),
        sa.Column("reading_ids", sa.String(512), nullable=True),
        sa.Column("sampling_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_references", sa.Text, nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recipients_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("delivered_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_advisories_ghat_id", "advisories", ["ghat_id"])
    op.create_index("ix_advisories_status", "advisories", ["status"])

    # ── subscribers ───────────────────────────────────────────────────────────
    op.create_table(
        "subscribers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("phone_e164", sa.String(20), nullable=False, unique=True),
        sa.Column("language", sa.String(5), nullable=False, server_default="hi"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_subscribers_phone_e164", "subscribers", ["phone_e164"])

    # ── subscriber_ghats ──────────────────────────────────────────────────────
    op.create_table(
        "subscriber_ghats",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subscriber_id", sa.Integer, sa.ForeignKey("subscribers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ghat_id", sa.Integer, sa.ForeignKey("ghats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("subscriber_id", "ghat_id", name="uq_subscriber_ghat"),
    )

    # ── whatsapp_messages ─────────────────────────────────────────────────────
    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subscriber_id", sa.Integer, sa.ForeignKey("subscribers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("advisory_id", sa.Integer, sa.ForeignKey("advisories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recipient_phone", sa.String(20), nullable=False),
        sa.Column("template_name", sa.String(120), nullable=True),
        sa.Column("language", sa.String(5), nullable=False),
        sa.Column("body_preview", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("is_dry_run", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("meta_message_id", sa.String(120), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(20), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("attempt_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_wam_advisory_subscriber", "whatsapp_messages", ["advisory_id", "subscriber_id"])
    op.create_index("ix_whatsapp_messages_meta_message_id", "whatsapp_messages", ["meta_message_id"])

    # ── delivery_events ───────────────────────────────────────────────────────
    op.create_table(
        "delivery_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("message_id", sa.Integer, sa.ForeignKey("whatsapp_messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meta_event_id", sa.String(120), nullable=False, unique=True),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── incoming_messages ─────────────────────────────────────────────────────
    op.create_table(
        "incoming_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("meta_message_id", sa.String(120), nullable=False, unique=True),
        sa.Column("from_phone", sa.String(20), nullable=False),
        sa.Column("message_type", sa.String(30), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_incoming_messages_meta_message_id", "incoming_messages", ["meta_message_id"])


def downgrade() -> None:
    op.drop_table("incoming_messages")
    op.drop_table("delivery_events")
    op.drop_table("whatsapp_messages")
    op.drop_table("subscriber_ghats")
    op.drop_table("subscribers")
    op.drop_table("advisories")
    op.drop_table("admin_users")
    op.drop_table("cpcb_thresholds")
    op.drop_table("water_quality_readings")
    op.drop_table("data_sources")
    op.drop_table("ghats")
