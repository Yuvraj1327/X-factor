// Visarjan Ghat Watch UI: renders the live API (/ranking, /brief). No numbers live in this file.
const API = window.API_BASE || "https://api-production-9a4c9.up.railway.app";
const VISARJAN = new Date("2026-10-20T00:00:00+05:30");
const PHASES = ["pre", "during", "after"];
const PHASE_HI = { pre: "पहले / Before", during: "दौरान / During", after: "एक सप्ताह बाद / After" };
const FEST_HI = { Ganesh: "गणेश", Durga: "दुर्गा" };
const TIER_HI = { HIGH: "उच्च / HIGH", MEDIUM: "मध्यम / MEDIUM", WATCH: "निगरानी / WATCH" };

let ranking = null;
const briefCache = {};
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const pdf = (path) => (path ? API + path : "#");

function toast(msg) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 1800); }

// ---- data helpers -------------------------------------------------------------------------------
function band(cell) {
  if (!cell || cell.status !== "measured") return "X";
  const v = cell.value;
  return v < 2 ? "D" : v < 4 ? "R" : v < 5 ? "A" : "W";
}
const needsVerify = (cell) => !!(cell && cell.quality_flag && /verify/.test(cell.quality_flag));

function shortName(site) {
  // "Bairagarh (Sant Hirdaram) kund" -> "Bairagarh", "Rani Kamlapati ghat / Kamla Park kund" -> "Rani Kamlapati"
  const out = [];
  for (const w of site.split(" ")) { if (/^(kund|ghat|lake|dam|\(|\/)/i.test(w) || w.startsWith("(")) break; out.push(w); }
  return out.join(" ") || site;
}

function tagHi(t) {
  if (t.startsWith("temporary kund")) return "अस्थायी कुंड / temporary kund";
  if (t.startsWith("near Upper Lake")) return "Upper Lake के पास: जल-आपूर्ति इनटेक कुएँ (lake report 2023-24 p.1-4)" + (t.includes("inferred") ? " · Upper Lake अनुमानित" : "");
  if (t.startsWith("Lower Lake")) return "Lower Lake: 2025-26 में हर महीने BOD 3 mg/l से ऊपर, त्योहार हो या न हो (lake report p.9)";
  return t;
}

function subline(g) {
  const parts = [];
  if (g.tags.some((t) => t.startsWith("temporary kund"))) parts.push("अस्थायी कुंड");
  if (g.water_body === "Upper Lake") parts.push(g.tags.some((t) => t.includes("inferred")) ? "Upper Lake (अनुमानित)" : "Upper Lake के पास, जल-आपूर्ति इनटेक कुएँ");
  else if (g.water_body === "not printed") parts.push("जल-स्रोत छपा नहीं");
  else parts.push(g.water_body);
  if (g.site_note && g.site_note.includes("two sampling points")) parts.push("⚠ दो नमूना-स्थल हो सकते हैं");
  return parts.join(" · ");
}

const MISSING_HI = [
  [/not built yet/, "कुंड नहीं बना था"], [/dismantled/, "कुंड हटा दिया गया"], [/no table/, "रिपोर्ट में तालिका नहीं"],
  [/blank/, "रिपोर्ट में खाली"], [/parameter not/, "पैरामीटर नहीं"],
];
const missingHi = (reason) => (MISSING_HI.find(([re]) => re.test(reason || "")) || [0, "जाँच नहीं"])[1];

function reportFor(year) { return (ranking.sources || []).find((s) => s.includes(`/${year}_`) || s.startsWith(`reports/${year}_`)); }
function pageChip(label) {
  // label like "2023 p.26"
  const m = /^(\d{4}) p\.(\d+)$/.exec(label);
  if (!m) return `<span class="pg">${esc(label)}</span>`;
  const file = reportFor(m[1]);
  return `<a class="pg" target="_blank" rel="noopener" href="${pdf(file ? "/" + file + "#page=" + m[2] : "")}">${esc(label)}</a>`;
}

// Action types -> timeline slot and short Hindi label. Keys match the fixed action templates in backend/facts.py.
const ACTIONS = [
  { key: "Ask MPPCB to sample", when: 0, hi: "MPPCB से नमूने का अनुरोध: पहले, दौरान, लगभग 27 अक्टूबर", letter: true },
  { key: "Ask MPPCB to confirm", when: 0, hi: "उसी पत्र में संदिग्ध रीडिंग की पुष्टि" },
  { key: "Line the temporary kund", when: 0, hi: "कुंड बनाते समय हटाने योग्य लाइनर (CPCB, 2025 रिपोर्ट p.14)" },
  { key: "Place aerators", when: 1, hi: "एरेटर लगाएँ / Place aerators" },
  { key: "Keep immersion out of the open Upper Lake", when: 2, hi: "खुली Upper Lake में विसर्जन नहीं (जल-आपूर्ति इनटेक कुएँ, NGT)" },
  { key: "Keep separate bins", when: 2, hi: "फूल व पूजा सामग्री के अलग डिब्बे" },
  { key: "Collect idols", when: 3, hi: "48 घंटे में प्रतिमाएँ, फूल, बचा सामान हटाएँ (CPCB, 2025 रिपोर्ट p.23)" },
];
const WHEN = ["18 अक्टूबर तक / By 18 Oct", "20 अक्टूबर से पहले / Before 20 Oct", "20 अक्टूबर से / From 20 Oct", "विसर्जन के बाद / After"];

function chips(ghats) {
  if (ghats.length === ranking.ghats.length) return `<span class="chip">सभी ${ghats.length} घाट</span>`;
  return ghats.map((g) => `<span class="chip">${esc(shortName(g.site))}</span>`).join("");
}

// ---- pages --------------------------------------------------------------------------------------
function home() {
  const R = ranking, high = R.ghats.filter((g) => g.tier === "HIGH");
  const allUntestedCrash = high.length && high.every((g) => g.untested_latest_durga && g.score_parts.oxygen_below_2_ever);
  const names = high.map((g) => g.site);
  const bannerHi = allUntestedCrash
    ? `पहले इन ${high.length === 2 ? "दो" : high.length} कुंडों पर ध्यान दें: ${names.join(" और ")}: ${high.length === 2 ? "दोनों" : "सभी"} में लगभग शून्य DO दर्ज, दुर्गा ${R.latest_durga} में जाँच नहीं।`
    : `पहले इन घाटों पर ध्यान दें: ${names.join(", ")}`;
  const bannerEn = allUntestedCrash
    ? `Act first at ${high.map((g) => shortName(g.site)).join(" and ")}: near-zero oxygen on record, not tested in Durga ${R.latest_durga}.`
    : `Act first at: ${names.join(", ")}.`;

  const events = R.ghats[0].oxygen_grid.map((e) => `${e.festival} ${String(e.year).slice(2)}`);
  const rows = R.ghats.map((g) => {
    const measured = g.oxygen_grid.flatMap((e) => PHASES.map((p) => e.phases[p])).filter((c) => c && c.status === "measured").length;
    const heat = g.oxygen_grid.map((e) => `<span class="grp">${PHASES.map((p) => {
      const c = e.phases[p], b = band(c);
      const tip = `${FEST_HI[e.festival]} ${e.year} · ${PHASE_HI[p]}: ${c && c.status === "measured" ? c.value + " mg/l" : missingHi(c && c.missing_reason)}${c && c.page ? " · p." + c.page : ""}`;
      const href = c && c.pdf ? pdf(c.pdf) : null;
      const inner = `<span class="cell ${b}${needsVerify(c) ? " v" : ""}" title="${esc(tip)}" aria-label="${esc(tip)}"></span>`;
      return href ? `<a href="${href}" target="_blank" rel="noopener">${inner}</a>` : inner;
    }).join("")}</span>`).join("");
    return `<tr>
      <td>${g.rank}</td>
      <td><a class="name" href="#/ghat/${g.rank}">${esc(g.site)}</a><div class="sl">${esc(subline(g))}</div></td>
      <td><span class="pill ${g.tier}">${TIER_HI[g.tier]}</span>${g.tier_note ? `<div><span class="raised" title="${esc(g.tier_note)}">↑ स्तर बढ़ाया / raised</span></div>` : ""}
          ${g.untested_latest_durga ? `<div><span class="nt striped">▨ दुर्गा ${R.latest_durga} जाँच नहीं</span></div>` : ""}</td>
      <td><div class="heat">${heat}<span class="count">${g.score_parts.oxygen_below_5}/${measured} &lt; 5</span></div></td>
      <td class="nowrap"><a href="#/ghat/${g.rank}">देखें ›</a></td></tr>`;
  }).join("");

  const tl = [[], [], [], []];
  for (const a of ACTIONS) {
    const gs = R.ghats.filter((g) => g.actions.some((x) => x.startsWith(a.key)));
    if (gs.length) tl[a.when].push(`<div class="task">${esc(a.hi)}</div>${chips(gs)}${a.letter ? ` <a href="#/ghat/${gs[0].rank}">पत्र का मसौदा / Draft letter</a>` : ""}`);
    if (a.letter && gs.length) tl[3].push(`<div class="task">लगभग 27 अक्टूबर: MPPCB का बाद वाला नमूना</div>${chips(gs)}`);
  }
  const timeline = tl.map((items, i) => items.length ? `<div class="when">${WHEN[i]}</div>${items.join("")}` : "").join("");
  const v = R.verification;

  return `
  <section class="card banner">
    <div><strong>${esc(bannerHi)}</strong><span>${esc(bannerEn)}</span></div>
    <div class="btns"><button class="btn solid" data-wa="hi"><span class="dot"></span>WhatsApp पर ब्रीफ भेजें / Send brief</button>
      <button class="btn" onclick="window.print()">प्रिंट A4 / Print</button></div>
  </section>
  <div class="grid2">
    <section class="card">
      <h2>घाट प्राथमिकता सूची / Ghat priority list</h2>
      <div class="muted">घुलित ऑक्सीजन (DO), MPPCB विसर्जन रिपोर्ट 2023–2025 · Class B स्नान मानक: DO ≥ ${R.standard.oxygen_min} mg/l</div>
      <table class="ptable" style="margin-top:12px">
        <thead><tr><th>क्र.</th><th>घाट / Ghat</th><th>स्तर / Tier</th>
          <th>घुलित ऑक्सीजन, हर जाँच / DO, every test<div class="heat-head"><span>${esc(events[0])} · पुराना → नया</span><span>${esc(events[events.length - 1])} · 5 से कम / below 5</span></div></th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div class="legend"><span><i class="cell D"></i>2 से कम</span><span><i class="cell R"></i>2–4</span><span><i class="cell A"></i>4–5</span><span><i class="cell W"></i>5+</span>
        <span><i class="cell X"></i>जाँच नहीं = रिपोर्ट में रीडिंग नहीं, साफ़ नहीं माना गया</span><span><i class="cell W v"></i>MPPCB से पुष्टि करें</span>
        <span>हर खाना रिपोर्ट के पेज से जुड़ा है · हर समूह: पहले · दौरान · बाद</span></div>
    </section>
    <aside class="card"><h2>आगे क्या करें / What to do next</h2><div class="tl">${timeline}</div></aside>
  </div>
  <div class="halves">
    <section class="card"><h2>रैंकिंग कैसे बनी / How the ranking works</h2>
      <p class="muted">केवल घुलित ऑक्सीजन पर: 5, 4 और 2 mg/l से कम रीडिंग, विसर्जन में 2 mg/l से ज़्यादा गिरावट, एक सप्ताह बाद सुधार न होना। रैंक सभी रीडिंग पर, एक न्यूनतम पर नहीं। BOD दिखाया, अंक नहीं।</p>
      <a href="#/limits">Read more</a></section>
    <section class="card"><h2>यह डेटा क्या नहीं बताता / What this data does not cover</h2>
      <p class="muted">घाटों पर कोलीफॉर्म (बैक्टीरिया) जाँच नहीं · रिपोर्टों में इकाइयाँ छपी नहीं · हर चरण में एक ही नमूना; एक रीडिंग रुझान नहीं · कम DO विसर्जन से है या सीवेज से, डेटा अलग नहीं कर सकता</p>
      <a href="#/limits">सभी ${R.not_in_data.length} देखें →</a></section>
  </div>
  <section class="card" style="margin-top:24px;padding:12px 22px;font-size:13px">
    ✓ हर संख्या दो बार पढ़ी गई: ${v ? `${v.cells.toLocaleString("en-IN")} में से ${(v.match || 0).toLocaleString("en-IN")} मेल खाती हैं / Every number read twice: ${(v.match || 0).toLocaleString("en-IN")} of ${v.cells.toLocaleString("en-IN")} agree` : ""}
    · स्रोत: ${R.sources.map((s) => `<a target="_blank" rel="noopener" href="${pdf("/" + s)}">MPPCB report ${s.match(/\d{4}/)[0]} (PDF)</a>`).join(" · ")}
  </section>`;
}

function detail(rank) {
  const R = ranking, g = R.ghats.find((x) => x.rank === rank);
  if (!g) return `<p>Ghat not found. <a href="#/">Back</a></p>`;
  const prev = R.ghats.find((x) => x.rank === rank - 1), next = R.ghats.find((x) => x.rank === rank + 1);
  const cells = g.oxygen_grid.flatMap((e) => PHASES.map((p) => e.phases[p])).filter((c) => c && c.status === "measured");
  const low = cells.reduce((a, c) => (a && a.value <= c.value ? a : c), null);
  const lowVerify = cells.some((c) => c.value === low?.value && needsVerify(c));
  const grid = g.oxygen_grid.map((e) => {
    const page = PHASES.map((p) => e.phases[p]).find((c) => c && c.page);
    return `<tr><td class="lab">${e.festival} ${e.year} ${page ? pageChip(`${e.year} p.${page.page}`) : "—"}</td>${PHASES.map((p) => {
      const c = e.phases[p], b = band(c);
      if (b === "X") return `<td><span class="val X striped">${esc(missingHi(c && c.missing_reason))}</span></td>`;
      return `<td><a class="val ${b}" target="_blank" rel="noopener" href="${pdf(c.pdf)}" title="Open report page ${c.page}">${c.value}${needsVerify(c) ? '<span class="vdot" title="MPPCB से पुष्टि करें"></span>' : ""}</a></td>`;
    }).join("")}</tr>`;
  }).join("");
  const sp = g.score_parts, P = R.scoring.points;
  const why = `${g.points} अंक = ${sp.oxygen_below_2_ever * P.oxygen_below_2_ever} (कभी 2 से कम) + ${sp.oxygen_below_4 * P.oxygen_below_4} (4 से कम, ${sp.oxygen_below_4} × ${P.oxygen_below_4}) + ${sp.oxygen_below_5 * P.oxygen_below_5} (5 से कम, ${sp.oxygen_below_5} × ${P.oxygen_below_5}) + ${sp.oxygen_drop * P.oxygen_drop} (गिरावट) + ${sp.not_recovered * P.not_recovered} (सुधार नहीं, ${sp.not_recovered} × ${P.not_recovered}) · उच्च = ${R.scoring.tiers.HIGH} या अधिक`;
  const reasons = g.reasons.map((r) => `<li>${esc(r.text_hi)} ${(r.pages || []).map(pageChip).join("")}${r.text.startsWith("BOD") ? ' <span class="chip">दिखाया, अंक नहीं / shown, not scored</span>' : ""}<small>${esc(r.text)}</small></li>`).join("");
  const groups = [[], [], [], []];
  g.actions.forEach((a, i) => {
    const t = ACTIONS.find((x) => a.startsWith(x.key));
    groups[t ? t.when : 1].push(`<div class="task">${esc(g.actions_hi[i])}</div>`);
  });
  const actions = groups.map((it, i) => it.length ? `<div class="when">${WHEN[i]}</div>${it.join("")}` : "").join("");
  const verify = g.verify.map((v) => `<li><span>${esc(v.parameter === "Dissolved oxygen" ? "DO" : v.parameter)} ${v.value}, ${FEST_HI[v.festival]} ${v.year} ${PHASE_HI[v.phase].split(" /")[0]}</span><a class="pg" target="_blank" rel="noopener" href="${pdf(v.pdf)}">${v.year} p.${v.page}</a></li>`).join("");
  const cov = g.coverage, tot = cov.rows;
  const covReasons = Object.entries(cov.missing_reasons).map(([k, n]) => `${missingHi(k)} ${n}`).join(" · ");
  const below5 = g.reasons[0] && /in (\d+) of (\d+) readings/.exec(g.reasons[0].text);

  return `
  <div class="crumb"><span><a href="#/">प्राथमिकता सूची</a> › ${esc(g.site)}</span>
    <span>${prev ? `<a href="#/ghat/${prev.rank}">‹ पिछला</a>` : "‹ पिछला"} | ${next ? `<a href="#/ghat/${next.rank}">अगला: ${esc(shortName(next.site))} ›</a>` : "अगला ›"}</span></div>
  <section class="card">
    <div class="title-row"><div>
      <div class="muted">#${g.rank} / ${R.ghats.length}</div>
      <h1>${esc(g.site)} <span class="pill ${g.tier}">${TIER_HI[g.tier]}</span></h1>
      <div>${g.tags.map((t) => `<span class="chip" title="${esc(t)}">${esc(tagHi(t))}</span>`).join("")}
        ${g.untested_latest_durga ? `<span class="nt striped">दुर्गा ${R.latest_durga}: जाँच नहीं · ${esc(missingHi((g.reasons.find((r) => r.text.startsWith("Not tested")) || {}).text))}</span>` : ""}</div>
      ${g.tier_note ? `<p class="muted">↑ ${esc(g.tier_note)}</p>` : ""}
      ${g.site_note ? `<p class="muted">⚠ ${esc(g.site_note)}</p>` : ""}
    </div><div class="btns"><button class="btn solid" data-wa="hi"><span class="dot"></span>WhatsApp पर ब्रीफ भेजें</button><button class="btn" onclick="window.print()">प्रिंट A4</button></div></div>
    <div class="facts">
      <div><span class="muted">न्यूनतम DO / Lowest DO:</span><b>${low ? low.value + " mg/l" : "—"}</b>${lowVerify ? '<span class="vchip">पुष्टि करें</span> ' : ""}${low && low.page ? `<a class="pg" target="_blank" rel="noopener" href="${pdf(low.pdf)}">${low.pdf.match(/\d{4}/)[0]} p.${low.page}</a>` : ""}</div>
      <div><span class="muted">5 mg/l से कम / Below 5:</span><b>${below5 ? `${below5[2]} में से ${below5[1]}` : "—"}</b></div>
      <div><span class="muted">विसर्जन-पूर्व मध्यमान / Median before immersion:</span><b>${g.derived.oxygen_before_median ?? "—"} mg/l</b></div>
    </div>
  </section>
  <div class="grid2" style="margin-top:24px">
    <section class="card">
      <h2>घुलित ऑक्सीजन, हर जाँच / Dissolved oxygen, every test (mg/l)</h2>
      <table class="dogrid" style="margin-top:12px"><thead><tr><th>त्योहार / Festival</th>${PHASES.map((p) => `<th>${PHASE_HI[p]}</th>`).join("")}</tr></thead><tbody>${grid}</tbody></table>
      <p class="muted">Class B स्नान सीमा ${R.standard.oxygen_min} mg/l · CPCB Class D (मत्स्य) ${R.standard.fish_oxygen_min} mg/l · धारीदार = जाँच नहीं, साफ़ नहीं माना गया · <span class="vdot"></span> = MPPCB से पुष्टि करें · हर संख्या रिपोर्ट के पेज पर खुलती है</p>
      <div class="why"><b>रैंक ${g.rank} क्यों / Why rank ${g.rank}:</b><br>${esc(why)}</div>
      <h3>कारण / Reasons</h3><ul class="reasons">${reasons}</ul>
    </section>
    <div>
      <aside class="card"><h2>इस घाट के काम / Actions</h2><div class="tl">${actions}</div></aside>
      ${g.verify.length ? `<aside class="card verify-card" style="margin-top:24px"><h2>MPPCB से पुष्टि करें / Confirm with MPPCB</h2><ul class="plain">${verify}</ul>
        <button class="btn" style="margin-top:12px;width:100%;justify-content:center" data-letter="${g.rank}">पत्र का मसौदा कॉपी करें / Copy draft letter</button>
        <p class="muted" style="text-align:center">मसौदे में नाम नहीं; प्राप्तकर्ता खाली</p></aside>` : ""}
      <aside class="card" style="margin-top:24px"><h2>डेटा कवरेज / Coverage</h2>
        <div class="muted">मापा ${cov.measured} · BDL ${cov.bdl} · जाँच नहीं ${cov.missing} (कुल ${tot})</div>
        <div class="cov"><span class="m" style="width:${100 * cov.measured / tot}%"></span><span class="b" style="width:${100 * cov.bdl / tot}%"></span><span class="x" style="width:${100 * cov.missing / tot}%"></span></div>
        <div class="muted">${esc(covReasons)}</div></aside>
    </div>
  </div>`;
}

function letter(g) {
  const lines = g.verify.map((v) => `- ${v.parameter} ${v.value}, ${v.festival} ${v.year}, ${v.phase}-immersion sample (report page ${v.page})`).join("\n");
  const sample = g.actions.find((a) => a.startsWith("Ask MPPCB to sample"));
  return `विषय: ${g.site} — दुर्गा विसर्जन 2026 हेतु जल-नमूना एवं रीडिंग पुष्टि का अनुरोध\n\nप्रति,\n[प्राप्तकर्ता]\nमध्य प्रदेश प्रदूषण नियंत्रण बोर्ड\n\n` +
    (sample ? `1. Request: ${sample}.\n` : "") +
    `2. Please confirm the following readings and their units from the visarjan reports:\n${lines}\n\nभोपाल नगर निगम\n[नाम / पद]`;
}

async function getBrief(lang, format) {
  const k = lang + format;
  if (!briefCache[k]) briefCache[k] = fetch(`${API}/brief?lang=${lang}&format=${format}`).then((r) => r.json());
  return briefCache[k];
}

function md(text) {
  return esc(text).split("\n").map((l) => {
    l = l.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
    if (/^#+ /.test(l)) return `<h2>${l.replace(/^#+ /, "")}</h2>`;
    if (/^\s*[-–] /.test(l)) return `<div style="padding-left:14px">• ${l.replace(/^\s*[-–] /, "")}</div>`;
    return l.trim() ? `<div>${l}</div>` : "<br>";
  }).join("");
}

async function brief(lang = "hi") {
  const [b, w] = await Promise.all([getBrief(lang, "page"), getBrief(lang, "whatsapp")]);
  return `
  <div class="crumb"><span><a href="#/">प्राथमिकता सूची</a> › ब्रीफ / Brief</span></div>
  <div class="title-row"><h1 style="font-size:24px;margin:0 0 12px">दुर्गा विसर्जन ब्रीफ / Durga Visarjan Brief</h1>
    <div class="tabs"><button class="${lang === "hi" ? "on" : ""}" data-lang="hi">हिंदी</button><button class="${lang === "en" ? "on" : ""}" data-lang="en">English</button></div></div>
  <div class="btns" style="margin-bottom:14px"><button class="btn" onclick="window.print()">प्रिंट करें / Print</button>
    <button class="btn" data-copy>कॉपी करें / Copy text</button><button class="btn solid" data-wa="${lang}"><span class="dot"></span>WhatsApp पर भेजें / Share on WhatsApp</button></div>
  <div class="grid2">
    <article class="brief-box" id="brief-text">${md(b.text)}</article>
    <aside class="card"><h2>WhatsApp संदेश / WhatsApp message</h2><pre style="white-space:pre-wrap;font-family:inherit;font-size:13px">${esc(w.text)}</pre>
      <p class="muted">${w.text.length} अक्षर · हर संख्या डेटा से जाँची गई / every number checked against the data</p></aside>
  </div>`;
}

function limits() {
  const R = ranking, v = R.verification, k = R.context.kund_vs_river;
  return `
  <div class="crumb"><span><a href="#/">प्राथमिकता सूची</a> › डेटा की सीमाएँ / Data limits</span></div>
  <h1 style="font-size:24px;margin:0 0 16px">डेटा की सीमाएँ / What this data does not cover</h1>
  <div class="grid2">
    <div>
      <section class="card"><h2>रैंकिंग का आधार / How ghats are ranked</h2><p>${esc(R.how_ranked)}</p>
        <p class="muted">Standard: CPCB Class ${esc(R.standard.class)}: DO ≥ ${R.standard.oxygen_min} mg/l, BOD ≤ ${R.standard.bod_max} mg/l. ${esc(R.standard.why)}</p></section>
      <section class="card" style="margin-top:24px"><h2>डेटा में नहीं / Not in the data</h2><ul>${R.not_in_data.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></section>
      <section class="card warn" style="margin-top:24px"><h2>डेटा चेतावनी / Data warnings</h2><ul>${R.data_warnings.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></section>
    </div>
    <div>
      ${v ? `<section class="card"><h2>डेटा जाँच / Data check</h2><table class="dogrid"><tr><td class="lab">Report pages read twice</td><td>${v.pages}</td></tr><tr><td class="lab">Figures compared</td><td>${v.cells.toLocaleString("en-IN")}</td></tr><tr><td class="lab">Figures that agree</td><td>${(v.match || 0).toLocaleString("en-IN")}</td></tr></table><p class="muted">${esc(v.method)}</p></section>` : ""}
      ${k ? `<section class="card" style="margin-top:24px"><h2>कुंड बनाम नदी / Kunds vs rivers</h2><p class="muted">${esc(k.text)}</p></section>` : ""}
      <section class="card" style="margin-top:24px"><h2>झील की नियमित जाँच / Routine lake monitoring</h2><ul class="plain">${R.context.lake_baseline.map((l) => `<li class="muted" style="margin:6px 0">${esc(l.text.replace("Routine lake monitoring, not at the ghats: ", ""))} <a class="pg" target="_blank" rel="noopener" href="${pdf(l.pdf)}">PDF</a></li>`).join("")}</ul></section>
      <section class="card" style="margin-top:24px"><h2>स्रोत / Sources</h2><ul class="plain">${R.sources.map((s) => `<li><a target="_blank" rel="noopener" href="${pdf("/" + s)}">${esc(s.replace("reports/", ""))}</a></li>`).join("")}<li><a href="https://cpcb.gov.in/water-quality-criteria/" target="_blank" rel="noopener">CPCB Water Quality Criteria</a></li></ul></section>
    </div>
  </div>`;
}

// ---- router & events ----------------------------------------------------------------------------
let briefLang = "hi";
async function render() {
  const h = location.hash || "#/";
  const route = h.startsWith("#/ghat/") ? "home" : h.startsWith("#/brief") ? "brief" : h.startsWith("#/limits") ? "limits" : "home";
  document.querySelectorAll(".nav a").forEach((a) => a.classList.toggle("on", a.dataset.route === route));
  const main = $("#main");
  try {
    if (!ranking) ranking = await fetch(`${API}/ranking`).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
    if (h.startsWith("#/ghat/")) main.innerHTML = detail(Number(h.split("/")[2]));
    else if (route === "brief") main.innerHTML = await brief(briefLang);
    else if (route === "limits") main.innerHTML = limits();
    else main.innerHTML = home();
  } catch (e) {
    main.innerHTML = `<div class="card warn">डेटा लोड नहीं हुआ / Could not load data from the API (${esc(e.message)}). <button class="btn" onclick="location.reload()">Retry</button></div>`;
  }
  window.scrollTo(0, 0);
}

document.addEventListener("click", async (ev) => {
  const t = ev.target.closest("button");
  if (!t) return;
  if (t.dataset.wa) {
    const w = await getBrief(t.dataset.wa, "whatsapp");
    window.open("https://wa.me/?text=" + encodeURIComponent(w.text), "_blank", "noopener");
  } else if (t.dataset.lang) { briefLang = t.dataset.lang; render(); }
  else if (t.hasAttribute("data-copy")) { await navigator.clipboard.writeText($("#brief-text").innerText); toast("कॉपी हो गया / Copied"); }
  else if (t.dataset.letter) {
    const g = ranking.ghats.find((x) => x.rank === Number(t.dataset.letter));
    await navigator.clipboard.writeText(letter(g)); toast("पत्र का मसौदा कॉपी हुआ / Draft letter copied");
  } else if (t.dataset.size !== undefined) {
    document.documentElement.style.setProperty("--fs", { "-1": "13px", "0": "15px", "1": "17px" }[t.dataset.size]);
  } else if (t.id === "contrast") document.body.classList.toggle("contrast");
});

const days = Math.ceil((VISARJAN - new Date()) / 86400000);
$("#countdown").textContent = days > 0 ? `दुर्गा विसर्जन 20 अक्टूबर 2026 · ${days} दिन शेष / ${days} days` : "दुर्गा विसर्जन 20 अक्टूबर 2026";
window.addEventListener("hashchange", render);
render();
