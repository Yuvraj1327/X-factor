import React, { useState } from 'react';
import { useApp } from '../context/AppContext.jsx';

export default function WorkOrders() {
  const { openProof } = useApp();
  const [filterType, setFilterType] = useState('all'); // 'all' | 'aeration' | 'desilt' | 'sluice'
  const [search, setSearch] = useState('');
  const [selectedOrder, setSelectedOrder] = useState('WO-801');

  const [orders, setOrders] = useState([
    {
      id: 'WO-801',
      ward: 'Ward-04',
      type: 'Aeration',
      typeBadge: 'Aeration',
      severity: 'CRITICAL',
      title: 'Bairagarh Ghat — Micro-Bubble Aeration Cascades',
      desc: 'Deploy 4× venturi diffuser cascades at immersion channel to restore dissolved oxygen before next cycle.',
      metricLabel: 'DO Breach: 0.0 mg/L',
      metricSub: 'Critical Low',
      threshold: 'CPCB Threshold: ≥ 5.0 mg/L',
      statusTag: '100% Depleted',
      statusCol: 'draft',
      supervisor: 'Er. Rajesh Tiwari',
      location: 'Upper Lake',
      record: 'Field Ledger #04, p.28',
      queue: 'P-1 QUEUE',
      phone: '+91 98260 XXXXX'
    },
    {
      id: 'WO-802',
      ward: 'Ward-22',
      type: 'Dredge',
      typeBadge: 'Dredge',
      severity: 'URGENT',
      title: 'Khatlapura Ghat — Organic Sludge Dredging & Silt Screen',
      desc: 'Suck and excavate bottom sludge containing synthetic lacquer residues and heavy organic decomposition sediment.',
      metricLabel: 'BOD: 14.8 mg/L',
      metricSub: '4.9x Limit',
      threshold: 'CPCB Permitted: ≤ 3.0 mg/L',
      statusTag: 'Exceedance',
      statusCol: 'draft',
      supervisor: 'BMC Sanitation Unit 3',
      location: 'Lower Lake',
      record: 'Ledger #02, p.14',
      queue: 'P-2 QUEUE',
      phone: '+91 98261 XXXXX'
    },
    {
      id: 'WO-804',
      ward: 'Ward-18',
      type: 'Excavator',
      typeBadge: 'Excavator',
      severity: 'In Progress - 65%',
      title: 'Prempura Ghat — Silt Trap Clearance & Floating Booms',
      desc: 'Mechanical amphibian excavator team deployed to scoop out debris along the Upper Lake direct intake zone.',
      metricLabel: 'Turbidity: 118 NTU',
      metricSub: 'High Silt',
      threshold: 'Permissible: < 10 NTU',
      statusTag: 'Target: 24h',
      statusCol: 'sent',
      supervisor: 'Er. Amit Sharma',
      location: 'Bhadbhada Spillway',
      record: 'Dispatched: 18 Oct, 09:30 AM',
      queue: 'WhatsApp Active',
      phone: '+91 98262 XXXXX'
    },
    {
      id: 'WO-805',
      ward: 'Ward-31',
      type: 'Bio-Enzyme',
      typeBadge: 'Bio-Enzyme',
      severity: 'En Route / Active',
      title: 'Rani Kamlapati Kund — Bio-Enzyme Inoculation & Demarcation',
      desc: 'Install physical geotextile boom cordon and deploy solar-powered micro-aerators to digest festive organic load.',
      metricLabel: 'Fecal Coliform: 820 MPN',
      metricSub: 'Elevated',
      threshold: 'Standard: < 500 MPN',
      statusTag: 'Cordon Active',
      statusCol: 'sent',
      supervisor: 'Civic Zone 02 Team',
      location: 'Chhota Talaab',
      record: 'Dispatched: 18 Oct, 11:15 AM',
      queue: 'WhatsApp Active',
      phone: '+91 98263 XXXXX'
    },
    {
      id: 'WO-806',
      ward: 'Ward-45',
      type: 'Trash Boom',
      typeBadge: 'Trash Boom',
      severity: 'Work Completed',
      title: 'Hathaikheda Dam — Floating Trash Screen Deployment',
      desc: 'Dual wire-mesh intake boom fixed. Over 1.4 MT flower waste & fabric debris collected and safely carted away.',
      metricLabel: '1.4 MT Waste Recovered',
      metricSub: 'Exec: 4.2 hrs',
      threshold: 'Collector: Zone 18 Sanitation',
      statusTag: '100% Cleared',
      statusCol: 'done',
      supervisor: 'Signed by Ward Officer',
      location: 'Hathaikheda',
      record: 'Evidence: Geo-tagged photo logged',
      queue: 'Pending Lab Clearance',
      phone: '+91 98264 XXXXX'
    },
    {
      id: 'WO-807',
      ward: 'Ward-52',
      type: 'Sluice Gate',
      typeBadge: 'Sluice Gate',
      severity: 'Work Completed',
      title: 'Shahpura Lake — Sluice Gate Desiltation & Bamboo Snag Removal',
      desc: 'Sluice regulator gates 1 and 2 cleared of snagged bamboo framework to restore natural retention flow.',
      metricLabel: 'Sluice Flow Restored',
      metricSub: 'Exec: 6.8 hrs',
      threshold: 'Discharge: Normal velocity',
      statusTag: '100% Cleared',
      statusCol: 'done',
      supervisor: 'Clearance Verified',
      location: 'Shahpura Lake',
      record: 'Evidence: Sluice clearance verified',
      queue: 'Pending Lab Clearance',
      phone: '+91 98265 XXXXX'
    }
  ]);

  const moveOrderStatus = (orderId, targetCol) => {
    setOrders((prev) =>
      prev.map((o) => (o.id === orderId ? { ...o, statusCol: targetCol } : o))
    );
  };

  const filteredOrders = orders.filter((o) => {
    if (filterType === 'aeration' && o.type !== 'Aeration') return false;
    if (filterType === 'desilt' && o.type !== 'Dredge' && o.type !== 'Excavator' && o.type !== 'Sluice Gate') return false;
    if (filterType === 'sluice' && o.type !== 'Trash Boom' && o.type !== 'Bio-Enzyme') return false;
    if (search.trim() !== '') {
      const q = search.toLowerCase();
      return o.title.toLowerCase().includes(q) || o.location.toLowerCase().includes(q) || o.id.toLowerCase().includes(q);
    }
    return true;
  });

  const activeOrder = orders.find((o) => o.id === selectedOrder) || orders[0];

  return (
    <div className="flex flex-col gap-4 text-left">
      {/* 1. TOP TITLE BANNER (Matching Screenshot 1) */}
      <div className="w-full bg-white rounded-xl p-4 sm:p-5 border border-[#e2e8f0] shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5 text-xs">
            <span className="font-bold px-2 py-0.5 rounded bg-[#f1f5f9] text-[#0f2942] border border-[#cbd5e1]">
              BMC WARD CELL • म.प्र. प्रदूषण नियंत्रण बोर्ड
            </span>
            <span className="text-[#64748b]">
              CPCB Class B Standard Grid Protocol • 24h Post-Visarjan Mandate
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-[#0f2942]">
            कार्य आदेश एवं जल सुधार पाइपलाइन <span className="font-normal text-[#64748b] text-lg sm:text-xl">/ Remediation Pipeline</span>
          </h1>
          <p className="text-xs text-[#64748b] mt-0.5">
            Post-visarjan water quality emergency work orders. Status reflects mechanical &amp; operational completion only; ecological safety remains subject to formal MPPCB laboratory certification.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => alert('Synchronizing breach telemetry with MPPCB Central Grid...')}
            className="flex items-center gap-1.5 px-3 py-2 bg-[#f8fafc] hover:bg-[#e2e8f0] text-[#0f2942] rounded-lg border border-[#cbd5e1] text-xs font-bold transition-colors cursor-pointer shadow-2xs"
          >
            <span className="material-symbols-outlined text-[16px]">sync</span>
            <span>Re-sync Breaches (पुनः सिंकनाइज़)</span>
          </button>
          <button
            type="button"
            onClick={() => alert('Opening new work order dispatch wizard...')}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-[#9a3412] hover:bg-[#c2410c] text-white rounded-lg text-xs font-bold transition-colors cursor-pointer shadow-xs"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            <span>+ Create Order (नया आदेश)</span>
          </button>
        </div>
      </div>

      {/* 2. PIPELINE EXECUTION PROGRESS BAR (Matching Screenshot 1) */}
      <div className="w-full bg-[#f8fafc] rounded-lg p-2.5 px-4 border border-[#e2e8f0] flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-bold text-[#0f2942]">समग्र प्रगति / Pipeline Execution:</span>
          <span className="px-2 py-0.5 rounded bg-[#ffedd5] text-[#9a3412] font-mono font-bold">
            2 of 6 Orders Executed (33%)
          </span>
          <span className="text-[#94a3b8]">|</span>
          <span className="text-[#64748b]">Target Turnaround: &lt; 24h</span>
        </div>

        <div className="flex items-center gap-4 font-mono text-[11px] text-[#475569]">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#0f2942]"></span>
            <span>2 Done</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#d97706]"></span>
            <span>2 Sent &amp; In-Progress</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#64748b]"></span>
            <span>2 Drafts</span>
          </span>
        </div>
      </div>

      {/* 3. FILTER TABS & SEARCH BAR (Matching Screenshot 1) */}
      <div className="w-full flex flex-wrap items-center justify-between gap-3 bg-white p-2.5 rounded-lg border border-[#e2e8f0] text-xs">
        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {[
            { id: 'all', label: 'All Orders (6)' },
            { id: 'aeration', label: 'Aeration / वातन (2)' },
            { id: 'desilt', label: 'Desiltation & Cleaning (2)' },
            { id: 'sluice', label: 'Sluice & Barrier (2)' }
          ].map((cat) => (
            <button
              key={cat.id}
              type="button"
              onClick={() => setFilterType(cat.id)}
              className={`px-3 py-1.5 rounded text-xs font-bold transition-colors cursor-pointer ${
                filterType === cat.id
                  ? 'bg-[#0f2942] text-white shadow-2xs'
                  : 'bg-[#f1f5f9] text-[#334155] hover:bg-[#e2e8f0]'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Sort & Search */}
        <div className="flex flex-wrap items-center gap-2">
          <select className="bg-[#f8fafc] border border-[#cbd5e1] rounded px-2.5 py-1.5 text-xs font-semibold text-[#0f2942] focus:outline-none">
            <option>Sort: Severity (उच्च प्राथमिकता)</option>
            <option>Sort: Turnaround Time</option>
            <option>Sort: Ward Number</option>
          </select>

          <div className="relative">
            <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-[16px] text-[#94a3b8]">
              search
            </span>
            <input
              type="text"
              placeholder="Search by Ghat, Basin, or WO"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded border border-[#cbd5e1] bg-[#f8fafc] text-xs text-[#0f2942] focus:outline-none w-56"
            />
          </div>
        </div>
      </div>

      {/* 4. 3-COLUMN KANBAN BOARD + RIGHT WHATSAPP / PROOF PANELS (Matching Screenshot 1) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* KANBAN 3 COLUMNS (8 COLS) */}
        <div className="xl:col-span-8 grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* COLUMN 1: प्रारूप / Draft (2) */}
          <div className="bg-[#f8fafc] p-3 rounded-xl border border-[#e2e8f0] flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs font-bold pb-2 border-b border-[#e2e8f0]">
              <div className="flex items-center gap-1.5 text-[#0f2942]">
                <span className="w-2.5 h-2.5 rounded-full bg-[#64748b]"></span>
                <span>प्रारूप / Draft</span>
              </div>
              <span className="font-mono bg-white px-2 py-0.5 rounded border border-[#cbd5e1] text-[11px]">
                {filteredOrders.filter((o) => o.statusCol === 'draft').length}
              </span>
            </div>

            <div className="space-y-3">
              {filteredOrders
                .filter((o) => o.statusCol === 'draft')
                .map((o) => (
                  <div
                    key={o.id}
                    onClick={() => setSelectedOrder(o.id)}
                    className={`bg-white rounded-lg p-3.5 border shadow-2xs transition-all cursor-pointer ${
                      selectedOrder === o.id
                        ? 'border-[#0f2942] ring-1 ring-[#0f2942]'
                        : 'border-[#cbd5e1] hover:border-[#94a3b8]'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-2">
                      <div className="flex items-center gap-1 font-mono text-[11px]">
                        <span className="font-bold text-[#0f2942]">{o.id}</span>
                        <span className="px-1.5 py-0.2 rounded bg-[#f1f5f9] text-[#475569]">{o.ward}</span>
                        <span className="px-1.5 py-0.2 rounded bg-[#f1f5f9] text-[#475569]">{o.typeBadge}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#fee2e2] text-[#ba1a1a]">
                        ● {o.severity}
                      </span>
                    </div>

                    <h3 className="font-bold text-xs sm:text-[13px] text-[#0f2942] leading-snug mb-1">
                      {o.title}
                    </h3>
                    <p className="text-[11px] text-[#64748b] leading-tight line-clamp-2 mb-2.5">
                      {o.desc}
                    </p>

                    {/* Metric Box */}
                    <div className="bg-[#fef2f2] border border-[#fecaca] p-2 rounded text-[11px] font-mono mb-2.5">
                      <div className="flex items-center justify-between text-[#ba1a1a] font-bold">
                        <span>{o.metricLabel}</span>
                        <span>{o.metricSub}</span>
                      </div>
                      <div className="flex items-center justify-between text-[#64748b] text-[10px] mt-0.5">
                        <span>{o.threshold}</span>
                        <span className="font-bold text-[#ba1a1a]">{o.statusTag}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#64748b] pt-2 border-t border-[#f1f5f9] mb-2.5">
                      <span className="flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">person</span>
                        {o.supervisor}
                      </span>
                      <span>{o.location}</span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] font-mono text-[#64748b] mb-2.5">
                      <span>Record: <strong>{o.record}</strong></span>
                      <span className="font-bold text-[#ba1a1a]">{o.queue}</span>
                    </div>

                    <div className="flex items-center gap-1.5 pt-1">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          moveOrderStatus(o.id, 'sent');
                        }}
                        className="flex-1 py-1.5 bg-[#9a3412] hover:bg-[#c2410c] text-white rounded font-bold text-xs flex items-center justify-center gap-1 transition-colors cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[14px]">send</span>
                        <span>Dispatch Order</span>
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          alert(`Editing draft specifications for ${o.id}...`);
                        }}
                        className="px-2.5 py-1.5 bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] rounded font-bold text-xs"
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* COLUMN 2: प्रेषित / Sent & Active (2) */}
          <div className="bg-[#f8fafc] p-3 rounded-xl border border-[#e2e8f0] flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs font-bold pb-2 border-b border-[#e2e8f0]">
              <div className="flex items-center gap-1.5 text-[#0f2942]">
                <span className="w-2.5 h-2.5 rounded-full bg-[#d97706]"></span>
                <span>प्रेषित / Sent &amp; Active</span>
              </div>
              <span className="font-mono bg-white px-2 py-0.5 rounded border border-[#cbd5e1] text-[11px]">
                {filteredOrders.filter((o) => o.statusCol === 'sent').length}
              </span>
            </div>

            <div className="space-y-3">
              {filteredOrders
                .filter((o) => o.statusCol === 'sent')
                .map((o) => (
                  <div
                    key={o.id}
                    onClick={() => setSelectedOrder(o.id)}
                    className={`bg-white rounded-lg p-3.5 border shadow-2xs transition-all cursor-pointer ${
                      selectedOrder === o.id
                        ? 'border-[#0f2942] ring-1 ring-[#0f2942]'
                        : 'border-[#cbd5e1] hover:border-[#94a3b8]'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-2">
                      <div className="flex items-center gap-1 font-mono text-[11px]">
                        <span className="font-bold text-[#0f2942]">{o.id}</span>
                        <span className="px-1.5 py-0.2 rounded bg-[#f1f5f9] text-[#475569]">{o.ward}</span>
                        <span className="px-1.5 py-0.2 rounded bg-[#f1f5f9] text-[#475569]">{o.typeBadge}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#ffedd5] text-[#9a3412]">
                        {o.severity}
                      </span>
                    </div>

                    <h3 className="font-bold text-xs sm:text-[13px] text-[#0f2942] leading-snug mb-1">
                      {o.title}
                    </h3>
                    <p className="text-[11px] text-[#64748b] leading-tight line-clamp-2 mb-2.5">
                      {o.desc}
                    </p>

                    {/* Metric Box */}
                    <div className="bg-[#fff7ed] border border-[#fed7aa] p-2 rounded text-[11px] font-mono mb-2.5">
                      <div className="flex items-center justify-between text-[#c2410c] font-bold">
                        <span>{o.metricLabel}</span>
                        <span>{o.metricSub}</span>
                      </div>
                      <div className="flex items-center justify-between text-[#64748b] text-[10px] mt-0.5">
                        <span>{o.threshold}</span>
                        <span className="font-bold text-[#9a3412]">{o.statusTag}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#64748b] pt-2 border-t border-[#f1f5f9] mb-2.5">
                      <span>{o.supervisor}</span>
                      <span>{o.location}</span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] font-mono text-[#64748b] mb-2.5">
                      <span>{o.record}</span>
                      <span className="font-bold text-[#15803d] flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#15803d]"></span>
                        {o.queue}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 pt-1">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          moveOrderStatus(o.id, 'done');
                        }}
                        className="flex-1 py-1.5 bg-[#0f2942] hover:bg-[#1e2f42] text-white rounded font-bold text-xs flex items-center justify-center gap-1 transition-colors cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-[14px]">check_circle</span>
                        <span>Mark Executed</span>
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          alert(`Tracking GPS telemetry stream for ${o.id}...`);
                        }}
                        className="px-2.5 py-1.5 bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] rounded font-bold text-xs"
                      >
                        Live Status
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* COLUMN 3: कार्य पूर्ण / Done (2) */}
          <div className="bg-[#f8fafc] p-3 rounded-xl border border-[#e2e8f0] flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs font-bold pb-2 border-b border-[#e2e8f0]">
              <div className="flex items-center gap-1.5 text-[#0f2942]">
                <span className="w-2.5 h-2.5 rounded-full bg-[#0f2942]"></span>
                <span>कार्य पूर्ण / Done</span>
              </div>
              <span className="font-mono bg-white px-2 py-0.5 rounded border border-[#cbd5e1] text-[11px]">
                {filteredOrders.filter((o) => o.statusCol === 'done').length}
              </span>
            </div>

            <div className="space-y-3">
              {filteredOrders
                .filter((o) => o.statusCol === 'done')
                .map((o) => (
                  <div
                    key={o.id}
                    onClick={() => setSelectedOrder(o.id)}
                    className={`bg-white rounded-lg p-3.5 border shadow-2xs transition-all cursor-pointer ${
                      selectedOrder === o.id
                        ? 'border-[#0f2942] ring-1 ring-[#0f2942]'
                        : 'border-[#cbd5e1] hover:border-[#94a3b8]'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-2">
                      <div className="flex items-center gap-1 font-mono text-[11px]">
                        <span className="font-bold text-[#0f2942]">{o.id}</span>
                        <span className="px-1.5 py-0.2 rounded bg-[#f1f5f9] text-[#475569]">{o.ward}</span>
                        <span className="px-1.5 py-0.2 rounded bg-[#f1f5f9] text-[#475569]">{o.typeBadge}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#f1f5f9] text-[#0f2942] border border-[#cbd5e1]">
                        ✓ {o.severity}
                      </span>
                    </div>

                    <h3 className="font-bold text-xs sm:text-[13px] text-[#0f2942] leading-snug mb-1">
                      {o.title}
                    </h3>
                    <p className="text-[11px] text-[#64748b] leading-tight line-clamp-2 mb-2.5">
                      {o.desc}
                    </p>

                    {/* Metric Box */}
                    <div className="bg-[#f8fafc] border border-[#e2e8f0] p-2 rounded text-[11px] font-mono mb-2.5">
                      <div className="flex items-center justify-between text-[#0f2942] font-bold">
                        <span>{o.metricLabel}</span>
                        <span>{o.metricSub}</span>
                      </div>
                      <div className="flex items-center justify-between text-[#64748b] text-[10px] mt-0.5">
                        <span>{o.threshold}</span>
                        <span className="font-bold text-[#0f2942]">{o.statusTag}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#64748b] pt-2 border-t border-[#f1f5f9] mb-2">
                      <span>{o.supervisor}</span>
                      <span>{o.location}</span>
                    </div>

                    <div className="text-[10px] font-mono text-[#64748b] mb-2.5 flex items-center justify-between">
                      <span>{o.record}</span>
                      <span className="text-[#c2410c] font-bold">{o.queue}</span>
                    </div>

                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        alert(`Opening signed civil handover certificate for ${o.id}...`);
                      }}
                      className="w-full py-1.5 bg-white hover:bg-[#f1f5f9] text-[#0f2942] border border-[#cbd5e1] rounded font-bold text-xs flex items-center justify-center gap-1 transition-colors cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[14px]">verified</span>
                      <span>View Handover Certificate</span>
                    </button>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: WHATSAPP DISPATCH & STATUTORY PROOF DOSSIER (4 COLS - Matching Screenshot 1) */}
        <div className="xl:col-span-4 flex flex-col gap-4">
          {/* Panel 1: त्वरित प्रेषण संदेश / WhatsApp Remediation Dispatch */}
          <div className="bg-white rounded-xl border border-[#cbd5e1] shadow-2xs p-4">
            <div className="flex items-center justify-between pb-2 mb-2.5 border-b border-[#f1f5f9]">
              <div className="flex items-center gap-1.5 text-xs font-bold text-[#0f2942]">
                <span className="material-symbols-outlined text-[18px]">chat</span>
                <span>त्वरित प्रेषण संदेश / WhatsApp Remediation Dispatch</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#fee2e2] text-[#ba1a1a]">
                Status: Draft
              </span>
            </div>

            {/* WhatsApp Pre-Formatted Message Box */}
            <div className="bg-[#f8fafc] border border-[#cbd5e1] rounded-lg p-3 font-mono text-[11px] text-[#0f172a] leading-relaxed overflow-x-auto space-y-1.5 mb-3">
              <div className="flex items-center justify-between text-[10px] font-bold text-[#64748b] border-b border-[#e2e8f0] pb-1">
                <span>TO: BMC WARD-04 SANITATION IN-CHARGE</span>
                <span className="text-[#9a3412]">AUTO-FORMATTED</span>
              </div>
              <div className="text-[#ba1a1a] font-bold">
                🚨 *BMC VISARJAN EMERGENCY REMEDIATION ORDER*
              </div>
              <div>*Order Ref:* {activeOrder.id} ({activeOrder.type})</div>
              <div>*Location:* {activeOrder.title.split('—')[0]?.trim()}, Upper Lake, Bhopal</div>
              <div className="text-[#ba1a1a] font-bold">*Priority:* {activeOrder.severity}</div>
              <div>*Required Action:* {activeOrder.desc}</div>
              <div>*Breach Trigger:* {activeOrder.metricLabel} ({activeOrder.metricSub}) ({activeOrder.threshold})</div>
              <div>*Supervisor:* {activeOrder.supervisor} ({activeOrder.phone})</div>
              <div>*Evidentiary Record:* MPPCB Field Ledger #04 (📄 2025 - पृष्ठ 28 (Entry 4B))</div>
              <div className="italic text-[#64748b]">
                _Acknowledge receipt and send geo-tagged commencement photo._
              </div>
              <div className="flex items-center justify-between text-[10px] text-[#94a3b8] pt-1 border-t border-[#e2e8f0]">
                <span>Encrypted Civic Feed</span>
                <span>11:42 AM ✓✓</span>
              </div>
            </div>

            {/* Send & Actions Buttons */}
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => {
                  const text = `*BMC VISARJAN EMERGENCY REMEDIATION ORDER*\nRef: ${activeOrder.id}\nAction: ${activeOrder.desc}\nSupervisor: ${activeOrder.supervisor}`;
                  if (navigator.clipboard) navigator.clipboard.writeText(text);
                  alert(`Copied WhatsApp message for ${activeOrder.id} to clipboard!`);
                }}
                className="w-full py-2.5 px-3 bg-[#9a3412] hover:bg-[#c2410c] text-white rounded-lg font-bold text-xs flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow-xs"
              >
                <span className="material-symbols-outlined text-[16px]">send</span>
                <span>Send via WhatsApp / प्रेषित करें</span>
              </button>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => alert(`Editing WhatsApp template draft for ${activeOrder.id}...`)}
                  className="py-1.5 px-2 bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] rounded border border-[#cbd5e1] font-bold flex items-center justify-center gap-1 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[14px]">edit</span>
                  <span>Edit Draft</span>
                </button>
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="py-1.5 px-2 bg-[#f1f5f9] hover:bg-[#e2e8f0] text-[#0f2942] rounded border border-[#cbd5e1] font-bold flex items-center justify-center gap-1 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[14px]">print</span>
                  <span>Print Work Dossier</span>
                </button>
              </div>
            </div>
          </div>

          {/* Panel 2: प्रमाण एवं प्रयोगशाला उद्धरण / Statutory Proof Dossier */}
          <div className="bg-white rounded-xl border border-[#cbd5e1] shadow-2xs p-4">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#f1f5f9] text-xs">
              <div className="flex items-center gap-1.5 font-bold text-[#0f2942]">
                <span className="material-symbols-outlined text-[16px]">verified</span>
                <span>प्रमाण एवं प्रयोगशाला उद्धरण</span>
              </div>
              <span className="font-mono font-bold text-[#9a3412] bg-[#ffedd5] px-2 py-0.5 rounded text-[11px]">
                {activeOrder.id}
              </span>
            </div>

            <div className="text-[11px] text-[#475569] space-y-1.5 mb-3">
              <div className="flex items-center justify-between">
                <span>Statutory Register:</span>
                <strong className="text-[#0f2942] font-mono">MPPCB Field Ledger #04</strong>
              </div>
              <div className="flex items-center justify-between">
                <span>Official Citation Page:</span>
                <span className="font-mono text-[#ba1a1a] font-bold">📄 2025 · पृष्ठ 28 (Entry 4B)</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Attesting Scientist:</span>
                <span className="text-[#0f2942] font-semibold">Dr. Sunita Verma, Sr. Chemist</span>
              </div>
              <div className="flex items-center justify-between pt-1 border-t border-[#f1f5f9]">
                <span>Live Breach Alert:</span>
                <span className="font-mono font-bold text-[#ba1a1a]">⇘ DO: 2.4 → 0.0 mg/L (Critical)</span>
              </div>
            </div>

            <div className="bg-[#f8fafc] border border-[#e2e8f0] rounded p-2 text-[10px] font-mono text-[#64748b] flex items-center justify-between">
              <span className="flex items-center gap-1 text-[#0f2942] font-bold">
                <span className="material-symbols-outlined text-[14px] text-[#15803d]">lock</span>
                SHA-256 Tamper-Evident Badge
              </span>
              <span>0x7f4C...9E21</span>
            </div>

            <div className="text-[9px] text-[#94a3b8] font-mono mt-1 text-center">
              Digitally timestamped &amp; encrypted on MP State Environmental Grid.
            </div>
          </div>
        </div>
      </div>

      {/* 5. BOTTOM CIVIC COMPLIANCE RULE BANNER (Matching Screenshot 1) */}
      <div className="w-full bg-[#ffedd5]/50 border border-[#fed7aa] rounded-lg p-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#9a3412]">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">info</span>
          <div>
            <strong>Civic Compliance Rule:</strong> A marked "Work Completed" order certifies civic contractor mechanical execution. Water ecological safety re-certification strictly requires subsequent MPPCB laboratory clearance.
          </div>
        </div>
        <span className="font-mono text-[11px] font-bold whitespace-nowrap text-[#c2410c]">
          Bhopal Municipal Corporation Grid • 2025
        </span>
      </div>
    </div>
  );
}
