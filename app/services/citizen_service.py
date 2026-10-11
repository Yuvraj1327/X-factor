"""
app/services/citizen_service.py
────────────────────────────────
Handles incoming WhatsApp messages from citizens.

Design rules:
  - Only returns verified, stored water-quality data.
  - Does NOT invent readings, scores, or safety statements.
  - Official advisory instructions must come from approved advisories.
  - Data age is always disclosed.
  - Missing or stale data is explained, not hidden.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.repositories.ghat_repo import GhatRepository
from app.repositories.whatsapp_repo import WhatsAppRepository
from app.services.whatsapp_client import WhatsAppClient

settings = get_settings()
logger = get_logger(__name__)

_FRESHNESS_DAYS = settings.DATA_FRESHNESS_THRESHOLD_DAYS

COMMANDS_EN = {
    "HI": "welcome",
    "HELP": "help",
    "ALERTS": "alerts",
    "GHAT": "ghats",
    "SUBSCRIBE": "subscribe",
    "STOP": "stop",
}
COMMANDS_HI = {
    "नमस्ते": "welcome",
    "मदद": "help",
    "अलर्ट": "alerts",
    "घाट": "ghats",
    "सदस्यता": "subscribe",
    "रुकें": "stop",
}

WELCOME_EN = (
    "🙏 Welcome to *Visarjan Ghat Watch* – Bhopal Impact Lab.\n\n"
    "I share verified water-quality data for Bhopal ghats, sourced from official reports.\n\n"
    "Commands:\n"
    "• HELP – What I can do\n"
    "• ALERTS – Latest approved advisories\n"
    "• GHAT – List monitored ghats\n"
    "• <Ghat Name> – Data for that ghat\n"
    "• SUBSCRIBE – Get proactive alerts\n"
    "• STOP – Unsubscribe\n\n"
    "_Note: I provide data-based indicators only. Official safety decisions are made by BMC officers._"
)

WELCOME_HI = (
    "🙏 *विसर्जन घाट वॉच* में आपका स्वागत है – भोपाल इम्पैक्ट लैब।\n\n"
    "मैं सरकारी रिपोर्टों से सत्यापित जल-गुणवत्ता डेटा साझा करता हूँ।\n\n"
    "कमांड:\n"
    "• मदद – मैं क्या कर सकता हूँ\n"
    "• अलर्ट – नवीनतम स्वीकृत सलाह\n"
    "• घाट – निगरानी वाले घाटों की सूची\n"
    "• <घाट का नाम> – उस घाट का डेटा\n"
    "• सदस्यता – सक्रिय अलर्ट प्राप्त करें\n"
    "• रुकें – अनसब्सक्राइब करें\n\n"
    "_नोट: मैं केवल डेटा-आधारित संकेतक प्रदान करता हूँ। आधिकारिक सुरक्षा निर्णय BMC अधिकारी लेते हैं।_"
)

HELP_EN = (
    "*Ghat Watch – Available Commands*\n\n"
    "ALERTS – Latest BMC-approved water-quality advisories\n"
    "GHAT – List of monitored ghats\n"
    "<Ghat Name> – Historical readings and source references for a ghat\n"
    "SUBSCRIBE – Opt in to receive proactive advisories\n"
    "STOP – Opt out of proactive alerts\n\n"
    "_Data shown is from official reports. Sampling dates are always disclosed._"
)


def _data_age_note(sampling_date: Optional[datetime], lang: str = "en") -> str:
    if not sampling_date:
        if lang == "hi":
            return "⚠️ इस घाट के लिए कोई पठन उपलब्ध नहीं है।"
        return "⚠️ No readings available for this ghat."

    now = datetime.now(timezone.utc)
    sd = sampling_date.replace(tzinfo=timezone.utc) if sampling_date.tzinfo is None else sampling_date
    age_days = (now - sd).days

    if age_days > _FRESHNESS_DAYS:
        if lang == "hi":
            return (
                f"⚠️ नवीनतम पठन *{age_days} दिन पुराना* है "
                f"({sd.strftime('%d %b %Y')})। यह वर्तमान स्थिति नहीं दर्शाता।"
            )
        return (
            f"⚠️ Latest reading is *{age_days} days old* ({sd.strftime('%d %b %Y')}). "
            "This does not reflect current conditions."
        )
    if lang == "hi":
        return f"📅 नमूना दिनांक: {sd.strftime('%d %b %Y')}"
    return f"📅 Sampling date: {sd.strftime('%d %b %Y')}"


async def handle_citizen_message(
    from_phone: str,
    body: str,
    db: AsyncSession,
) -> str:
    """
    Process an incoming WhatsApp message and return the reply text.
    Never invents readings. Always states data age and source.
    """
    ghat_repo = GhatRepository(db)
    wa_repo = WhatsAppRepository(db)

    subscriber = await wa_repo.get_or_create_subscriber(from_phone)
    lang = subscriber.language

    text = body.strip().upper() if body else ""
    text_orig = body.strip() if body else ""

    # ── Opt-out ───────────────────────────────────────────────────────────────
    if text in ("STOP", "UNSUBSCRIBE", "रुकें"):
        await wa_repo.unsubscribe(subscriber)
        return (
            "✅ You have been unsubscribed from Ghat Watch alerts. "
            "Reply SUBSCRIBE to opt back in."
            if lang == "en"
            else "✅ आपने घाट वॉच अलर्ट से सदस्यता समाप्त कर ली है। वापस जुड़ने के लिए सदस्यता टाइप करें।"
        )

    # ── Subscribe ─────────────────────────────────────────────────────────────
    if text in ("SUBSCRIBE", "सदस्यता"):
        await wa_repo.set_consent(subscriber)
        return (
            "✅ You are now subscribed! You'll receive BMC-approved advisories.\n\n"
            "Reply GHAT to see monitored ghats and add ghat preferences."
            if lang == "en"
            else "✅ आप अब सदस्य हैं! आपको BMC-अनुमोदित सलाह मिलेगी।\n\n"
            "घाट वरीयता जोड़ने के लिए घाट टाइप करें।"
        )

    # ── Welcome ───────────────────────────────────────────────────────────────
    if text in ("HI", "HELLO", "START", "नमस्ते"):
        return WELCOME_HI if lang == "hi" else WELCOME_EN

    # ── Help ──────────────────────────────────────────────────────────────────
    if text in ("HELP", "मदद"):
        return HELP_EN

    # ── Ghat list ─────────────────────────────────────────────────────────────
    if text in ("GHAT", "GHATS", "घाट"):
        ghats = await ghat_repo.list_ghats()
        if not ghats:
            return "No ghats are currently configured." if lang == "en" else "कोई घाट उपलब्ध नहीं है।"
        ghat_list = "\n".join(f"• {g.name}" for g in ghats)
        if lang == "hi":
            return f"🏊 *निगरानी घाट:*\n{ghat_list}\n\nकिसी घाट का डेटा देखने के लिए उसका नाम टाइप करें।"
        return f"🏊 *Monitored Ghats:*\n{ghat_list}\n\nType a ghat name to see its data."

    # ── Alerts ────────────────────────────────────────────────────────────────
    if text in ("ALERTS", "ALERT", "अलर्ट"):
        from app.models.advisory import AdvisoryStatus
        from app.repositories.advisory_repo import AdvisoryRepository
        advisory_repo = AdvisoryRepository(db)
        advisories = await advisory_repo.list_all(
            status=AdvisoryStatus.SENT, limit=3
        )
        if not advisories:
            return (
                "No recent advisories available." if lang == "en"
                else "अभी कोई हालिया सलाह उपलब्ध नहीं है।"
            )
        parts = []
        for a in advisories:
            body_text = a.body_hi if lang == "hi" and a.body_hi else a.body_en
            parts.append(f"📋 *{a.title_en}*\n{body_text}")
        return "\n\n---\n\n".join(parts)

    # ── Ghat name lookup ──────────────────────────────────────────────────────
    ghats = await ghat_repo.list_ghats()
    matched_ghat = None
    for g in ghats:
        if (
            text_orig.lower() == g.name.lower()
            or text_orig.lower() == (g.name_hi or "").lower()
            or text == g.slug.upper().replace("-", " ")
        ):
            matched_ghat = g
            break

    if matched_ghat:
        reading = await ghat_repo.get_latest_reading(matched_ghat.id)
        age_note = _data_age_note(reading.sampling_date if reading else None, lang)

        if not reading:
            return (
                f"🏊 *{matched_ghat.name}*\n\n{age_note}\n\n"
                "_No readings are available. BMC has not published data for this ghat._"
                if lang == "en"
                else f"🏊 *{matched_ghat.name}*\n\n{age_note}\n\n"
                "_कोई पठन उपलब्ध नहीं है। BMC ने इस घाट के लिए डेटा प्रकाशित नहीं किया है।_"
            )

        lines = [f"🏊 *{matched_ghat.name}*\n{age_note}\n"]
        if reading.dissolved_oxygen is not None:
            lines.append(f"• Dissolved O₂: {reading.dissolved_oxygen} mg/L (CPCB min: 5.0)")
        if reading.bod is not None:
            lines.append(f"• BOD: {reading.bod} mg/L (CPCB max: 3.0)")
        if reading.ph is not None:
            lines.append(f"• pH: {reading.ph} (CPCB range: 6.5–8.5)")
        if reading.fecal_coliform is not None:
            lines.append(f"• Fecal Coliform: {reading.fecal_coliform} MPN/100mL (CPCB max: 500)")

        source_note = ""
        if reading.source:
            source_note = f"\n📄 Source: {reading.source.title}"
            if reading.source.url:
                source_note += f"\n🔗 {reading.source.url}"

        lines.append(
            "\n⚠️ _These are historical readings only. They do not certify current safety._"
        )
        if source_note:
            lines.append(source_note)

        return "\n".join(lines)

    # ── Unknown ───────────────────────────────────────────────────────────────
    return (
        "I didn't understand that. Reply HELP to see available commands."
        if lang == "en"
        else "मुझे यह समझ नहीं आया। उपलब्ध कमांड देखने के लिए मदद टाइप करें।"
    )
