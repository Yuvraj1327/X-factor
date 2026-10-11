import React, { useState } from 'react';
import { useApp } from '../context/AppContext.jsx';

export default function Coverage() {
  const { openProof } = useApp();
  const [highlightGaps, setHighlightGaps] = useState(false);
  const [sortBy, setSortBy] = useState('completeness'); // 'completeness' | 'risk'
  const [inspectedCell, setInspectedCell] = useState(null);

  // 7 Ghats Matrix Data with exact percentages from Screenshot 2
  const matrixGhats = [
    {
      id: '1',
      name: '1. Khatlapura Ghat',
      basin: 'Lower Lake · छोटा तालाब',
      pct: 89,
      // 18 phases: 9 Ganesh (3 yrs x 3 phases), 9 Durga (3 yrs x 3 phases)
      // States: 'M' (measured), 'B' (BDL), 'S' (skipped/not sampled), 'V' (void table)
      phases: ['M','M','M', 'M','M','M', 'M','M','M', 'M','M','B', 'M','M','M', 'M','M','M']
    },
    {
      id: '2',
      name: '2. Prempura Ghat',
      basin: 'Upper Lake · बड़ा तालाब',
      pct: 83,
      phases: ['M','M','M', 'M','M','M', 'M','M','M', 'S','M','M', 'M','M','M', 'M','M','M']
    },
    {
      id: '3',
      name: '3. Rani Kamlapati Ghat',
      basin: 'Kamla Park Conflated Site',
      pct: 77,
      phases: ['M','M','M', 'S','M','M', 'M','M','M', 'M','M','M', 'S','M','M', 'M','M','M']
    },
    {
      id: '4',
      name: '4. Hathaikheda Dam',
      basin: 'Eastern Catchment Enclosure',
      pct: 74,
      phases: ['M','M','M', 'S','M','M', 'S','M','M', 'M','M','B', 'M','M','M', 'M','S','M']
    },
    {
      id: '5',
      name: '5. Bairagarh (Sant Hirdaram)',
      basin: 'Ward 04 Artificial Kund',
      pct: 71,
      phases: ['M','M','M', 'M','M','M', 'S','M','M', 'M','M','M', 'M','M','M', 'M','V','M']
    },
    {
      id: '6',
      name: '6. Malikhedi Kund',
      basin: 'Vidisha Bypass Enclosure',
      pct: 60,
      phases: ['M','M','M', 'M','M','M', 'M','M','M', 'M','M','M', 'S','M','M', 'V','B','V']
    },
    {
      id: '7',
      name: '7. Shahpura Lake',
      basin: 'Sector 08 Urban Catchment',
      pct: 48,
      phases: ['S','M','M', 'S','M','M', 'S','M','M', 'S','M','B', 'S','M','M', 'S','M','M']
    }
  ];

  const sortedGhats = [...matrixGhats].sort((a, b) => {
    if (sortBy === 'completeness') return b.pct - a.pct;
    return a.pct - b.pct;
  });

  return (
    <div className="flex flex-col gap-4 text-left">
      {/* 1. TOP TITLE HEADER (Matching Screenshot 2) */}
      <div className="w-full bg-white rounded-xl p-5 border border-[#e2e8f0] shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <h1 className="text-xl sm:text-2xl font-extrabold text-[#0f2942]">
              Data Coverage <span className="font-normal text-[#64748b]">· डेटा कवरेज व निगरानी पूर्णता</span>
            </h1>
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-[#f1f5f9] text-[#475569] font-bold border border-[#cbd5e1]">
              126 Statutory Cell Matrix
            </span>
            <span className="text-xs text-[#64748b] bg-[#f8fafc] px-2 py-0.5 rounded border border-[#e2e8f0]">
              7 Statutory Water Bodies
            </span>
          </div>
          <p className="text-xs text-[#64748b] max-w-4xl leading-relaxed">
            Statutory surveillance completeness audit across 7 visarjan water bodies (2023–2025) pursuant to MPPCB CPCB Class B outdoor bathing criteria. Visual audit for instant deficit diagnosis ahead of Durga Visarjan.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => setSortBy('completeness')}
            className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors cursor-pointer ${
              sortBy === 'completeness'
                ? 'bg-[#0f2942] text-white border-[#0f2942]'
                : 'bg-white text-[#334155] border-[#cbd5e1] hover:bg-[#f8fafc]'
            }`}
          >
            Sort by Completeness
          </button>
          <button
            type="button"
            onClick={() => setSortBy('risk')}
            className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors cursor-pointer ${
              sortBy === 'risk'
                ? 'bg-[#ba1a1a] text-white border-[#ba1a1a]'
                : 'bg-white text-[#334155] border-[#cbd5e1] hover:bg-[#f8fafc]'
            }`}
          >
            ! Sort by Risk Rank
          </button>
          <button
            type="button"
            onClick={() => setHighlightGaps(!highlightGaps)}
            className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors cursor-pointer flex items-center gap-1.5 ${
              highlightGaps
                ? 'bg-[#fee2e2] text-[#ba1a1a] border-[#fecaca]'
                : 'bg-white text-[#334155] border-[#cbd5e1] hover:bg-[#f8fafc]'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#ba1a1a]"></span>
            <span>Highlight Gaps (28)</span>
          </button>
          <button
            type="button"
            onClick={() => window.print()}
            className="px-3.5 py-1.5 bg-[#9a3412] hover:bg-[#c2410c] text-white rounded text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
          >
            <span className="material-symbols-outlined text-[15px]">print</span>
            <span>Print Matrix</span>
          </button>
        </div>
      </div>

      {/* 2. THREE STATUTORY SCORECARDS (Matching Screenshot 2) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card 1: Protocol Execution / Completeness */}
        <div className="bg-white rounded-xl p-5 border border-[#e2e8f0] shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-[#64748b] mb-3">
              <span className="font-bold text-[#0f2942]">PROTOCOL EXECUTION</span>
              <span className="bg-[#f1f5f9] px-2 py-0.5 rounded font-bold">126 Test Points</span>
            </div>
            <h2 className="text-base font-bold text-[#0f2942] mb-3">
              डेटा पूर्णता / Completeness
            </h2>

            <div className="flex items-center gap-5 my-2">
              {/* Donut graphic */}
              <div className="relative w-24 h-24 shrink-0 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="14" fill="none" stroke="#e2e8f0" strokeWidth="4"></circle>
                  <circle
                    cx="18"
                    cy="18"
                    r="14"
                    fill="none"
                    stroke="#0f2942"
                    strokeWidth="4"
                    strokeDasharray="88"
                    strokeDashoffset="19.3"
                  ></circle>
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="font-mono text-xl font-extrabold text-[#0f2942]">78%</span>
                  <span className="text-[9px] font-bold text-[#64748b] leading-none">VERIFIED</span>
                </div>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="bg-[#f8fafc] border border-[#e2e8f0] p-1.5 rounded text-[11px]">
                  <div className="text-[10px] text-[#64748b]">TARGET MINIMUM</div>
                  <strong className="text-[#0f2942]">100% CPCB Class B</strong>
                </div>
                <div className="bg-[#fef2f2] border border-[#fecaca] p-1.5 rounded text-[11px]">
                  <div className="text-[10px] text-[#ba1a1a] font-bold">AUDIT DEFICIT</div>
                  <strong className="text-[#ba1a1a]">22% (28 Cells Void/Gap)</strong>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-[#f1f5f9] flex items-center justify-between text-[11px] font-mono text-[#64748b]">
            <span>Central Zonal Order OA 36/2021</span>
            <span className="text-[#0f2942] font-bold">Statutory Baseline Active</span>
          </div>
        </div>

        {/* Card 2: Surveillance Quality / Verification Share */}
        <div className="bg-white rounded-xl p-5 border border-[#e2e8f0] shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-[#64748b] mb-3">
              <span className="font-bold text-[#0f2942]">SURVEILLANCE QUALITY</span>
              <span className="material-symbols-outlined text-[16px] text-[#9a3412]">donut_large</span>
            </div>
            <h2 className="text-base font-bold text-[#0f2942] mb-3">
              सत्यापन विवरण / Verification Share
            </h2>

            <div className="flex items-center gap-5 my-2">
              {/* Donut chart */}
              <div className="relative w-24 h-24 shrink-0 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="14" fill="none" stroke="#e2e8f0" strokeWidth="4"></circle>
                  <circle cx="18" cy="18" r="14" fill="none" stroke="#0f2942" strokeWidth="4" strokeDasharray="88" strokeDashoffset="19.3"></circle>
                  <circle cx="18" cy="18" r="14" fill="none" stroke="#ea580c" strokeWidth="4" strokeDasharray="88" strokeDashoffset="78.3"></circle>
                </svg>
                <div className="absolute flex flex-col items-center text-center">
                  <span className="font-mono text-xs font-bold text-[#0f2942]">126</span>
                  <span className="text-[8px] text-[#64748b]">TOTAL CELLS</span>
                </div>
              </div>

              {/* Legend with exact numbers from Screenshot 2 */}
              <div className="space-y-1 text-[11px] font-mono text-[#334155]">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#0f2942]"></span>
                  <span>Measured: <strong>98 (78%)</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#ea580c]"></span>
                  <span>BDL Trace: <strong>14 (11%)</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm pattern-hatched border border-[#cbd5e1]"></span>
                  <span>Skipped: <strong>10 (8%)</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm pattern-dark-hatched border border-[#334155]"></span>
                  <span>Void Table: <strong className="text-[#ba1a1a]">4 (3%)</strong></span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-[#f1f5f9] flex items-center justify-between text-[11px] font-mono text-[#64748b]">
            <span>Physical MPPCB Registers</span>
            <span className="text-[#ba1a1a] font-bold">4 Critical Omissions</span>
          </div>
        </div>

        {/* Card 3: Site Compliance / Ghat Integrity Tiers */}
        <div className="bg-white rounded-xl p-5 border border-[#e2e8f0] shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-[#64748b] mb-1">
              <span className="font-bold text-[#0f2942]">SITE COMPLIANCE</span>
              <span className="material-symbols-outlined text-[16px] text-[#0f2942]">bar_chart</span>
            </div>
            <h2 className="text-base font-bold text-[#0f2942] mb-2">
              घाटवार स्तर / Ghat Integrity Tiers
            </h2>

            {/* List of Bars matching Screenshot 2 */}
            <div className="space-y-1 text-[11px]">
              {matrixGhats.map((g) => (
                <div key={g.id} className="flex items-center justify-between gap-2">
                  <span className="truncate w-32 text-[#334155]">{g.name.split('. ')[1]}</span>
                  <div className="flex-1 h-1.5 bg-[#e2e8f0] rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        g.pct >= 75 ? 'bg-[#0f2942]' : g.pct >= 60 ? 'bg-[#d97706]' : 'bg-[#ba1a1a]'
                      }`}
                      style={{ width: `${g.pct}%` }}
                    ></div>
                  </div>
                  <span className="font-mono text-[10px] font-bold text-[#0f2942] w-8 text-right">
                    {g.pct}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-2 mt-2 border-t border-[#f1f5f9] flex items-center justify-between text-[10px] font-mono text-[#64748b]">
            <span>Tier 1: ≥75% (4 sites)</span>
            <span className="text-[#ba1a1a] font-bold">Critical: Shahpura Lake (&lt;50%)</span>
          </div>
        </div>
      </div>

      {/* 3. 18-CYCLE MULTI-YEAR SURVEILLANCE MATRIX TABLE (Matching Screenshot 2) */}
      <div className="bg-white rounded-xl border border-[#cbd5e1] shadow-2xs overflow-hidden">
        {/* Table Title Bar */}
        <div className="p-4 border-b border-[#e2e8f0] flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-base text-[#0f2942]">
                18-Cycle Multi-Year Surveillance Matrix · बहु-वर्षीय निगरानी ग्रिड
              </h2>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-[#f1f5f9] text-[#475569] font-bold border border-[#cbd5e1]">
                Full Width View · 7 Ghats × 18 Phases
              </span>
            </div>
            <p className="text-xs text-[#64748b] mt-0.5">
              Statutory sampling rounds covering Ganesh Visarjan &amp; Durga Visarjan (Pre-immersion / PRE (B), During / DUR (D), Post-immersion / PST (A)).
            </p>
          </div>

          {/* Status Protocol Legend */}
          <div className="flex items-center gap-3 text-xs font-mono bg-[#f8fafc] px-3 py-1.5 rounded border border-[#e2e8f0]">
            <span className="font-bold text-[#0f2942]">STATUS PROTOCOL:</span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 bg-[#0f2942] rounded-xs"></span> Measured
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 bg-[#ea580c] rounded-xs"></span> BDL / ND
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 pattern-hatched border border-[#cbd5e1] rounded-xs"></span> Not Sampled
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 pattern-dark-hatched border border-[#334155] rounded-xs"></span> Void Table
            </span>
          </div>
        </div>

        {/* Matrix Grid Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              {/* Row 1: Cycle Group Headers */}
              <tr className="border-b border-[#cbd5e1]">
                <th className="p-2.5 bg-[#f8fafc] text-[#0f2942] font-mono text-[11px] font-bold w-56 border-r border-[#cbd5e1]">
                  WATER BODY / GHAT (घाट व जल निकाय)
                </th>
                <th colSpan={9} className="p-2 bg-[#0f2942] text-white font-mono text-[11px] font-bold text-center border-r border-[#cbd5e1]">
                  GANESH VISARJAN CYCLES · गणेश विसर्जन (2023 - 2025)
                </th>
                <th colSpan={9} className="p-2 bg-[#b91c1c] text-white font-mono text-[11px] font-bold text-center">
                  DURGA VISARJAN CYCLES · दुर्गा विसर्जन (2023 - 2025)
                </th>
              </tr>
              {/* Row 2: Years */}
              <tr className="border-b border-[#cbd5e1] font-mono text-[10px] text-center bg-[#f1f5f9]">
                <th className="p-1 bg-[#f8fafc] text-left text-[#64748b] border-r border-[#cbd5e1] px-2.5">
                  Statutory Monitoring Cycle
                </th>
                <th colSpan={3} className="p-1 border-r border-[#cbd5e1]">2023</th>
                <th colSpan={3} className="p-1 border-r border-[#cbd5e1]">2024</th>
                <th colSpan={3} className="p-1 border-r border-[#cbd5e1]">2025</th>
                <th colSpan={3} className="p-1 border-r border-[#cbd5e1]">2023</th>
                <th colSpan={3} className="p-1 border-r border-[#cbd5e1]">2024</th>
                <th colSpan={3} className="p-1">2025</th>
              </tr>
              {/* Row 3: Phases */}
              <tr className="border-b border-[#cbd5e1] font-mono text-[9px] text-[#64748b] text-center bg-[#f8fafc]">
                <th className="p-1 text-left border-r border-[#cbd5e1] px-2.5 font-sans">
                  IMMERSION PHASE
                </th>
                {Array.from({ length: 6 }).map((_, i) => (
                  <React.Fragment key={i}>
                    <th className="p-1 w-7">PRE</th>
                    <th className="p-1 w-7">DUR</th>
                    <th className="p-1 w-7 border-r border-[#cbd5e1]">PST</th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e2e8f0]">
              {sortedGhats.map((ghat) => (
                <tr key={ghat.id} className="hover:bg-[#f8fafc] transition-colors">
                  {/* Name + Pct */}
                  <td className="p-2.5 border-r border-[#cbd5e1]">
                    <div className="flex items-center justify-between gap-1">
                      <div>
                        <div className="font-bold text-[#0f2942] text-[12px]">{ghat.name}</div>
                        <div className="text-[10px] text-[#64748b]">{ghat.basin}</div>
                      </div>
                      <span
                        className={`font-mono text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          ghat.pct >= 75
                            ? 'bg-[#f1f5f9] text-[#0f2942]'
                            : ghat.pct >= 60
                            ? 'bg-[#ffedd5] text-[#c2410c]'
                            : 'bg-[#fee2e2] text-[#ba1a1a]'
                        }`}
                      >
                        {ghat.pct}%
                      </span>
                    </div>
                  </td>

                  {/* 18 Matrix Cells */}
                  {ghat.phases.map((state, cellIdx) => {
                    const isM = state === 'M';
                    const isB = state === 'B';
                    const isS = state === 'S';
                    const isV = state === 'V';
                    const isBorderRight = (cellIdx + 1) % 3 === 0;

                    return (
                      <td
                        key={cellIdx}
                        className={`p-1 text-center ${isBorderRight ? 'border-r border-[#cbd5e1]' : ''}`}
                      >
                        <button
                          type="button"
                          onClick={() => {
                            setInspectedCell({
                              ghat: ghat.name,
                              cycle: cellIdx < 9 ? 'Ganesh' : 'Durga',
                              state: isM ? 'Measured' : isB ? 'BDL' : isS ? 'Not Sampled' : 'Void Table'
                            });
                            openProof({
                              reportYear: cellIdx < 3 || (cellIdx >= 9 && cellIdx < 12) ? '2023' : cellIdx < 6 || (cellIdx >= 12 && cellIdx < 15) ? '2024' : '2025',
                              reportPage: '28',
                              param: 'Surveillance Matrix Cell Verification',
                              station: ghat.name,
                              standard: 'CPCB Class B Baseline: DO ≥ 5.0 mg/L',
                              dataState: isM ? '● Measured In-situ Titration' : isB ? '◐ BDL Trace' : isS ? '⊘ Not Sampled' : '▧ Void Table',
                              cleanedValue: isM ? 'Measured' : state,
                              rawValue: `Matrix Status: ${state} at ${ghat.name}`,
                              unit: ''
                            });
                          }}
                          className={`w-6 h-6 rounded-xs flex items-center justify-center mx-auto transition-transform hover:scale-110 cursor-pointer shadow-2xs ${
                            isM
                              ? 'bg-[#0f2942] text-white'
                              : isB
                              ? 'bg-[#ea580c] text-white'
                              : isS
                              ? 'pattern-hatched border border-[#cbd5e1] text-[#475569]'
                              : 'pattern-dark-hatched border border-[#334155] text-white'
                          } ${highlightGaps && (isS || isV) ? 'ring-2 ring-[#ba1a1a]' : ''}`}
                          title={`${ghat.name}: ${isM ? 'Measured' : isB ? 'BDL' : isS ? 'Not Sampled' : 'Void Table'}`}
                        >
                          {isM && <span className="w-1.5 h-1.5 rounded-full bg-white"></span>}
                          {isB && <span className="font-mono text-[9px] font-bold">◐</span>}
                          {isS && <span className="font-mono text-[9px] font-bold">⊘</span>}
                          {isV && <span className="font-mono text-[9px] font-bold">▧</span>}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Bottom Cell Inspection Register (Matching Screenshot 2) */}
        <div className="p-3 bg-[#f8fafc] border-t border-[#e2e8f0] flex flex-wrap items-center justify-between gap-3 text-xs text-[#475569]">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px] text-[#0f2942]">table_chart</span>
            <div>
              <strong className="text-[#0f2942]">CELL INSPECTION REGISTER (लाइव निरीक्षण):</strong> Hover or click any cell above to inspect statutory DO/BOD metrics, field lab registers, and citation records.
            </div>
          </div>
          <div className="flex items-center gap-3 font-mono text-[11px]">
            <span>CPCB Class B DO &gt; 5.0 mg/l - BOD &lt; 3.0 mg/l</span>
            <button
              type="button"
              onClick={() => setInspectedCell(null)}
              className="text-[#9a3412] hover:underline font-bold cursor-pointer"
            >
              Reset View
            </button>
          </div>
        </div>
      </div>

      {/* 4. MANDATORY 2026 BASELINE DIRECTIVE BANNER (Matching Screenshot 2) */}
      <div className="w-full bg-[#fef2f2] border border-[#fecaca] rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded bg-[#fee2e2] flex items-center justify-center text-[#ba1a1a] shrink-0">
            <span className="material-symbols-outlined text-[20px]">policy</span>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <strong className="text-[#0f2942] text-sm">
                Mandatory 2026 Baseline Directive (आदेश क्रमांक २२/२०२६)
              </strong>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#fee2e2] text-[#ba1a1a]">
                Immediate Action
              </span>
            </div>
            <p className="text-[#64748b]">
              Pursuant to CPCB guidelines, both artificial kunds (Bairagarh &amp; Malikhedi) and 5 open water ghats must implement continuous 48-hour automated multi-parameter telemetry before Durga Visarjan 2026. Void tables from 2025 are scheduled for retrospective inquiry.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => alert('Dispatching statutory compliance memorandum to MPPCB Lake Conservation Wing...')}
          className="px-4 py-2 bg-[#0f2942] hover:bg-[#1e2f42] text-white rounded-lg font-bold text-xs shrink-0 transition-colors cursor-pointer shadow-xs"
        >
          Dispatch Statutory Memo
        </button>
      </div>
    </div>
  );
}
