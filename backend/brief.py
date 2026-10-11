"""Step 5: officer brief in English and Hindi from data/clean/llm_input.json.

Two writers, same facts:
- template: deterministic, no API key needed; the demo never depends on the network
- claude:   rewords the facts into a smoother brief; used only if every check passes

Checks on any brief before it is shown:
- every number must already be in llm_input.json (the LLM may not invent or compute)
- no health or "safe/clean" wording (the data shows readings against limits, nothing more)

Run from the repo root: python backend/brief.py  -> writes data/clean/brief_en.md, brief_hi.md
"""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LLM_INPUT = ROOT / "data" / "clean" / "llm_input.json"
MODEL = "claude-opus-5-5"
TOP = 3  # ghats in the brief; the full list is in the UI

BANNED = [r"\bdiseases?\b", r"\billness", r"\bpoison", r"\btoxic", r"\bcancer", r"\binfection",
          r"\bunsafe\b", r"\bhealth\b",
          # Claims that water is fine; "not treated as clean" is allowed.
          r"\b(is|are|was|were|looks?|seems?) (clean|safe|fine)\b", r"\bsafe (to|for)\b", r"\bclean water\b",
          "बीमारी", "रोग", "ज़हर", "जहर", "विषैल", "कैंसर", "संक्रमण", "सुरक्षित", "स्वास्थ्य", "साफ़ है", "साफ है", "स्वच्छ"]
NUMBER = re.compile(r"\d+(?:\.\d+)?")

SYSTEM = """You write a one-page brief for the Bhopal Municipal Corporation officer who plans Durga idol immersion.
Rules:
- Use ONLY facts and numbers from FACTS. Do not calculate, round, add or estimate any number.
- Write every number with Western digits, exactly as in FACTS, even in Hindi.
- Keep page references like (2023 p.60) next to the numbers they support.
- A ghat that was not tested is "not tested", never clean or fine.
- Do not mention health effects, disease, safety or cleanliness. Say "below the bathing limit" instead.
- Do not claim immersion caused anything; the data cannot separate immersion from sewage.
Structure: one-line purpose; the top 3 ghats (tier, 2 reasons, 2 actions each); one line on how ghats were ranked;
3 data gaps; date of visarjan. Plain short sentences. No more than 250 words."""
LANG = {"en": "Write the brief in English.",
        "hi": "Write the brief in simple Hindi (Devanagari). Keep ghat names, 'mg/l', 'BOD', 'MPPCB' and "
              "'CPCB' as they are."}


def load_facts():
    return json.loads(LLM_INPUT.read_text())


# --- checks -------------------------------------------------------------------------------------------

def unknown_numbers(text, facts):
    allowed = {float(n) for n in NUMBER.findall(json.dumps(facts, ensure_ascii=False))}
    return [n for n in NUMBER.findall(text) if float(n) not in allowed]


def banned_words(text):
    return [w for w in BANNED if re.search(w, text, flags=re.IGNORECASE)]


def check(text, facts):
    return {"unknown_numbers": unknown_numbers(text, facts), "banned_words": banned_words(text)}


def passes(checks):
    return not checks["unknown_numbers"] and not checks["banned_words"]


# --- template writer ----------------------------------------------------------------------------------
# Reasons and actions come from fixed templates in facts.py, so each maps to Hindi by pattern.

TIER_HI = {"HIGH": "उच्च जोखिम", "MEDIUM": "मध्यम जोखिम", "WATCH": "निगरानी"}
PHASE_HI = {"pre": "विसर्जन से पहले", "during": "विसर्जन के दौरान", "after": "विसर्जन के एक सप्ताह बाद"}
FEST_HI = {"Durga": "दुर्गा", "Ganesh": "गणेश"}


def events_hi(text):
    return re.sub(r"(Durga|Ganesh) (\d{4})", lambda m: f"{FEST_HI[m.group(1)]} {m.group(2)}", text)


