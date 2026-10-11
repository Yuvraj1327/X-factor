import React from 'react';
import { useApp } from '../context/AppContext.jsx';

export default function ProofDrawer() {
  const { proof, closeProof, lang } = useApp();

  if (!proof.isOpen) return null;

  return (
    <>
      {/* Drawer Overlay Scrim */}
      <div
        className="fixed inset-0 bg-[#001428]/60 backdrop-blur-xs z-50 transition-opacity"
        onClick={closeProof}
      />

      {/* Slide-over (desktop) / Bottom sheet (mobile) */}
      <div
        className="fixed inset-x-0 bottom-0 sm:inset-y-0 sm:left-auto sm:right-0 w-full sm:w-[480px] max-h-[85vh] sm:max-h-full bg-white shadow-2xl z-50 flex flex-col overflow-hidden border-t sm:border-t-0 sm:border-l border-[#c3c6ce] rounded-t-2xl sm:rounded-none animate-in slide-in-from-bottom sm:slide-in-from-right duration-300"
      >
        {/* Panel Header */}
        <div className="bg-[#001428] text-white p-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#ff8843] text-[22px]">verified</span>
            <div className="flex flex-col">
              <span className="font-semibold text-sm">
                {lang === 'hi' ? 'आधिकारिक साक्ष्य अभिलेख' : 'Official Proof Record'}
              </span>
              <span className="font-mono text-xs text-[#b0c9e8]">
                LEVEL 4 GAZZETTE SOURCE CITATION
              </span>
            </div>
          </div>
          <button
            className="w-10 h-10 flex items-center justify-center rounded bg-[#0f2942] text-white hover:bg-[#1b365d] transition-colors cursor-pointer"
            onClick={closeProof}
            type="button"
            aria-label="Close"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Panel Content */}
        <div className="p-5 flex-1 overflow-y-auto flex flex-col gap-4 text-left">
          {/* Active Reference Chip */}
          <div className="flex items-center justify-between bg-[#f0f3ff] p-3 rounded-lg border border-[#d6e3ff]">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#43474d]">
              {lang === 'hi' ? 'स्रोत संदर्भ:' : 'Source Reference:'}
            </span>
            <span className="font-mono text-xs px-2.5 py-1 bg-[#001428] text-white rounded font-bold">
              Report {proof.reportYear} · Page {proof.reportPage}
            </span>
          </div>

          {/* Metric Card */}
          <div className="bg-[#f9f9ff] rounded-xl p-4 flex flex-col gap-3 border border-[#c3c6ce]/60 shadow-xs">
            <div className="text-xs font-semibold text-[#74777e] uppercase tracking-wider">
              {lang === 'hi' ? 'निगरानी पैरामीटर' : 'Monitored Parameter'}
            </div>
            <div className="text-xl font-bold text-[#001b3d]">
              {proof.param}
            </div>

            <div className="p-3 bg-white rounded-lg flex items-center justify-between border border-[#e2e8f0]">
              <span className="text-xs font-medium text-[#43474d]">
                {lang === 'hi' ? 'सत्यापित मान:' : 'Cleaned Metric:'}
              </span>
              <span className="text-2xl font-bold font-mono text-[#ba1a1a]">
                {proof.cleanedValue} {proof.unit}
              </span>
            </div>

            <div className="p-3 bg-[#f8fafc] rounded-lg flex items-center justify-between border border-[#e2e8f0]">
              <span className="text-xs font-medium text-[#43474d]">
                {lang === 'hi' ? 'मूल पाठ (Raw):' : 'Raw Report Value:'}
              </span>
              <span className="text-sm font-semibold font-mono text-[#001428]">
                {proof.rawValue}
              </span>
            </div>

            <div className="space-y-2 pt-2 text-xs border-t border-[#e2e8f0]">
              <div className="flex items-start justify-between gap-2">
                <span className="text-[#74777e] font-medium">Statutory Standard:</span>
                <span className="font-mono text-[#001b3d] text-right font-bold">
                  {proof.standard}
                </span>
              </div>
              <div className="flex items-start justify-between gap-2">
                <span className="text-[#74777e] font-medium">Station:</span>
                <span className="font-mono text-[#001b3d] text-right">
                  {proof.station}
                </span>
              </div>
              <div className="flex items-start justify-between gap-2">
                <span className="text-[#74777e] font-medium">Data State:</span>
                <span className="font-mono text-[#001b3d] text-right font-semibold">
                  {proof.dataState}
                </span>
              </div>
            </div>
          </div>

          {/* Gazette Facsimile Extract Snippet */}
          <div className="bg-[#f0f3ff] rounded-lg p-3 border border-[#d6e3ff]">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-[11px] text-[#43474d] font-bold">
                BMC REGULATORY GAZETTE AUDIT SNIPPET
              </span>
              <span className="text-[10px] font-mono text-[#9e4300] font-bold">
                AUDIT HASH #BPL-{proof.reportYear}-Q3
              </span>
            </div>
            <div className="bg-white p-3 rounded font-mono text-xs text-[#001b3d] space-y-1 overflow-x-auto border border-[#c3c6ce]/50">
              <div className="text-slate-400">--------------------------------------------------</div>
              <div className="font-bold text-slate-800">
                TABLE 4.2 · POST-VISARJAN IMMERSION WATER QUALITY
              </div>
              <div className="text-slate-600">STATION: {proof.station.toUpperCase()}</div>
              <div className="text-[#ba1a1a] font-bold">
                &gt;&gt; PARAMETER: {proof.param.toUpperCase()} ....... {proof.rawValue} [NON-COMPLIANT]
              </div>
              <div className="text-slate-600">&gt;&gt; CITATION: GAZETTE REPORT {proof.reportYear} (PAGE {proof.reportPage})</div>
              <div className="text-slate-400">--------------------------------------------------</div>
            </div>
          </div>

          {/* Action Button */}
          <button
            className="mt-2 w-full min-h-[44px] bg-[#001428] text-white rounded font-medium text-sm hover:bg-[#0f2942] transition-colors flex items-center justify-center gap-2 cursor-pointer"
            onClick={() => alert(`Downloading signed BMC gazette excerpt for ${proof.station} (Report ${proof.reportYear}, Page ${proof.reportPage})...`)}
            type="button"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            <span>Download Verified Excerpt (PDF)</span>
          </button>
        </div>
      </div>
    </>
  );
}
