import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../context/AppContext.jsx';
import { getPdfUrl, GHAT_COORDINATES } from '../api/client.js';

export default function Overview() {
  const { rankingData, loading, error, refreshRanking, openProof, lang } = useApp();
  const [tierFilter, setTierFilter] = useState('ALL'); // 'ALL' | 'HIGH' | 'MEDIUM' | 'WATCH'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGhatRank, setSelectedGhatRank] = useState(1);

  const ghats = rankingData?.ghats || [];
  const selectedGhat = ghats.find((g) => g.rank === selectedGhatRank) || ghats[0] || null;

  const filteredGhats = ghats.filter((g) => {
    if (tierFilter !== 'ALL' && g.tier !== tierFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchSite = g.site.toLowerCase().includes(q);
      const matchTag = g.tags?.some((t) => t.toLowerCase().includes(q));
      const matchNote = g.site_note?.toLowerCase().includes(q);
      if (!matchSite && !matchTag && !matchNote) return false;
    }
    return true;
  });

  // Tier color styling
  const getTierBadge = (tier) => {
    if (tier === 'HIGH') {
      return {
        bg: 'bg-[#ba1a1a]',
        text: 'text-white',
        border: 'border-[#991b1b]',
        label: 'HIGH / उच्च प्राथमिकता'
      };
    }
    if (tier === 'MEDIUM') {
      return {
        bg: 'bg-[#d97706]',
        text: 'text-white',
        border: 'border-[#b45309]',
        label: 'MEDIUM / मध्यम प्राथमिकता'
      };
    }
    return {
      bg: 'bg-[#64748b]',
      text: 'text-white',
      border: 'border-[#475569]',
      label: 'WATCH / निगरानी स्तर'
    };
  };

  return (
    <div className="flex flex-col gap-6 text-left pb-12">
      {/* 1. TOP STATUTORY BAN ADVISORY BANNER */}
      <div className="w-full bg-[#fdf2f2] border border-[#fecaca] rounded-lg p-3 sm:p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-2xs">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded bg-[#fee2e2] flex items-center justify-center text-[#ba1a1a] shrink-0 mt-0.5">
            <span className="material-symbols-outlined text-[20px]">warning</span>
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold text-sm sm:text-base text-[#0f2942]">
                बड़े तालाब एवं छोटे तालाब में विसर्जन पूर्णतः प्रतिबंधित (NGT OA No. 37/2020)
              </span>
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#ba1a1a] text-white">
                वैज्ञानिक निषेध / STATUTORY BAN
              </span>
            </div>
            <p className="text-xs text-[#475569] mt-0.5">
              Direct idol immersion in Bhojtal (Upper Lake Ramsar Site #1206) and Lower Lake strictly prohibited. BMC artificial immersion ponds (विसर्जन कुंड) with zero-spill bunds are mandatory.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
          <span className="px-2.5 py-1 rounded bg-[#f1f5f9] text-[#475569] font-mono text-xs font-semibold border border-[#e2e8f0]">
            BMC-ENV/CIRC-2026-9
          </span>
          <a
            href="https://api-production-9a4c9.up.railway.app/reports/2025_MPPCB_Ganesh_Durga_Visarjan_Report.pdf#page=1"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-[#f8fafc] text-[#0f2942] border border-[#cbd5e1] rounded text-xs font-bold transition-colors shadow-xs"
          >
            <span className="material-symbols-outlined text-[16px]">visibility</span>
            <span>राजपत्रित आदेश / Gazetted Order (PDF)</span>
          </a>
        </div>
      </div>

      {/* 2. STATUTORY KPI SUMMARY BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Monitored Sites */}
        <div className="bg-white rounded-xl p-4 border border-[#e2e8f0] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#64748b] font-medium mb-1">
            <span>निगरानी विसर्जन स्थल</span>
            <span className="font-mono text-[11px]">SURVEILLANCE GHATS</span>
          </div>
          <div className="text-2xl font-bold font-mono text-[#0f2942]">
            7 <span className="text-sm font-sans font-normal text-[#64748b]">घाट / कुंड</span>
          </div>
          <div className="text-[11px] text-[#475569] mt-1 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#ba1a1a]"></span>
            <span>2 उच्च (HIGH) · 3 मध्यम (MEDIUM) · 2 निगरानी (WATCH)</span>
          </div>
        </div>

        {/* KPI 2: Verification Badge */}
        <div className="bg-white rounded-xl p-4 border border-[#e2e8f0] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#64748b] font-medium mb-1">
            <span>स्वतंत्र डेटा सत्यापन</span>
            <span className="font-mono text-[11px]">AUDIT INTEGRITY</span>
          </div>
          <div className="text-2xl font-bold font-mono text-[#0284c7]">
            {rankingData?.verification?.match?.toLocaleString() || '1,476'} / {rankingData?.verification?.cells?.toLocaleString() || '1,476'}
          </div>
          <div className="text-[11px] text-[#475569] mt-1">
            100% सांख्यिकीय दोहराव मिलान (19 पृष्ठ)
          </div>
        </div>

        {/* KPI 3: CPCB Baseline */}
        <div className="bg-white rounded-xl p-4 border border-[#e2e8f0] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#64748b] font-medium mb-1">
            <span>CPCB वर्ग 'ख' मानक</span>
            <span className="font-mono text-[11px]">CPCB CLASS B</span>
          </div>
          <div className="text-2xl font-bold font-mono text-[#ba1a1a]">
            ≥ 5.0 <span className="text-sm font-sans font-normal text-[#64748b]">mg/l O₂</span>
          </div>
          <div className="text-[11px] text-[#475569] mt-1">
            संगठित बाहरी स्नान सीमा (BOD ≤ 3.0 mg/l)
          </div>
        </div>

        {/* KPI 4: Statewide Kund vs River Insight */}
        <div className="bg-white rounded-xl p-4 border border-[#e2e8f0] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#64748b] font-medium mb-1">
            <span>राज्यव्यापी कुंड जोखिम</span>
            <span className="font-mono text-[11px]">STATEWIDE RISK</span>
          </div>
          <div className="text-2xl font-bold font-mono text-[#d97706]">
            11.5% <span className="text-xs font-sans font-normal text-[#64748b]">vs 2.7% नदी</span>
          </div>
          <div className="text-[11px] text-[#475569] mt-1">
            विसर्जन उपरांत 16.8% कुंडों में O₂ &lt; 4 mg/l
          </div>
        </div>
      </div>

      {/* 3. CONTROLS BAR: TIER FILTER & SEARCH */}
      <div className="w-full flex flex-wrap items-center justify-between gap-3 bg-white p-3.5 rounded-lg border border-[#e2e8f0] shadow-2xs">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="font-bold text-[#0f2942] mr-1">जोखिम फ़िल्टर / Tier:</span>
          {['ALL', 'HIGH', 'MEDIUM', 'WATCH'].map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTierFilter(t)}
              className={`px-3 py-1.5 rounded text-xs font-bold transition-colors cursor-pointer ${
                tierFilter === t
                  ? 'bg-[#0f2942] text-white'
                  : 'bg-[#f1f5f9] text-[#334155] hover:bg-[#e2e8f0]'
              }`}
            >
              {t === 'ALL' ? 'सभी 7 घाट (All)' : t}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-[18px]">
              search
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="घाट या टैग खोजें..."
              className="pl-8 pr-3 py-1.5 text-xs bg-[#f8fafc] border border-[#cbd5e1] rounded text-[#0f2942] placeholder:text-slate-400 focus:outline-none focus:border-[#0f2942] w-48 sm:w-64"
            />
          </div>

          <button
            type="button"
            onClick={refreshRanking}
            title="Refresh from Live API"
            className="p-1.5 bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] rounded border border-[#cbd5e1] cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">sync</span>
          </button>
        </div>
      </div>

      {/* 4. MAIN GRID: SCREEN 1 RANKED LIST (Left) + DETAILED INSPECTOR (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: SCREEN 1 RANKED LIST (8 cols) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="bg-white rounded-xl border border-[#cbd5e1] shadow-sm overflow-hidden">
            {/* Table Header */}
            <div className="bg-[#0f2942] text-white px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[#ff8843] text-[20px]">format_list_numbered</span>
                <span className="font-bold text-sm">
                  {lang === 'hi' ? 'प्राथमिकता विहित सूची (7 घाट)' : 'Ranked Immersion Ghat Register (7 Sites)'}
                </span>
              </div>
              <span className="text-[11px] font-mono text-[#94a3b8]">
                API-LIVE · दुर्गा विसर्जन 2026
              </span>
            </div>

            {/* Ghats List */}
            <div className="divide-y divide-[#e2e8f0]">
              {filteredGhats.map((ghat) => {
                const tierBadge = getTierBadge(ghat.tier);
                const isSelected = selectedGhat?.rank === ghat.rank;
                const coords = GHAT_COORDINATES[ghat.site];

                return (
                  <div
                    key={ghat.rank}
                    onClick={() => setSelectedGhatRank(ghat.rank)}
                    className={`p-4 transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#f0f9ff] border-l-4 border-l-[#0284c7]'
                        : 'hover:bg-[#f8fafc]'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                      {/* Left: Rank, Name, Tier, Tags */}
                      <div className="flex items-start gap-3 flex-1">
                        {/* Rank Badge */}
                        <div
                          className={`w-9 h-9 rounded-full flex items-center justify-center font-mono font-bold text-sm shrink-0 border-2 ${
                            ghat.tier === 'HIGH'
                              ? 'bg-[#fee2e2] text-[#ba1a1a] border-[#ba1a1a]'
                              : ghat.tier === 'MEDIUM'
                              ? 'bg-[#fef3c7] text-[#d97706] border-[#d97706]'
                              : 'bg-[#f1f5f9] text-[#64748b] border-[#64748b]'
                          }`}
                        >
                          #{ghat.rank}
                        </div>

                        <div className="flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="font-bold text-base text-[#0f2942]">
                              {ghat.site}
                            </span>
                            {coords?.nameHi && (
                              <span className="text-xs text-[#64748b]">
                                ({coords.nameHi})
                              </span>
                            )}
                            {/* Tier Badge */}
                            <span
                              className={`px-2 py-0.5 rounded text-[11px] font-bold ${tierBadge.bg} ${tierBadge.text}`}
                            >
                              {ghat.tier}
                            </span>

                            {/* NOT TESTED Badge if true */}
                            {ghat.untested_latest_durga && (
                              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#475569] text-white">
                                NOT TESTED Durga 2025
                              </span>
                            )}
                          </div>

                          {/* Tier Note if present */}
                          {ghat.tier_note && (
                            <p className="text-xs text-[#b45309] font-medium mt-1 bg-[#fffbeb] p-1.5 rounded border border-[#fef3c7]">
                              ⚠️ {ghat.tier_note}
                            </p>
                          )}

                          {/* Site Note if present */}
                          {ghat.site_note && (
                            <p className="text-xs text-[#ba1a1a] font-medium mt-1">
                              {ghat.site_note}
                            </p>
                          )}

                          {/* Tags Chips */}
                          {ghat.tags && ghat.tags.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1.5 mt-2">
                              {ghat.tags.map((tag, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 rounded bg-[#f1f5f9] text-[#475569] text-[11px] font-medium border border-[#e2e8f0]"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}

                          {/* First Reason shown prominently with Pages */}
                          {ghat.reasons && ghat.reasons[0] && (
                            <div className="mt-2.5 text-xs text-[#334155] bg-white p-2.5 rounded border border-[#e2e8f0]">
                              <div className="font-semibold text-[#0f2942] mb-1">
                                {ghat.reasons[0].text}
                              </div>
                              {ghat.reasons[0].pages && (
                                <div className="flex flex-wrap items-center gap-1.5 mt-1 font-mono text-[11px]">
                                  <span className="text-[#64748b]">रिपोर्ट पृष्ठ:</span>
                                  {ghat.reasons[0].pages.map((p, pIdx) => (
                                    <span
                                      key={pIdx}
                                      className="px-1.5 py-0.2 rounded bg-[#f8fafc] text-[#0f2942] border border-[#cbd5e1]"
                                    >
                                      {p}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Right: Actions / Detail Link */}
                      <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2 shrink-0">
                        <Link
                          to={`/ghat/${ghat.rank}`}
                          className="px-3 py-1.5 bg-[#0f2942] hover:bg-[#1e40af] text-white rounded text-xs font-bold flex items-center gap-1 transition-colors shadow-xs"
                        >
                          <span>विस्तार / Detail</span>
                          <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                        </Link>

                        {ghat.actions && (
                          <span className="text-[11px] text-[#64748b] font-mono">
                            {ghat.actions.length} विहित कार्य (Actions)
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Line under the list: how_ranked explanation */}
            {rankingData?.how_ranked && (
              <div className="bg-[#f8fafc] border-t border-[#e2e8f0] p-4 text-xs text-[#475569] leading-relaxed">
                <span className="font-bold text-[#0f2942] block mb-1">
                  रैंकिंग प्रक्रिया एवं कार्यप्रणाली / How this is ranked:
                </span>
                {rankingData.how_ranked}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: QUICK INSPECTOR / DOSSIER PANEL (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          {selectedGhat ? (
            <div className="bg-white rounded-xl border border-[#cbd5e1] p-5 shadow-sm flex flex-col gap-4 sticky top-20">
              <div className="flex items-center justify-between pb-3 border-b border-[#f1f5f9]">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-3 h-3 rounded-full ${
                      selectedGhat.tier === 'HIGH'
                        ? 'bg-[#ba1a1a]'
                        : selectedGhat.tier === 'MEDIUM'
                        ? 'bg-[#d97706]'
                        : 'bg-[#64748b]'
                    }`}
                  ></span>
                  <span className="font-mono text-xs font-bold text-[#0f2942]">
                    RANK #{selectedGhat.rank} · {selectedGhat.tier} TIER
                  </span>
                </div>
                <Link
                  to={`/ghat/${selectedGhat.rank}`}
                  className="text-xs font-bold text-[#0284c7] hover:underline"
                >
                  Full Dossier →
                </Link>
              </div>

              <div>
                <h3 className="text-lg font-bold text-[#0f2942]">
                  {selectedGhat.site}
                </h3>
                <p className="text-xs text-[#64748b] font-mono mt-0.5">
                  {selectedGhat.water_body}
                </p>
              </div>

              {/* Derived Stats Chips */}
              {selectedGhat.derived && (
                <div className="grid grid-cols-2 gap-2 bg-[#f8fafc] p-3 rounded-lg border border-[#e2e8f0] text-xs">
                  <div>
                    <span className="text-[#64748b] block text-[10px]">न्यूनतम DO (Lowest)</span>
                    <span className="font-mono font-bold text-sm text-[#ba1a1a]">
                      {selectedGhat.derived.oxygen_lowest ?? 'N/A'} mg/l
                    </span>
                  </div>
                  <div>
                    <span className="text-[#64748b] block text-[10px]">पूर्व मध्यिका (Before)</span>
                    <span className="font-mono font-bold text-sm text-[#0f2942]">
                      {selectedGhat.derived.oxygen_before_median ?? 'N/A'} mg/l
                    </span>
                  </div>
                  <div>
                    <span className="text-[#64748b] block text-[10px]">विसर्जन गिरावट (Drop)</span>
                    <span className="font-mono font-bold text-sm text-[#b45309]">
                      {selectedGhat.derived.oxygen_drop_median ?? 'N/A'} mg/l
                    </span>
                  </div>
                  <div>
                    <span className="text-[#64748b] block text-[10px]">पुनर्प्राप्ति (Recovery)</span>
                    <span className="font-mono font-bold text-sm text-[#475569]">
                      {selectedGhat.derived.oxygen_recovery_median ?? 'N/A'} mg/l
                    </span>
                  </div>
                </div>
              )}

              {/* Action Checklist */}
              {selectedGhat.actions && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#0f2942] mb-2 flex items-center justify-between">
                    <span>विहित कार्यवाहियां / Action Checklist</span>
                    <span className="font-mono text-[11px] text-[#64748b]">
                      {selectedGhat.actions.length} items
                    </span>
                  </h4>
                  <ul className="space-y-1.5 text-xs text-[#334155]">
                    {selectedGhat.actions.slice(0, 4).map((act, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-[#f8fafc] p-2 rounded border border-[#e2e8f0]">
                        <span className="material-symbols-outlined text-[#0284c7] text-[16px] shrink-0 mt-0.5">
                          check_circle
                        </span>
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Verify chips / Doubtful readings to confirm with MPPCB */}
              {selectedGhat.verify && selectedGhat.verify.length > 0 && (
                <div className="bg-[#fffbeb] p-3 rounded-lg border border-[#fef3c7]">
                  <div className="text-xs font-bold text-[#b45309] mb-1.5 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px]">help_outline</span>
                    <span>MPPCB संशयित रीडिंग (Confirm with Lab)</span>
                  </div>
                  <div className="space-y-1">
                    {selectedGhat.verify.slice(0, 2).map((v, vIdx) => (
                      <div key={vIdx} className="text-[11px] text-[#78350f]">
                        • {v.text}
                        {v.pdf && (
                          <a
                            href={getPdfUrl(v.pdf)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-1 text-[#0284c7] font-mono hover:underline font-bold"
                          >
                            [PDF]
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Link
                to={`/ghat/${selectedGhat.rank}`}
                className="w-full py-2.5 bg-[#0f2942] hover:bg-[#1e40af] text-white rounded text-xs font-bold text-center transition-colors shadow-xs"
              >
                सम्पूर्ण घाट विवरण एवं साक्ष्य देखें →
              </Link>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-[#cbd5e1] p-5 text-center text-xs text-[#64748b]">
              लोड हो रहा है...
            </div>
          )}
        </div>
      </div>

      {/* 5. SCREEN 4: "WHAT THIS DATA DOESN'T COVER" (COMPREHENSIVE REGULATORY LIMITATIONS) */}
      <div className="w-full bg-white rounded-xl border border-[#cbd5e1] shadow-sm overflow-hidden mt-2">
        <div className="bg-[#001428] text-white p-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="material-symbols-outlined text-[#ff8843] text-[22px]">policy</span>
            <div>
              <h2 className="text-base font-bold">
                डेटा परिसीमाएं एवं वैधानिक प्रकटीकरण / What This Data Doesn't Cover
              </h2>
              <p className="text-xs text-[#94a3b8]">
                Statutory caveats, methodology disclosures, and unverified data flags (Section 4)
              </p>
            </div>
          </div>

          {/* Verification Badge */}
          {rankingData?.verification && (
            <div className="px-3 py-1.5 bg-[#0f2942] rounded border border-[#334155] flex items-center gap-2">
              <span className="material-symbols-outlined text-[#38bdf8] text-[18px]">verified</span>
              <div className="font-mono text-xs">
                <span className="text-white font-bold">
                  {rankingData.verification.match?.toLocaleString()} / {rankingData.verification.cells?.toLocaleString()}
                </span>{' '}
                <span className="text-[#94a3b8]">numbers read twice</span>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section 1: not_in_data[] */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 text-sm font-bold text-[#ba1a1a]">
              <span className="material-symbols-outlined text-[18px]">do_not_disturb_on</span>
              <h3>डेटा में क्या शामिल नहीं है (Data Exclusions)</h3>
            </div>
            <ul className="space-y-2 text-xs text-[#334155]">
              {(rankingData?.not_in_data || []).map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 bg-[#f8fafc] p-2.5 rounded border border-[#e2e8f0]">
                  <span className="text-[#ba1a1a] font-bold mt-0.5">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Section 2: data_warnings[] */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 text-sm font-bold text-[#d97706]">
              <span className="material-symbols-outlined text-[18px]">warning</span>
              <h3>डेटा चेतावनियां एवं विसंगतियां (Data Warnings & Discrepancies)</h3>
            </div>
            <ul className="space-y-2 text-xs text-[#334155]">
              {(rankingData?.data_warnings || []).map((warn, idx) => (
                <li key={idx} className="flex items-start gap-2 bg-[#fffbeb] p-2.5 rounded border border-[#fef3c7]">
                  <span className="text-[#d97706] font-bold mt-0.5">⚠️</span>
                  <span>{warn}</span>
                </li>
              ))}
            </ul>

            {/* Context Insights: kund_vs_river */}
            {rankingData?.context?.kund_vs_river && (
              <div className="mt-2 bg-[#f0f9ff] p-3 rounded-lg border border-[#bae6fd]">
                <div className="text-xs font-bold text-[#0369a1] mb-1 flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[16px]">info</span>
                  <span>राज्यव्यापी तुलना: कुंड बनाम नदी (Kund vs River Insight)</span>
                </div>
                <p className="text-xs text-[#0c4a6e] leading-relaxed">
                  {rankingData.context.kund_vs_river.text}
                </p>
                <div className="text-[10px] text-[#0284c7] font-mono mt-1">
                  Source: {rankingData.context.kund_vs_river.source}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Section 3: lake_baseline[] */}
        {rankingData?.context?.lake_baseline && rankingData.context.lake_baseline.length > 0 && (
          <div className="px-6 pb-6 pt-2 border-t border-[#f1f5f9]">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0f2942] uppercase tracking-wider mb-3">
              <span className="material-symbols-outlined text-[16px]">water</span>
              <span>नियमित झील निगरानी आधार रेखा (Routine Lake Monitoring Baselines · Not at Ghats)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {rankingData.context.lake_baseline.map((base, idx) => (
                <div key={idx} className="bg-[#f8fafc] p-3 rounded-lg border border-[#e2e8f0] text-xs flex flex-col justify-between">
                  <div>
                    <div className="font-bold text-[#0f2942] flex items-center justify-between">
                      <span>{base.station}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#e2e8f0] text-[#475569]">
                        {base.lake}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#475569] mt-1 leading-normal">
                      {base.text}
                    </p>
                  </div>
                  {base.pdf && (
                    <a
                      href={getPdfUrl(base.pdf)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-flex items-center gap-1 text-[11px] font-mono font-bold text-[#0284c7] hover:underline"
                    >
                      <span>रिपोर्ट देखें / View PDF</span>
                      <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
