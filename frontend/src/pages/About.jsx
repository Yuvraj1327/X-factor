import React from 'react';
import { useApp } from '../context/AppContext.jsx';

export default function About() {
  const { lang } = useApp();

  return (
    <div className="flex flex-col gap-6 text-left">
      {/* Top Header Card */}
      <div className="w-full bg-white rounded-xl p-5 shadow-xs border border-[#c3c6ce]/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs px-2.5 py-1 bg-[#001428] text-white rounded font-bold">
              STANDARDS & METHODOLOGY
            </span>
            <span className="font-semibold text-xs text-[#9e4300]">
              CENTRAL POLLUTION CONTROL BOARD (CPCB) CLASS B
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#001b3d]">
            {lang === 'hi'
              ? 'विश्लेषणात्मक आधार एवं गणना मानक'
              : 'Analytical Basis & Computation Standards'}
          </h1>
          <p className="text-xs sm:text-sm text-[#43474d] mt-1">
            Statutory thresholds, mathematical rank formula, and regulatory operational boundaries
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: The limits we use */}
        <div className="bg-white rounded-xl p-6 shadow-xs border border-[#c3c6ce]/60 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="material-symbols-outlined text-[#9e4300] text-[22px]">policy</span>
              <h2 className="text-xl font-bold text-[#001b3d]">The limits we use</h2>
            </div>
            <p className="text-xs text-[#43474d] mb-4">
              All evaluations reference statutory CPCB Class B standards for organized outdoor bathing and immersion:
            </p>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-[#f0f3ff] rounded-lg border border-[#dfe8ff]">
                <div className="text-[#001428] font-bold">Dissolved Oxygen (DO)</div>
                <div className="text-base font-extrabold text-[#ba1a1a] mt-0.5">≥ 5.0 mg/L</div>
                <div className="text-[11px] text-[#74777e] mt-1">
                  Required for natural biological buffering and fish respiration.
                </div>
              </div>

              <div className="p-3 bg-[#f0f3ff] rounded-lg border border-[#dfe8ff]">
                <div className="text-[#001428] font-bold">Pollution Load (BOD)</div>
                <div className="text-base font-extrabold text-[#9e4300] mt-0.5">≤ 3.0 mg/L</div>
                <div className="text-[11px] text-[#74777e] mt-1">
                  Upper ceiling for organic decomposition burden over 3 days at 27°C.
                </div>
              </div>

              <div className="p-3 bg-[#f0f3ff] rounded-lg border border-[#dfe8ff]">
                <div className="text-[#001428] font-bold">Acidity (pH)</div>
                <div className="text-base font-extrabold text-[#001b3d] mt-0.5">6.5 – 8.5</div>
                <div className="text-[11px] text-[#74777e] mt-1">
                  Standard neutral buffer window against chemical shock.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: How the rank is made */}
        <div className="bg-white rounded-xl p-6 shadow-xs border border-[#c3c6ce]/60 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="material-symbols-outlined text-[#001428] text-[22px]">calculate</span>
              <h2 className="text-xl font-bold text-[#001b3d]">How the rank is made</h2>
            </div>
            <p className="text-xs text-[#43474d] mb-4">
              Ghat priority order is calculated deterministically via a weighted deficit composition algorithm in <span className="font-mono text-[#001428] bg-slate-100 px-1 py-0.5 rounded">src/lib/rank.js</span>:
            </p>

            <div className="p-4 bg-[#f0f3ff] rounded-lg border border-[#dfe8ff] font-mono text-xs text-[#001b3d] space-y-2 mb-4">
              <div className="font-bold text-[#9e4300]">COMPOSITE DEFICIT SCORE:</div>
              <div className="text-sm font-extrabold text-[#001428]">
                2.0 × (DO Deficit) + 1.2 × (BOD Excess)
              </div>
              <div className="text-[11px] text-[#43474d] pt-2 border-t border-[#dfe8ff]">
                • DO Deficit = Max(0, 5.0 - DO_reading)<br/>
                • BOD Excess = Max(0, BOD_reading - 3.0)<br/>
                • Missing records penalized appropriately
              </div>
            </div>

            <div className="text-xs text-[#43474d] leading-relaxed">
              Ghats with the largest composite deficits are prioritized at Rank #1 to receive pre-visarjan aeration diffusers, silt curtains, and field teams.
            </div>
          </div>
        </div>

        {/* Card 3: What this does NOT cover (Rule 7: Strict compliance) */}
        <div className="bg-white rounded-xl p-6 shadow-xs border border-[#ba1a1a]/40 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="material-symbols-outlined text-[#ba1a1a] text-[22px]">gavel</span>
              <h2 className="text-xl font-bold text-[#ba1a1a]">What this does NOT cover</h2>
            </div>
            <p className="text-xs text-[#43474d] mb-4 font-semibold">
              Statutory transparency disclosures and regulatory boundaries:
            </p>

            <div className="space-y-3 text-xs text-[#001b3d]">
              <div className="p-3 bg-[#ffdad6]/40 rounded-lg border border-[#ba1a1a]/30">
                <div className="font-bold text-[#ba1a1a] mb-1">No Potability or Health Claims</div>
                <p className="text-[11px] text-[#43474d]">
                  This platform measures environmental receptor water compliance. It does not certify water as potable drinking water and makes no epidemiological claims.
                </p>
              </div>

              <div className="p-3 bg-[#f0f3ff] rounded-lg border border-[#dfe8ff]">
                <div className="font-bold text-[#001428] mb-1">Strict Prohibition on Vague Terminology</div>
                <p className="text-[11px] text-[#43474d]">
                  Per strict civic guidelines, this system deliberately avoids subjective language such as "safe", "clean", "dangerous", or "low risk". All states are reported solely as measured figures against statutory CPCB limits.
                </p>
              </div>

              <div className="p-3 bg-[#f0f3ff] rounded-lg border border-[#dfe8ff]">
                <div className="font-bold text-[#001428] mb-1">Zero Green Visual Indicator Policy</div>
                <p className="text-[11px] text-[#43474d]">
                  To prevent false perceptions of ecological purity in stressed urban reservoirs, green is strictly omitted across all dashboards and charts.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