REASON_HI = [
    (r"Dissolved oxygen below the bathing limit of ([\d.]+) mg/l in (\d+) of (\d+) readings",
     lambda m: f"घुली ऑक्सीजन (DO) {m[3]} में से {m[2]} रीडिंग में स्नान सीमा {m[1]} mg/l से कम"),
    (r"Near-zero oxygen \(below 2 mg/l\) in (\d+) readings?, lowest ([\d.]+) mg/l( \(printed as 0.*\))?",
     lambda m: f"{m[1]} रीडिंग में ऑक्सीजन लगभग शून्य (2 mg/l से कम), न्यूनतम {m[2]} mg/l"
               + (" (रिपोर्ट में 0 छपा है; MPPCB से पुष्टि करें)" if m[3] else "")),
    (r"Not tested in Durga (\d{4}).*", lambda m: f"दुर्गा {m[1]} में जाँच नहीं हुई (रिपोर्ट में इस स्थल की तालिका नहीं)"),
    (r"In Durga (\d{4}), oxygen was already ([\d.]+) mg/l before immersion.*",
     lambda m: f"दुर्गा {m[1]} में विसर्जन से पहले ही ऑक्सीजन {m[2]} mg/l थी"),
    (r"In Durga (\d{4}), oxygen was ([\d.]+) mg/l in the (pre|during|after)-immersion sample"
     r"(?:, and already ([\d.]+) mg/l before immersion)?",
     lambda m: f"दुर्गा {m[1]} में {PHASE_HI[m[3]]} ऑक्सीजन {m[2]} mg/l थी"
               + (f", और विसर्जन से पहले ही {m[4]} mg/l" if m[4] else "")),
    (r"Oxygen dropped by more than 2 mg/l during immersion in (.*)",
     lambda m: f"विसर्जन के दौरान ऑक्सीजन 2 mg/l से अधिक गिरी: {events_hi(m[1])}"),
    (r"One week after immersion, oxygen was more than 0.5 mg/l below the pre-immersion level in (\d+) of (\d+) festivals",
     lambda m: f"{m[2]} में से {m[1]} त्योहारों में एक सप्ताह बाद भी ऑक्सीजन पहले से 0.5 mg/l से अधिक कम रही"),
    (r"Temporary kund: no before or after sample in (.*?) because.*",
     lambda m: f"अस्थायी कुंड: {events_hi(m[1])} में पहले/बाद का नमूना नहीं (कुंड तब बना नहीं था या हटा दिया गया था)"),
    (r"BOD above the bathing limit of ([\d.]+) mg/l .*?in (\d+) of (\d+) readings",
     lambda m: f"BOD {m[3]} में से {m[2]} रीडिंग में स्नान सीमा {m[1]} mg/l से अधिक (रिपोर्ट में BOD जाँच विधि नहीं छपी)"),
]
ACTION_HI = [
    ("Place aerators", "20 अक्टूबर से पहले एरेटर लगाएँ और विसर्जन के बाद एक सप्ताह तक चलाएँ"),
    ("Ask MPPCB to sample", "MPPCB से नमूने लेने को कहें: पहले (18 अक्टूबर तक), दौरान, और एक सप्ताह बाद (लगभग 27 अक्टूबर)"),
    ("Collect idols", "48 घंटे में मूर्तियाँ, फूल और बचा सामान हटाएँ (CPCB दिशानिर्देश, 2025 रिपोर्ट p.23)"),
    ("Keep separate bins", "फूल और पूजा सामग्री के लिए अलग डिब्बे रखें ताकि वे पानी में न जाएँ"),
    ("Line the temporary kund", "अस्थायी कुंड में हटाने योग्य सिंथेटिक लाइनर लगाएँ (CPCB दिशानिर्देश, 2025 रिपोर्ट p.14)"),
    ("Keep immersion out of the open Upper Lake", "खुली बड़ी झील (Upper Lake) में विसर्जन न होने दें; वहाँ जल-आपूर्ति के इनटेक कुएँ हैं"),
    ("Ask MPPCB to confirm", "संदिग्ध रीडिंग और उनकी इकाइयों की MPPCB से पुष्टि कराएँ"),
]


def reason_hi(text):
    for pattern, fmt in REASON_HI:
        m = re.match(pattern, text)
        if m:
            return fmt(m)
    return text  # unknown template: keep English rather than guess


def action_hi(text):
    return next((hi for prefix, hi in ACTION_HI if text.startswith(prefix)), text)


def pages(r):
    return f" ({', '.join(r['pages'][:3])})" if r["pages"] else ""


