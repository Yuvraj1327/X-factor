import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApp } from '../context/AppContext.jsx';

export default function ParameterDetail() {
  const { id, param } = useParams();
  const { data, openProof, lang } = useApp();
  const [selectedFestival, setSelectedFestival] = useState('all');

  const ghats = data?.ghats || [];
  const currentGhat = ghats.find((g) => g.id === id || g.slug === id) || ghats[0] || {
    id: '1',
    name: 'Bairagarh (Sant Hirdaram) kund',
    nameHi: 'बैरागढ़ (संत हिरदाराम) कुंड',
    stationId: 'BMC-WQ-BG-01',
    waterBody: 'Upper Lake direct intake zone · Zone 1',
    reportYear: '2025',
    reportPage: '28'
  };

  const paramKey = (param || 'do').toLowerCase();
  const isDo = paramKey === 'do' || paramKey === 'oxygen';
  const isBod = paramKey === 'bod';

  const paramTitle = isDo
    ? 'Dissolved Oxygen (DO)'
    : isBod
    ? 'Biochemical Oxygen Demand (BOD)'
    : 'Acidity (pH)';

  const limitText = isDo
    ? 'CPCB Class B limit: ≥ 5.0 mg/L'
    : isBod
    ? 'CPCB Class B limit: ≤ 3.0 mg/L'
    : 'CPCB Class B limit: 6.5 – 8.5';

  const readings = [
    {
      date: '2025-10-05',
      festival: 'Durga Visarjan',
      phase: 'Post-Visarjan',
      val: isDo ? '0.2 mg/L' : isBod ? '9.1 mg/L' : '7.5',
      cleaned: isDo ? '0.2' : isBod ? '9.1' : '7.5',
      state: '● Measured',
      status: isDo ? 'Critical Deficit' : isBod ? 'Severe Excess' : 'Conforming',
      year: '2025',
      page: '31'
    },
    {
      date: '2025-09-29',
      festival: 'Durga Visarjan',
      phase: 'Peak Immersion',
      val: isDo ? '0.0 mg/L' : isBod ? '9.4 mg/L' : '7.4',
      cleaned: isDo ? '0.0' : isBod ? '9.4' : '7.4',
      state: '● Measured',
      status: isDo ? 'Severe Anoxia' : isBod ? 'Severe Excess' : 'Conforming',
      year: '2025',
      page: '28'
    },
    {
      date: '2025-09-20',
      festival: 'Ganesh Visarjan',
      phase: 'Post-Visarjan',
      val: isDo ? '1.4 mg/L' : isBod ? '8.2 mg/L' : '7.8',
      cleaned: isDo ? '1.4' : isBod ? '8.2' : '7.8',
      state: '● Measured',
      status: isDo ? 'Deficit' : isBod ? 'Excess' : 'Conforming',
      year: '2025',
      page: '22'
    },
    {
      date: '2024-10-14',
      festival: 'Durga Visarjan',
      phase: 'Peak Immersion',
      val: isDo ? '0.4 mg/L' : isBod ? '8.8 mg/L' : '7.6',
      cleaned: isDo ? '0.4' : isBod ? '8.8' : '7.6',
      state: '● Measured',
      status: isDo ? 'Deficit' : isBod ? 'Excess' : 'Conforming',
      year: '2024',
      page: '24'
    },
    {
      date: '2024-09-18',
      festival: 'Ganesh Visarjan',
      phase: 'Before Immersion',
      val: isDo ? '4.8 mg/L' : isBod ? '3.5 mg/L' : '7.5',
      cleaned: isDo ? '4.8' : isBod ? '3.5' : '7.5',
      state: '● Measured',
      status: 'Marginal',
      year: '2024',
      page: '18'
    },
    {
      date: '2023-10-25',
      festival: 'Durga Visarjan',
      phase: 'Peak Immersion',
      val: isDo ? '0.0 mg/L' : isBod ? '9.4 mg/L' : '7.4',
      cleaned: isDo ? '0.0' : isBod ? '9.4' : '7.4',
      state: '● Measured',
      status: isDo ? 'Severe Anoxia' : isBod ? 'Severe Excess' : 'Conforming',
      year: '2023',
      page: '19'
    },
    {
      date: '2023-09-28',
      festival: 'Ganesh Visarjan',
      phase: 'Before Immersion',
      val: isDo ? '5.4 mg/L' : isBod ? '2.8 mg/L' : '7.6',
      cleaned: isDo ? '5.4' : isBod ? '2.8' : '7.6',
      state: '● Measured',
      status: 'Conforming',
      year: '2023',
      page: '12'
    }
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Top Context Subheader */}
      <div className="w-full bg-white rounded-xl p-5 shadow-xs border border-[#c3c6ce]/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link
              to={`/ghat/${currentGhat.id}`}
              className="text-xs text-[#9e4300] hover:underline flex items-center gap-1 font-semibold"
            >
              <span className="material-symbols-outlined text-[15px]">arrow_back</span>
              <span>Back to {currentGhat.name}</span>
            </Link>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#001b3d]">
            {paramTitle} Telemetry · {lang === 'hi' && currentGhat.nameHi ? currentGhat.nameHi : currentGhat.name}
          </h1>
          <p className="text-xs sm:text-sm text-[#43474d] mt-1 font-mono">
            STATION ID: {currentGhat.stationId || 'BMC-WQ-BG-01'} | {limitText}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Parameter switch tabs */}
          {['do', 'bod', 'ph'].map((pKey) => (
            <Link
              key={pKey}
              to={`/ghat/${currentGhat.id}/${pKey}`}
              className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                paramKey === pKey
                  ? 'bg-[#001428] text-white'
                  : 'bg-[#f0f3ff] text-[#001428] hover:bg-[#dfe8ff] border border-[#c3c6ce]'
              }`}
            >
              {pKey.toUpperCase()}
            </Link>
          ))}
        </div>
      </div>

      {/* Signature Hero Telemetry Timeline Chart (Rule 4: ONLY on Parameter page) */}
      <section className="bg-white rounded-xl p-5 md:p-6 shadow-xs border border-[#c3c6ce]/60">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4 pb-3 border-b border-[#dfe8ff]">
          <div>
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#9e4300] text-[22px]">show_chart</span>
              <h2 className="text-xl font-bold text-[#001b3d]">
                Multi-Year {paramTitle} Temporal Progression
              </h2>
            </div>
            <p className="text-xs text-[#74777e]">
              Statutory 2023–2025 cycle testing data with official CPCB Class B compliance threshold
            </p>
          </div>

          <div className="flex items-center gap-3 font-mono text-xs text-[#43474d]">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 bg-[#ba1a1a] rounded-full"></span> Measured Titration
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-0 border-t-2 border-dashed border-[#9e4300]"></span> CPCB Class B Limit
            </span>
          </div>
        </div>

        {/* SVG High-Precision Timeline with Dashed CPCB Limit Line (Rule 5) */}
        <div className="w-full aspect-[21/9] max-h-[340px] my-4 bg-[#f9f9ff] p-4 rounded-lg border border-[#e2e8f0]">
          <svg className="w-full h-full" viewBox="0 0 800 280">
            {/* Grid Lines */}
            <line x1="60" y1="40" x2="760" y2="40" stroke="#e2e8f0" strokeWidth="1" />
            <line x1="60" y1="90" x2="760" y2="90" stroke="#e2e8f0" strokeWidth="1" />
            <line x1="60" y1="140" x2="760" y2="140" stroke="#e2e8f0" strokeWidth="1" />
            <line x1="60" y1="190" x2="760" y2="190" stroke="#e2e8f0" strokeWidth="1" />
            <line x1="60" y1="240" x2="760" y2="240" stroke="#cbd5e1" strokeWidth="1.5" />

            {/* Y-Axis scale numbers */}
            <text x="45" y="44" fill="#74777e" fontSize="11" fontFamily="Space Mono" textAnchor="end">
              {isDo ? '10.0' : isBod ? '12.0' : '9.0'}
            </text>
            <text x="45" y="94" fill="#74777e" fontSize="11" fontFamily="Space Mono" textAnchor="end">
              {isDo ? '7.5' : isBod ? '9.0' : '8.0'}
            </text>
            <text x="45" y="144" fill="#74777e" fontSize="11" fontFamily="Space Mono" textAnchor="end">
              {isDo ? '5.0' : isBod ? '6.0' : '7.0'}
            </text>
            <text x="45" y="194" fill="#74777e" fontSize="11" fontFamily="Space Mono" textAnchor="end">
              {isDo ? '2.5' : isBod ? '3.0' : '6.0'}
            </text>
            <text x="45" y="244" fill="#74777e" fontSize="11" fontFamily="Space Mono" textAnchor="end">
              0.0
            </text>

            {/* CPCB Class B Dashed Threshold Line (Rule 5) */}
            <line
              x1="60"
              y1={isDo ? 140 : isBod ? 190 : 80}
              x2="760"
              y2={isDo ? 140 : isBod ? 190 : 80}
              stroke="#9e4300"
              strokeWidth="2.5"
              strokeDasharray="6 4"
            />
            <text
              x="765"
              y={isDo ? 144 : isBod ? 194 : 84}
              fill="#9e4300"
              fontSize="11"
              fontFamily="Space Mono"
              fontWeight="bold"
            >
              {limitText}
            </text>

            {/* Multi-Year Progression Line */}
            {isDo ? (
              <>
                <polyline
                  fill="none"
                  stroke="#ba1a1a"
                  strokeWidth="3.5"
                  points="100,130 200,240 310,145 420,230 530,195 640,240 720,235"
                />
                {/* Data Points */}
                {[
                  { cx: 100, cy: 130, date: '2023 Ganesh Pre', val: '5.4' },
                  { cx: 200, cy: 240, date: '2023 Durga Immersion', val: '0.0' },
                  { cx: 310, cy: 145, date: '2024 Ganesh Pre', val: '4.8' },
                  { cx: 420, cy: 230, date: '2024 Durga Immersion', val: '0.4' },
                  { cx: 530, cy: 195, date: '2025 Ganesh Post', val: '1.4' },
                  { cx: 640, cy: 240, date: '2025 Durga Immersion', val: '0.0' },
                  { cx: 720, cy: 235, date: '2025 Durga Post', val: '0.2' }
                ].map((pt) => (
                  <g
                    key={pt.cx}
                    className="cursor-pointer"
                    onClick={() =>
                      openProof({
                        reportYear: '2025',
                        reportPage: '28',
                        param: 'Dissolved Oxygen Timeline Point',
                        station: currentGhat.name,
                        standard: 'CPCB Class B limit: ≥ 5.0 mg/L',
                        dataState: '● Measured In-situ Titration',
                        cleanedValue: `${pt.val} mg/L`,
                        rawValue: `${pt.val} mg/L DO on ${pt.date}`,
                        unit: 'mg/L'
                      })
                    }
                  >
                    <circle cx={pt.cx} cy={pt.cy} r="6" fill="#ba1a1a" stroke="#ffffff" strokeWidth="2" />
                    <text
                      x={pt.cx}
                      y={pt.cy - 10}
                      textAnchor="middle"
                      fill="#001428"
                      fontSize="11"
                      fontFamily="Space Mono"
                      fontWeight="bold"
                    >
                      {pt.val}
                    </text>
                    <text
                      x={pt.cx}
                      y={260}
                      textAnchor="middle"
                      fill="#43474d"
                      fontSize="10"
                      fontFamily="Space Mono"
                    >
                      {pt.date.split(' ')[0]}
                    </text>
                  </g>
                ))}
              </>
            ) : (
              <>
                <polyline
                  fill="none"
                  stroke="#9e4300"
                  strokeWidth="3.5"
                  points="100,195 200,80 310,180 420,95 530,105 640,80 720,88"
                />
                {[
                  { cx: 100, cy: 195, val: '2.8' },
                  { cx: 200, cy: 80, val: '9.4' },
                  { cx: 310, cy: 180, val: '3.5' },
                  { cx: 420, cy: 95, val: '8.8' },
                  { cx: 530, cy: 105, val: '8.2' },
                  { cx: 640, cy: 80, val: '9.4' },
                  { cx: 720, cy: 88, val: '9.1' }
                ].map((pt) => (
                  <g key={pt.cx} className="cursor-pointer">
                    <circle cx={pt.cx} cy={pt.cy} r="6" fill="#9e4300" stroke="#ffffff" strokeWidth="2" />
                    <text
                      x={pt.cx}
                      y={pt.cy - 10}
                      textAnchor="middle"
                      fill="#001428"
                      fontSize="11"
                      fontFamily="Space Mono"
                      fontWeight="bold"
                    >
                      {pt.val}
                    </text>
                  </g>
                ))}
              </>
            )}
          </svg>
        </div>
      </section>

      {/* Statutory Readings Table (Rule 4: ONLY on Parameter page) */}
      <section className="bg-white rounded-xl p-5 shadow-xs border border-[#c3c6ce]/60">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-[#001b3d]">Statutory Inspection Log & Titration Ledger</h2>
            <p className="text-xs text-[#74777e]">
              Official gazette test results with raw laboratory records and proof verification
            </p>
          </div>
          <span className="font-mono text-xs bg-[#f0f3ff] px-3 py-1 rounded text-[#001b3d] font-bold">
            {readings.length} ARCHIVE RECORDS
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#001428] text-white uppercase font-mono text-[11px]">
                <th className="p-3">Sampling Date</th>
                <th className="p-3">Festival Cycle</th>
                <th className="p-3">Surveillance Phase</th>
                <th className="p-3">Measured Reading</th>
                <th className="p-3">Statutory Status</th>
                <th className="p-3">Data State</th>
                <th className="p-3">Gazette Reference</th>
                <th className="p-3 text-right">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e2e8f0]">
              {readings.map((r, i) => (
                <tr
                  key={i}
                  className="hover:bg-[#f0f3ff] transition-colors cursor-pointer group"
                  onClick={() =>
                    openProof({
                      reportYear: r.year,
                      reportPage: r.page,
                      param: paramTitle,
                      station: currentGhat.name,
                      standard: limitText,
                      dataState: r.state,
                      cleanedValue: r.cleaned,
                      rawValue: r.val,
                      unit: isDo || isBod ? 'mg/L' : ''
                    })
                  }
                >
                  <td className="p-3 font-mono font-semibold text-[#001b3d]">{r.date}</td>
                  <td className="p-3 font-medium text-[#43474d]">{r.festival}</td>
                  <td className="p-3 text-[#43474d]">{r.phase}</td>
                  <td className="p-3 font-mono font-bold text-[#ba1a1a] text-sm">
                    {r.val}
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        r.status.includes('Deficit') || r.status.includes('Anoxia') || r.status.includes('Excess')
                          ? 'bg-[#ffdad6] text-[#ba1a1a]'
                          : 'bg-[#ffdbcb] text-[#9e4300]'
                      }`}
                    >
                      {r.status}
                    </span>
                  </td>
                  <td className="p-3 font-mono text-[#001b3d]">{r.state}</td>
                  <td className="p-3 font-mono text-[#74777e]">
                    Report {r.year} · p.{r.page}
                  </td>
                  <td className="p-3 text-right">
                    <span className="inline-flex items-center gap-1 text-[#9e4300] font-semibold group-hover:underline">
                      <span>View proof</span>
                      <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
