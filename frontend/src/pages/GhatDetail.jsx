import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext.jsx';
import { getPdfUrl, GHAT_COORDINATES } from '../api/client.js';

export default function GhatDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { rankingData, lang, openProof } = useApp();
  const [activeTab, setActiveTab] = useState('reasons'); // 'reasons' | 'grid' | 'actions' | 'verify'

  const ghats = rankingData?.ghats || [];

  // Match by rank number or site name
  const currentGhat =
    ghats.find((g) => String(g.rank) === id) ||
    ghats.find((g) => g.site.toLowerCase().includes(String(id).toLowerCase())) ||
    ghats[0] ||
    null;

  if (!currentGhat) {
    return (
      <div className="bg-white rounded-xl p-8 text-center text-sm text-[#64748b] border border-[#e2e8f0]">
        घाट डेटा लोड हो रहा है या उपलब्ध नहीं है...
      </div>
    );
  }

  const currentRank = currentGhat.rank;
  const prevRank = currentRank > 1 ? currentRank - 1 : 7;
  const nextRank = currentRank < 7 ? currentRank + 1 : 1;
  const coords = GHAT_COORDINATES[currentGhat.site];

  // Tier color styling
  const isHigh = currentGhat.tier === 'HIGH';
  const isMed = currentGhat.tier === 'MEDIUM';
  const tierColor = isHigh ? '#ba1a1a' : isMed ? '#d97706' : '#64748b';
  const tierBg = isHigh ? 'bg-[#ba1a1a]' : isMed ? 'bg-[#d97706]' : 'bg-[#64748b]';

  return (
    <div className="flex flex-col gap-6 text-left pb-12">
      {/* 1. TOP BREADCRUMB & PREV/NEXT SELECTOR */}
      <div className="w-full bg-white rounded-lg px-4 py-3 border border-[#e2e8f0] shadow-2xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Link to="/" className="text-[#0f2942] hover:underline font-bold flex items-center gap-1">
            <span className="material-symbols-outlined text-[16px]">arrow_back</span>
            <span>प्राथमिकता सूची / Ranked List</span>
          </Link>
          <span className="text-[#94a3b8]">/</span>
          <span className="font-mono text-[#64748b]">
            Rank #{currentGhat.rank} · {currentGhat.site}
          </span>
        </div>

        {/* Ghat Selector & Navigation */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => navigate(`/ghat/${prevRank}`)}
            className="px-2.5 py-1 rounded bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] font-semibold text-xs transition-colors cursor-pointer flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[14px]">chevron_left</span>
            <span>पूर्व / Prev #{prevRank}</span>
          </button>

          <select
            value={currentGhat.rank}
            onChange={(e) => navigate(`/ghat/${e.target.value}`)}
            className="bg-[#f8fafc] border border-[#cbd5e1] rounded px-2.5 py-1 text-xs font-bold text-[#0f2942] focus:outline-none cursor-pointer"
          >
            {ghats.map((g) => (
              <option key={g.rank} value={g.rank}>
                #{g.rank} {g.site} ({g.tier})
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={() => navigate(`/ghat/${nextRank}`)}
            className="px-2.5 py-1 rounded bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] font-semibold text-xs transition-colors cursor-pointer flex items-center gap-1"
          >
            <span>अगला / Next #{nextRank}</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          </button>
        </div>
      </div>

      {/* 2. HERO SITE HEADER & STATUTORY STATUS */}
      <div className="bg-white rounded-xl border border-[#cbd5e1] p-5 sm:p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            {/* Rank Bubble */}
            <div
              className={`w-14 h-14 rounded-2xl flex flex-col items-center justify-center font-mono font-bold text-white shrink-0 shadow-xs ${tierBg}`}
            >
              <span className="text-[10px] tracking-wider uppercase opacity-80">RANK</span>
              <span className="text-2xl leading-none">#{currentGhat.rank}</span>
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0f2942]">
                  {currentGhat.site}
                </h1>
                {coords?.nameHi && (
                  <span className="text-base text-[#64748b] font-medium">
                    ({coords.nameHi})
                  </span>
                )}
                <span
                  className={`px-2.5 py-1 rounded text-xs font-bold text-white shadow-2xs ${tierBg}`}
                >
                  {currentGhat.tier} TIER
                </span>
                {currentGhat.untested_latest_durga && (
                  <span className="px-2.5 py-1 rounded text-xs font-bold bg-[#475569] text-white">
                    NOT TESTED Durga 2025
                  </span>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-[#475569]">
                <span className="font-mono text-[#0f2942] font-semibold">
                  {currentGhat.water_body}
                </span>
                {coords?.ward && (
                  <>
                    <span className="text-[#cbd5e1]">·</span>
                    <span className="bg-[#f1f5f9] px-2 py-0.5 rounded text-[11px] font-mono">
                      {coords.ward}
                    </span>
                  </>
                )}
                {coords?.basin && (
                  <>
                    <span className="text-[#cbd5e1]">·</span>
                    <span className="text-[#64748b]">{coords.basin}</span>
                  </>
                )}
              </div>

              {/* Tier Note Warning */}
              {currentGhat.tier_note && (
                <div className="mt-2.5 p-2.5 rounded-lg bg-[#fffbeb] border border-[#fef3c7] text-xs text-[#92400e] font-medium">
                  <strong>वैधानिक टिप्पणी:</strong> {currentGhat.tier_note}
                </div>
              )}

              {/* Site Note Warning */}
              {currentGhat.site_note && (
                <div className="mt-2 p-2.5 rounded-lg bg-[#fef2f2] border border-[#fecaca] text-xs text-[#991b1b] font-medium">
                  {currentGhat.site_note}
                </div>
              )}

              {/* Tags */}
              {currentGhat.tags && currentGhat.tags.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
                  {currentGhat.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded bg-[#f1f5f9] text-[#334155] text-xs font-medium border border-[#e2e8f0]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Metrics from derived */}
          {currentGhat.derived && (
            <div className="flex flex-wrap lg:flex-col items-start gap-2 bg-[#f8fafc] p-3.5 rounded-xl border border-[#e2e8f0] text-xs shrink-0 min-w-[200px]">
              <div className="w-full flex items-center justify-between pb-1 border-b border-[#e2e8f0]">
                <span className="text-[#64748b]">न्यूनतम ऑक्सीजन (Lowest):</span>
                <span className="font-mono font-bold text-sm text-[#ba1a1a]">
                  {currentGhat.derived.oxygen_lowest ?? 'N/A'} mg/l
                </span>
              </div>
              <div className="w-full flex items-center justify-between pb-1 border-b border-[#e2e8f0]">
                <span className="text-[#64748b]">पूर्व मध्यिका (Before):</span>
                <span className="font-mono font-bold text-[#0f2942]">
                  {currentGhat.derived.oxygen_before_median ?? 'N/A'} mg/l
                </span>
              </div>
              <div className="w-full flex items-center justify-between pb-1 border-b border-[#e2e8f0]">
                <span className="text-[#64748b]">विसर्जन गिरावट (Drop):</span>
                <span className="font-mono font-bold text-[#d97706]">
                  {currentGhat.derived.oxygen_drop_median ?? 'N/A'} mg/l
                </span>
              </div>
              <div className="w-full flex items-center justify-between">
                <span className="text-[#64748b]">पुनर्प्राप्ति (Recovery):</span>
                <span className="font-mono font-bold text-[#475569]">
                  {currentGhat.derived.oxygen_recovery_median ?? 'N/A'} mg/l
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-[#e2e8f0] mt-6 pt-2 text-xs font-bold">
          <button
            type="button"
            onClick={() => setActiveTab('reasons')}
            className={`pb-2.5 px-3 flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'reasons'
                ? 'border-[#0f2942] text-[#0f2942]'
                : 'border-transparent text-[#64748b] hover:text-[#0f2942]'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">gavel</span>
            <span>वैज्ञानिक आधार एवं साक्ष्य ({currentGhat.reasons?.length || 0})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('grid')}
            className={`pb-2.5 px-3 flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'grid'
                ? 'border-[#0f2942] text-[#0f2942]'
                : 'border-transparent text-[#64748b] hover:text-[#0f2942]'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">grid_on</span>
            <span>निगरानी मैट्रिक्स / Oxygen Grid</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('actions')}
            className={`pb-2.5 px-3 flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'actions'
                ? 'border-[#0f2942] text-[#0f2942]'
                : 'border-transparent text-[#64748b] hover:text-[#0f2942]'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">checklist</span>
            <span>विहित कार्यवाहियां / Actions ({currentGhat.actions?.length || 0})</span>
          </button>

          {currentGhat.verify && currentGhat.verify.length > 0 && (
            <button
              type="button"
              onClick={() => setActiveTab('verify')}
              className={`pb-2.5 px-3 flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
                activeTab === 'verify'
                  ? 'border-[#ba1a1a] text-[#ba1a1a]'
                  : 'border-transparent text-[#64748b] hover:text-[#ba1a1a]'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">flag</span>
              <span>प्रयोगशाला सत्यापन / Verify ({currentGhat.verify.length})</span>
            </button>
          )}
        </div>
      </div>

      {/* 3. TAB 1: ALL REASONS WITH EVIDENCE NUMBERS AS PDF LINKS & QUALITY FLAGS */}
      {activeTab === 'reasons' && (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#0f2942] flex items-center gap-2">
              <span className="material-symbols-outlined text-[#0284c7] text-[20px]">fact_check</span>
              <span>विहित वैज्ञानिक कारण एवं संख्यात्मक साक्ष्य (Reasons & Numerical Evidence)</span>
            </h2>
            <span className="text-xs text-[#64748b] font-mono">
              CPCB Class B Baseline: ≥ 5.0 mg/l O₂
            </span>
          </div>

          <div className="space-y-4">
            {(currentGhat.reasons || []).map((reason, rIdx) => (
              <div
                key={rIdx}
                className="bg-white rounded-xl border border-[#cbd5e1] p-5 shadow-xs"
              >
                {/* Reason Title */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-base font-bold text-[#0f2942] leading-snug">
                      {lang === 'hi' && reason.text_hi ? reason.text_hi : reason.text}
                    </h3>
                    {lang === 'hi' && reason.text && (
                      <p className="text-xs text-[#64748b] mt-0.5">{reason.text}</p>
                    )}
                  </div>

                  {/* Report Pages Chips */}
                  {reason.pages && (
                    <div className="flex flex-wrap items-center gap-1.5 shrink-0 font-mono text-[11px]">
                      {reason.pages.map((p, pIdx) => (
                        <span
                          key={pIdx}
                          className="px-2 py-0.5 rounded bg-[#f1f5f9] text-[#0f2942] border border-[#cbd5e1] font-semibold"
                        >
                          {p}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Evidence Array: The numbers behind each reason */}
                {reason.evidence && reason.evidence.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-[#f1f5f9]">
                    <div className="text-xs font-bold uppercase tracking-wider text-[#64748b] mb-2.5">
                      आधारभूत संख्यात्मक साक्ष्य / Monitored Evidence Records ({reason.evidence.length})
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {reason.evidence.map((ev, evIdx) => (
                        <div
                          key={evIdx}
                          className="bg-[#f8fafc] p-3 rounded-lg border border-[#e2e8f0] text-xs flex flex-col justify-between gap-2 hover:border-[#cbd5e1] transition-all"
                        >
                          <div>
                            {/* Evidence Top: Parameter, Value, Status */}
                            <div className="flex items-start justify-between gap-2">
                              <span className="font-semibold text-[#0f2942]">
                                {ev.parameter}
                              </span>
                              <span className="font-mono font-bold text-sm text-[#ba1a1a]">
                                {ev.value} mg/l
                              </span>
                            </div>

                            {/* Cycle info: Year · Festival · Phase */}
                            <div className="text-[11px] text-[#475569] font-mono mt-1">
                              {ev.festival} {ev.year} · चरण: <strong>{ev.phase}</strong>
                            </div>

                            {/* Quality Flag if any ("verify" chip) */}
                            {ev.quality_flag && (
                              <div className="mt-1.5 inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#fee2e2] text-[#ba1a1a] text-[10px] font-bold border border-[#fecaca]">
                                <span className="material-symbols-outlined text-[12px]">flag</span>
                                <span>{ev.quality_flag}</span>
                              </div>
                            )}
                          </div>

                          {/* Bottom: PDF Citation Button */}
                          <div className="pt-2 border-t border-[#e2e8f0] flex items-center justify-between text-[11px]">
                            <span className="font-mono text-[#64748b]">
                              पृष्ठ {ev.page}
                            </span>
                            {ev.pdf && (
                              <a
                                href={getPdfUrl(ev.pdf)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 px-2 py-1 bg-white hover:bg-[#f1f5f9] text-[#0284c7] border border-[#cbd5e1] rounded font-bold transition-colors cursor-pointer"
                              >
                                <span>रिपोर्ट PDF खोलें</span>
                                <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. TAB 2: OXYGEN SURVEILLANCE GRID */}
      {activeTab === 'grid' && (
        <div className="bg-white rounded-xl border border-[#cbd5e1] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-[#0f2942]">
                घुलित ऑक्सीजन निगरानी मैट्रिक्स (Oxygen Surveillance Grid)
              </h2>
              <p className="text-xs text-[#64748b]">
                Pre, during, and post-visarjan dissolved oxygen readings with direct PDF citations
              </p>
            </div>
            <span className="text-xs font-mono text-[#ba1a1a] bg-[#fee2e2] px-2.5 py-1 rounded font-bold">
              Baseline: ≥ 5.0 mg/l
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-[#0f2942] text-white font-mono text-[11px]">
                  <th className="p-3 border border-slate-700">वर्ष एवं उत्सव</th>
                  <th className="p-3 border border-slate-700">विसर्जन पूर्व (Pre)</th>
                  <th className="p-3 border border-slate-700">विसर्जन समय (During)</th>
                  <th className="p-3 border border-slate-700">विसर्जन 1 सप्ताह बाद (After)</th>
                  <th className="p-3 border border-slate-700">शुद्ध गिरावट / पुनर्प्राप्ति</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e2e8f0]">
                {(currentGhat.oxygen_grid || []).map((row, idx) => {
                  const pre = row.phases?.pre;
                  const during = row.phases?.during;
                  const after = row.phases?.after;

                  const drop =
                    pre?.value !== undefined && during?.value !== undefined
                      ? (during.value - pre.value).toFixed(1)
                      : null;

                  return (
                    <tr key={idx} className="hover:bg-[#f8fafc]">
                      <td className="p-3 font-bold text-[#0f2942] border border-[#e2e8f0]">
                        {row.festival} {row.year}
                      </td>

                      {/* Pre */}
                      <td className="p-3 border border-[#e2e8f0]">
                        {pre ? (
                          <div>
                            <span
                              className={`font-mono font-bold ${
                                pre.value < 5.0 ? 'text-[#ba1a1a]' : 'text-[#0f2942]'
                              }`}
                            >
                              {pre.value} mg/l
                            </span>
                            {pre.quality_flag && (
                              <div className="text-[10px] text-[#b45309]">⚠️ {pre.quality_flag}</div>
                            )}
                            {pre.pdf && (
                              <a
                                href={getPdfUrl(pre.pdf)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block text-[10px] text-[#0284c7] font-mono hover:underline mt-0.5"
                              >
                                पृ. {pre.page} [PDF]
                              </a>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-400 font-mono">No data</span>
                        )}
                      </td>

                      {/* During */}
                      <td className="p-3 border border-[#e2e8f0]">
                        {during ? (
                          <div>
                            <span
                              className={`font-mono font-bold ${
                                during.value < 5.0 ? 'text-[#ba1a1a]' : 'text-[#0f2942]'
                              }`}
                            >
                              {during.value} mg/l
                            </span>
                            {during.quality_flag && (
                              <div className="text-[10px] text-[#b45309]">⚠️ {during.quality_flag}</div>
                            )}
                            {during.pdf && (
                              <a
                                href={getPdfUrl(during.pdf)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block text-[10px] text-[#0284c7] font-mono hover:underline mt-0.5"
                              >
                                पृ. {during.page} [PDF]
                              </a>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-400 font-mono">No data</span>
                        )}
                      </td>

                      {/* After */}
                      <td className="p-3 border border-[#e2e8f0]">
                        {after ? (
                          <div>
                            <span
                              className={`font-mono font-bold ${
                                after.value < 5.0 ? 'text-[#ba1a1a]' : 'text-[#0f2942]'
                              }`}
                            >
                              {after.value} mg/l
                            </span>
                            {after.quality_flag && (
                              <div className="text-[10px] text-[#b45309]">⚠️ {after.quality_flag}</div>
                            )}
                            {after.pdf && (
                              <a
                                href={getPdfUrl(after.pdf)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block text-[10px] text-[#0284c7] font-mono hover:underline mt-0.5"
                              >
                                पृ. {after.page} [PDF]
                              </a>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-400 font-mono">No data</span>
                        )}
                      </td>

                      {/* Drop */}
                      <td className="p-3 border border-[#e2e8f0] font-mono font-bold">
                        {drop !== null ? (
                          <span className={Number(drop) < 0 ? 'text-[#ba1a1a]' : 'text-[#0f2942]'}>
                            {drop} mg/l
                          </span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 5. TAB 3: ACTIONS CHECKLIST */}
      {activeTab === 'actions' && (
        <div className="bg-white rounded-xl border border-[#cbd5e1] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-[#0f2942]">
                विहित कार्यवाहियां एवं निवारक चेकलिस्ट (Intervention Checklist)
              </h2>
              <p className="text-xs text-[#64748b]">
                Standard Operating Procedures and NGT/CPCB compliance measures for {currentGhat.site}
              </p>
            </div>
            <a
              href={`https://wa.me/?text=${encodeURIComponent(
                `*BMC WORK ORDER · ${currentGhat.site} (RANK #${currentGhat.rank})*\n` +
                  (currentGhat.actions || []).map((a, i) => `${i + 1}. ${a}`).join('\n')
              )}`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 bg-[#0f2942] hover:bg-[#1e40af] text-white rounded text-xs font-bold flex items-center gap-1.5 transition-colors shadow-xs"
            >
              <span className="material-symbols-outlined text-[16px]">send</span>
              <span>व्हाट्सएप पर भेजें / Dispatch</span>
            </a>
          </div>

          <div className="space-y-2.5">
            {(currentGhat.actions || []).map((act, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 bg-[#f8fafc] p-3.5 rounded-lg border border-[#e2e8f0]"
              >
                <div className="w-6 h-6 rounded bg-[#0f2942] text-white flex items-center justify-center font-mono font-bold text-xs shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <div className="flex-1 text-xs text-[#1e293b] leading-relaxed">
                  {act}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 6. TAB 4: DOUBTFUL READINGS TO CONFIRM WITH MPPCB (VERIFY) */}
      {activeTab === 'verify' && currentGhat.verify && (
        <div className="bg-white rounded-xl border border-[#cbd5e1] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-[#ba1a1a] flex items-center gap-2">
                <span className="material-symbols-outlined text-[20px]">warning</span>
                <span>MPPCB प्रयोगशाला से पुष्टि हेतु संशयित मान (Doubtful Readings to Confirm)</span>
              </h2>
              <p className="text-xs text-[#64748b]">
                Readings with potential anomalies (zero oxygen, unprinted units, extreme values) requiring lab re-audit
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {currentGhat.verify.map((v, vIdx) => (
              <div
                key={vIdx}
                className="bg-[#fffbeb] p-4 rounded-lg border border-[#fef3c7] flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div>
                  <div className="text-xs font-bold text-[#92400e] flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px]">flag</span>
                    <span>{v.text}</span>
                  </div>
                  {v.quality_flag && (
                    <span className="inline-block mt-1 text-[11px] font-mono text-[#b45309] bg-white px-2 py-0.5 rounded border border-[#fde68a]">
                      Flag: {v.quality_flag}
                    </span>
                  )}
                </div>

                {v.pdf && (
                  <a
                    href={getPdfUrl(v.pdf)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 bg-white hover:bg-[#f8fafc] text-[#0284c7] border border-[#cbd5e1] rounded text-xs font-bold font-mono shrink-0 flex items-center gap-1 shadow-xs"
                  >
                    <span>मूल रिपोर्ट (पृ. {v.page}) [PDF]</span>
                    <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