def template_brief(facts, lang="en"):
    top = facts["ghats"][:TOP]
    date = "20 Oct 2026" if lang == "en" else "20 अक्टूबर 2026"
    if lang == "en":
        lines = [f"Durga visarjan {date}: ghats that need attention first (MPPCB readings 2023-2025).", ""]
        for g in top:
            lines.append(f"{g['rank']}. {g['site']}: {g['tier']}" + (f" ({g['tier_note']})" if g["tier_note"] else ""))
            lines += [f"   - {r['text']}{pages(r)}" for r in g["reasons"][:2]]
            lines += [f"   > {a}" for a in g["actions"][:2]]
        lines += ["", "How ranked: " + facts["how_ranked"].split(". ")[0] + ".", "", "Not in the data:"]
        lines += [f"- {x}" for x in facts["not_in_data"][:3]]
    else:
        lines = [f"दुर्गा विसर्जन {date}: किन घाटों पर पहले ध्यान दें (MPPCB रीडिंग 2023-2025)।", ""]
        for g in top:
            note = " (जाँच न होने से उच्च माना गया; जाँच न होना साफ़ होना नहीं है)" if g["tier_note"] else ""
            lines.append(f"{g['rank']}. {g['site']}: {TIER_HI[g['tier']]}{note}")
            lines += [f"   - {reason_hi(r['text'])}{pages(r)}" for r in g["reasons"][:2]]
            lines += [f"   > {action_hi(a)}" for a in g["actions"][:2]]
        lines += ["", "रैंकिंग का आधार: केवल घुली ऑक्सीजन (DO) की रीडिंग; BOD दिखाया है पर अंक नहीं दिए।", "",
                  "डेटा में नहीं:", "- घाटों पर बैक्टीरिया (कोलिफॉर्म) की जाँच नहीं",
                  "- पानी का तापमान और नमूने का समय नहीं", "- रिपोर्ट में इकाइयाँ नहीं छपीं; मानक इकाइयाँ मानी गई हैं"]
    return "\n".join(lines)


def whatsapp_brief(facts, lang="en"):
    """Short forwardable text: top 3 ghats, one reason and one action each."""
    head = "Durga visarjan 20 Oct: priority ghats" if lang == "en" else "दुर्गा विसर्जन 20 अक्टूबर: प्राथमिक घाट"
    out = [head]
    for g in facts["ghats"][:TOP]:
        # An untested ghat leads with that fact: it is why a raised ghat is HIGH.
        reason = next((r["text"] for r in g["reasons"] if r["text"].startswith("Not tested")), g["reasons"][0]["text"])
        action = g["actions"][0] if g["actions"] else ""
        tier = g["tier"] if lang == "en" else TIER_HI[g["tier"]]
        if lang == "hi":
            reason, action = reason_hi(reason), action_hi(action)
        out.append(f"{g['rank']}. {g['site']} ({tier}): {reason}. {action}")
    out.append("Source: MPPCB visarjan reports 2023-2025" if lang == "en" else "स्रोत: MPPCB विसर्जन रिपोर्ट 2023-2025")
    return "\n".join(out)


# --- claude writer ------------------------------------------------------------------------------------

def claude_brief(facts, lang, client=None, feedback=""):
    import anthropic
    client = client or anthropic.Anthropic()
    resp = client.beta.messages.create(
        model=MODEL, max_tokens=4000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",  # retry on another model if declined
        system=SYSTEM + "\n" + LANG[lang],
        messages=[{"role": "user", "content": "FACTS:\n" + json.dumps(facts, ensure_ascii=False) + feedback}],
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError("model declined")
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def make_brief(lang="en", fmt="page", facts=None, client=None, use_llm=None):
    """Returns {lang, format, source, text, checks}. Falls back to the template on any LLM failure."""
    facts = facts or load_facts()
    if fmt == "whatsapp":
        text = whatsapp_brief(facts, lang)
        return {"lang": lang, "format": fmt, "source": "template", "text": text, "checks": check(text, facts)}
    use_llm = (client is not None or bool(os.environ.get("ANTHROPIC_API_KEY"))) if use_llm is None else use_llm
    error = None
    if use_llm:
        feedback = ""
        for _ in range(2):  # one retry, telling the model what failed
            try:
                text = claude_brief(facts, lang, client, feedback)
            except Exception as e:  # network, auth, refusal: the officer still gets the template brief
                error = f"{type(e).__name__}: {e}"
                break
            checks = check(text, facts)
            if passes(checks):
                return {"lang": lang, "format": fmt, "source": "claude", "text": text, "checks": checks}
            error = f"checks failed: {checks}"
            feedback = (f"\n\nYour previous brief failed checks: {checks}. Remove those numbers or words; "
                        "use only numbers that appear in FACTS.")
    text = template_brief(facts, lang)
    out = {"lang": lang, "format": fmt, "source": "template", "text": text, "checks": check(text, facts)}
    return out | ({"llm_error": error} if error else {})


if __name__ == "__main__":
    facts = load_facts()
    for lang in ["en", "hi"]:
        b = make_brief(lang, facts=facts)
        assert passes(b["checks"]), b["checks"]
        (ROOT / "data" / "clean" / f"brief_{lang}.md").write_text(b["text"] + "\n")
        print(f"--- {lang} ({b['source']}) ---\n{b['text']}\n")
        w = make_brief(lang, "whatsapp", facts=facts)
        assert passes(w["checks"]) and len(w["text"]) <= 1000, (w["checks"], len(w["text"]))
