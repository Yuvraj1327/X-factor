import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useApp } from '../context/AppContext.jsx';
import { GHAT_COORDINATES, getPdfUrl } from '../api/client.js';

// Custom Map Reset Helper
function MapResetController({ center, zoom }) {
  const map = useMap();
  React.useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

// Custom Leaflet DivIcon for pins
function createMapPinIcon(pinNum, tier, nameHi, lowestDo, subtext) {
  const bg = tier === 'HIGH' ? '#ba1a1a' : tier === 'MEDIUM' ? '#d97706' : '#64748b';

  return L.divIcon({
    className: 'custom-ghat-pin',
    html: `
      <div style="position: relative; display: flex; align-items: center; cursor: pointer;">
        <!-- Circular pin bubble -->
        <div style="
          width: 28px;
          height: 28px;
          border-radius: 9999px;
          background-color: ${bg};
          color: white;
          border: 2px solid white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Space Mono', monospace;
          font-weight: bold;
          font-size: 12px;
          z-index: 10;
        ">
          ${pinNum}
        </div>

        <!-- Attached label callout chip -->
        <div style="
          margin-left: 6px;
          background: #ffffff;
          color: #0f172a;
          border: 1px solid #cbd5e1;
          border-radius: 4px;
          padding: 2px 6px;
          font-size: 11px;
          line-height: 1.2;
          box-shadow: 0 1px 4px rgba(0,0,0,0.15);
          white-space: nowrap;
          pointer-events: none;
        ">
          <div style="font-weight: 700; color: #0f2942;">#${pinNum} ${nameHi || ''}</div>
          <div style="font-family: 'Space Mono', monospace; font-size: 10px; color: ${bg}; font-weight: 600;">
            O₂: ${lowestDo !== undefined ? lowestDo + ' mg/l' : 'N/A'} · ${subtext || tier}
          </div>
        </div>
      </div>
    `,
    iconSize: [160, 32],
    iconAnchor: [14, 16]
  });
}

export default function MapPage() {
  const { rankingData, openProof } = useApp();
  const [riskFilter, setRiskFilter] = useState('ALL'); // 'ALL' | 'HIGH' | 'MEDIUM' | 'WATCH'
  const [selectedRank, setSelectedRank] = useState(1);
  const [mapCenter, setMapCenter] = useState([23.2550, 77.3850]);
  const [mapZoom, setMapZoom] = useState(13);

  const apiGhats = rankingData?.ghats || [];

  const mapGhats = apiGhats.map((g) => {
    const geo = GHAT_COORDINATES[g.site] || {
      id: String(g.rank),
      rank: g.rank,
      lat: 23.2550,
      lng: 77.3850,
      nameHi: g.site,
      ward: 'भोपाल',
      basin: g.water_body
    };
    return {
      ...g,
      ...geo
    };
  });

  const selectedGhat = mapGhats.find((g) => g.rank === selectedRank) || mapGhats[0] || null;

  const filteredGhats = mapGhats.filter((g) => {
    if (riskFilter === 'ALL') return true;
    return g.tier === riskFilter;
  });

  const resetView = () => {
    setMapCenter([23.2550, 77.3850]);
    setMapZoom(13);
  };

  return (
    <div className="flex flex-col gap-4 text-left">
      {/* 1. NGT STATUTORY BAN ADVISORY CARD */}
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
              Direct immersion in Bhojtal (Upper Lake Ramsar Site) and Lower Lake strictly penalised. BMC designated artificial immersion ponds (विसर्जन कुंड) with zero-spill bunds are mandatory.
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
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-[#f8fafc] text-[#0f2942] border border-[#cbd5e1] rounded text-xs font-bold transition-colors cursor-pointer shadow-xs"
          >
            <span className="material-symbols-outlined text-[16px]">visibility</span>
            <span>राजपत्रित आदेश / Gazetted Order (PDF)</span>
          </a>
        </div>
      </div>

      {/* 2. RISK FILTER BAR */}
      <div className="w-full flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-lg border border-[#e2e8f0] shadow-2xs">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="font-bold text-[#0f2942] mr-1">जोखिम फ़िल्टर / Risk Tier:</span>
          {['ALL', 'HIGH', 'MEDIUM', 'WATCH'].map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setRiskFilter(t)}
              className={`px-3 py-1.5 rounded text-xs font-bold transition-colors cursor-pointer ${
                riskFilter === t
                  ? 'bg-[#0f2942] text-white'
                  : 'bg-[#f1f5f9] text-[#334155] hover:bg-[#e2e8f0]'
              }`}
            >
              {t === 'ALL' ? 'सभी 7 स्थल' : `${t} (${mapGhats.filter((g) => g.tier === t).length})`}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs text-[#64748b] font-mono">
          <span>7 विहित निगरानी स्थल · OpenStreetMap Bhopal</span>
        </div>
      </div>

      {/* 3. MAIN GEOSPATIAL VIEWPORT (Grid: Left Map + Right Inspector Card) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* LEAFLET OPEN MAP OF BHOPAL (8 Cols) */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-[#cbd5e1] shadow-sm overflow-hidden relative h-[620px] flex flex-col">
          {/* In-Map Top Header Banner Overlay */}
          <div className="absolute top-3 left-3 right-3 z-400 bg-white/95 backdrop-blur-xs px-3.5 py-2 rounded-lg border border-[#cbd5e1] shadow-xs flex items-center justify-between text-xs pointer-events-auto">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#d97706] text-[18px]">nature</span>
              <span className="font-bold text-[#0f2942]">भोपाल जल-संसाधन एवं विसर्जन कुंड GIS मानचित्र</span>
              <span className="text-[#94a3b8]">·</span>
              <span className="font-mono text-[11px] text-[#64748b]">WGS84 Leaflet Layer</span>
            </div>
            <div className="flex items-center gap-1.5 font-mono text-[11px] text-[#0f2942]">
              <span className="w-2 h-2 rounded-full bg-[#ba1a1a]"></span>
              <span>CPCB Class B Baseline: <strong>5.0 mg/l O₂</strong></span>
            </div>
          </div>

          {/* Map Reset Controls top right */}
          <div className="absolute top-16 right-3 z-400 flex flex-col gap-1">
            <button
              type="button"
              onClick={resetView}
              title="Reset Map to Bhojtal Extents"
              className="w-8 h-8 rounded bg-white text-[#0f2942] border border-[#cbd5e1] hover:bg-[#f8fafc] flex items-center justify-center font-bold text-sm shadow-xs cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">refresh</span>
            </button>
          </div>

          {/* Map Scale Bar bottom left */}
          <div className="absolute bottom-3 left-3 z-400 bg-white/90 backdrop-blur-xs px-2.5 py-1 rounded border border-[#cbd5e1] text-[11px] font-mono text-[#0f2942] flex items-center gap-2 shadow-xs">
            <div className="w-12 h-1.5 bg-[#0f2942] rounded-xs"></div>
            <span>2.5 किमी</span>
            <span className="text-[#94a3b8]">|</span>
            <span>Bhopal Upper & Lower Lake Basins</span>
          </div>

          {/* Map Legend bottom right */}
          <div className="absolute bottom-3 right-3 z-400 bg-white/95 backdrop-blur-xs p-3 rounded-lg border border-[#cbd5e1] text-[11px] shadow-sm max-w-[280px]">
            <div className="font-bold uppercase font-mono text-[#0f2942] mb-1.5 tracking-wider text-[10px]">
              संकेत सूची / MAP LEGEND
            </div>
            <div className="space-y-1 font-sans text-[#334155]">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ba1a1a] shrink-0"></span>
                <span>HIGH Tier (उच्च प्राथमिकता) [#1, #2]</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#d97706] shrink-0"></span>
                <span>MEDIUM Tier (मध्यम प्राथमिकता) [#3, #4, #5]</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#64748b] shrink-0"></span>
                <span>WATCH Tier (निगरानी स्तर) [#6, #7]</span>
              </div>
            </div>
          </div>

          {/* REAL LEAFLET MAP OF BHOPAL */}
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            scrollWheelZoom={true}
            style={{ width: '100%', height: '100%', zIndex: 1 }}
          >
            <MapResetController center={mapCenter} zoom={mapZoom} />

            {/* Real OpenStreetMap Tiles of Bhopal (100% Free, Open, No API Key Required) */}
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />

            {/* Map Markers for all 7 Ghats */}
            {filteredGhats.map((ghat) => (
              <Marker
                key={ghat.rank}
                position={[ghat.lat, ghat.lng]}
                icon={createMapPinIcon(
                  ghat.rank,
                  ghat.tier,
                  ghat.nameHi,
                  ghat.derived?.oxygen_lowest,
                  ghat.tier
                )}
                eventHandlers={{
                  click: () => {
                    setSelectedRank(ghat.rank);
                    setMapCenter([ghat.lat, ghat.lng]);
                  }
                }}
              >
                <Popup>
                  <div className="font-sans text-xs p-1">
                    <div className="font-bold text-[#0f2942] text-sm">
                      #{ghat.rank} {ghat.site}
                    </div>
                    <div className="text-[#64748b] text-[11px] mb-1">{ghat.water_body}</div>
                    <div className="font-mono text-[#ba1a1a] font-bold">
                      न्यूनतम DO: {ghat.derived?.oxygen_lowest ?? 'N/A'} mg/l
                    </div>
                    {ghat.tier_note && (
                      <div className="text-[10px] text-[#b45309] mt-1">{ghat.tier_note}</div>
                    )}
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* RIGHT INSPECTOR PANEL (4 Cols) */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-[#cbd5e1] p-5 shadow-sm flex flex-col justify-between">
          {selectedGhat ? (
            <div className="flex flex-col gap-4">
              {/* Header */}
              <div className="flex items-center justify-between pb-2 border-b border-[#f1f5f9]">
                <div className="flex items-center gap-1.5 text-xs font-bold">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      selectedGhat.tier === 'HIGH'
                        ? 'bg-[#ba1a1a]'
                        : selectedGhat.tier === 'MEDIUM'
                        ? 'bg-[#d97706]'
                        : 'bg-[#64748b]'
                    }`}
                  ></span>
                  <span className="font-mono text-[#0f2942]">
                    RANK #{selectedGhat.rank} · {selectedGhat.tier} TIER
                  </span>
                </div>
                {selectedGhat.untested_latest_durga && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#475569] text-white">
                    NOT TESTED Durga 2025
                  </span>
                )}
              </div>

              <div>
                <h3 className="text-xl font-extrabold text-[#0f2942]">
                  {selectedGhat.site}
                </h3>
                {selectedGhat.nameHi && (
                  <div className="text-sm text-[#64748b] font-medium">
                    {selectedGhat.nameHi}
                  </div>
                )}
                <div className="text-xs text-[#475569] font-mono mt-1">
                  {selectedGhat.water_body}
                </div>
              </div>

              {/* Tier Note Warning */}
              {selectedGhat.tier_note && (
                <div className="p-2.5 rounded bg-[#fffbeb] border border-[#fef3c7] text-xs text-[#92400e]">
                  ⚠️ {selectedGhat.tier_note}
                </div>
              )}

              {/* Dissolved Oxygen Gauge */}
              <div className="bg-[#f8fafc] p-3.5 rounded-lg border border-[#e2e8f0]">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-[#64748b] font-medium">न्यूनतम घुलित ऑक्सीजन:</span>
                  <span className="font-mono font-bold text-sm text-[#ba1a1a]">
                    {selectedGhat.derived?.oxygen_lowest ?? 'N/A'} mg/l
                  </span>
                </div>
                {/* Horizontal Bar */}
                <div className="w-full bg-[#e2e8f0] h-2.5 rounded-full overflow-hidden relative">
                  <div
                    className="h-full bg-[#ba1a1a]"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, ((selectedGhat.derived?.oxygen_lowest || 0) / 10) * 100)
                      )}%`
                    }}
                  ></div>
                </div>
                <div className="flex items-center justify-between text-[10px] font-mono text-[#64748b] mt-1">
                  <span>0.0 (शून्य)</span>
                  <span className="text-[#0f2942] font-bold">CPCB मानक: 5.0 mg/l</span>
                  <span>10.0 mg/l</span>
                </div>
              </div>

              {/* First Reason */}
              {selectedGhat.reasons && selectedGhat.reasons[0] && (
                <div className="text-xs text-[#334155] bg-white p-3 rounded-lg border border-[#e2e8f0]">
                  <div className="font-bold text-[#0f2942] mb-1">
                    {selectedGhat.reasons[0].text}
                  </div>
                  {selectedGhat.reasons[0].evidence && selectedGhat.reasons[0].evidence[0]?.pdf && (
                    <a
                      href={getPdfUrl(selectedGhat.reasons[0].evidence[0].pdf)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] font-mono text-[#0284c7] font-bold hover:underline mt-1"
                    >
                      <span>रिपोर्ट पृष्ठ {selectedGhat.reasons[0].evidence[0].page} [PDF]</span>
                      <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                    </a>
                  )}
                </div>
              )}

              {/* Action checklist items preview */}
              {selectedGhat.actions && (
                <div>
                  <div className="text-xs font-bold text-[#0f2942] uppercase tracking-wider mb-2">
                    विहित कार्य ({selectedGhat.actions.length})
                  </div>
                  <ul className="space-y-1.5 text-xs text-[#334155]">
                    {selectedGhat.actions.slice(0, 3).map((act, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-[#0284c7] font-bold">•</span>
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Bottom Navigation */}
              <div className="pt-2 flex flex-col gap-2">
                <Link
                  to={`/ghat/${selectedGhat.rank}`}
                  className="w-full py-2 bg-[#0f2942] hover:bg-[#1e40af] text-white rounded text-xs font-bold text-center transition-colors shadow-xs"
                >
                  सम्पूर्ण वैज्ञानिक विवरण एवं साक्ष्य देखें →
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-center text-xs text-slate-400">लोड हो रहा है...</div>
          )}
        </div>
      </div>
    </div>
  );
}
