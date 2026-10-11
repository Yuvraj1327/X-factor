import React, { useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext.jsx';
import ProofDrawer from './ProofDrawer.jsx';

function getDaysUntilVisarjan() {
  const target = new Date(2026, 9, 20); // 2026-10-20
  const today = new Date();
  const diffTime = target.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return Math.max(0, diffDays);
}

export default function SharedLayout({ children }) {
  const { lang, setLang } = useApp();
  const location = useLocation();
  const daysLeft = getDaysUntilVisarjan();
  const [fontSizeClass, setFontSizeClass] = useState('text-base');

  const navLinks = [
    { to: '/', label: 'प्राथमिकता / Priority', icon: 'format_list_bulleted' },
    { to: '/ghat/1', label: 'घाट विवरण / Ghat Detail', icon: 'water_drop' },
    { to: '/brief', label: 'कार्यकारी सारांश / Brief', icon: 'description' },
    { to: '/coverage', label: 'डेटा कवरेज / Data Coverage', icon: 'grid_view' },
    { to: '/work-orders', label: 'कार्य आदेश / Work Orders', icon: 'assignment' },
    { to: '/map', label: 'घाट मानचित्र / Ghat Geospatial Map', icon: 'map', hasDot: true },
    { to: '/about', label: 'पद्धति एवं मानक / About & Standards', icon: 'verified' },
  ];

  return (
    <div className={`min-h-screen flex flex-col bg-[#f6f7f9] text-[#001b3d] ${fontSizeClass}`}>
      {/* Sticky Top Header */}
      <header className="sticky top-0 z-50 bg-[#0c1a29] text-white shadow-md border-b border-[#1b2b3d] no-print">
        {/* Top Header Row */}
        <div className="w-full max-w-[1440px] mx-auto px-4 py-2.5 flex flex-wrap items-center justify-between gap-3">
          {/* Left: Emblem + Droplet + Title + Subtitle */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-white/10 border border-white/20 flex items-center justify-center text-white shrink-0">
              <span className="material-symbols-outlined text-[20px]">account_balance</span>
            </div>
            <div className="w-9 h-9 rounded bg-[#d96b27] flex items-center justify-center text-white shrink-0 shadow-sm">
              <span className="material-symbols-outlined text-[20px]">water_drop</span>
            </div>
            <div className="flex flex-col leading-tight">
              <div className="flex items-center gap-2">
                <span className="font-bold text-base sm:text-lg tracking-tight text-white">
                  विसर्जन जल-निगरानी
                </span>
                <span className="text-white/60 font-light">/</span>
                <span className="text-white/90 text-sm font-semibold">Visarjan Ghat Watch</span>
                <span className="hidden md:inline-block px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#1e2f42] text-[#93c5fd] border border-[#2e435a]">
                  MPPCB &amp; BMC STATUTORY GRID
                </span>
              </div>
              <div className="text-[11px] text-white/60 font-sans tracking-wide">
                भोपाल नगर पालिक निगम · एनजीटी ओए 37/2020 विहित संज्ञान पोर्टल (1440 Spatial Surveillance)
              </div>
            </div>
          </div>

          {/* Center: Dynamic Countdown Chip & Compliance Badge */}
          <div className="hidden xl:flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#1e2f42] border border-[#334a63] text-xs shadow-xs">
              <span className="material-symbols-outlined text-[#ff8843] text-[18px]">event_upcoming</span>
              <span className="text-white font-medium">दुर्गा विसर्जन: <strong className="text-white">20 अक्टू 2026</strong></span>
              <span className="w-1.5 h-1.5 rounded-full bg-[#ff8843]"></span>
              <span className="text-[#ffdbcb] font-bold font-mono">{daysLeft} दिन शेष</span>
            </div>

            <div className="hidden 2xl:flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#132333] border border-[#22384e] text-[11px] text-[#cbd5e1] font-mono">
              <span className="material-symbols-outlined text-[15px] text-[#38bdf8]">verified</span>
              <span>CPCB Class B Standard Compliant</span>
            </div>
          </div>

          {/* Right: Language toggle + Font controls + Print Dossier + User profile */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* Language Toggle */}
            <div className="flex items-center rounded bg-[#1e2f42] border border-[#334a63] p-0.5 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setLang('hi')}
                className={`px-2 py-1 rounded text-xs transition-colors cursor-pointer ${
                  lang === 'hi' ? 'bg-[#d96b27] text-white font-bold' : 'text-white/70 hover:text-white'
                }`}
              >
                हिं
              </button>
              <button
                type="button"
                onClick={() => setLang('en')}
                className={`px-2 py-1 rounded text-xs transition-colors cursor-pointer ${
                  lang === 'en' ? 'bg-[#d96b27] text-white font-bold' : 'text-white/70 hover:text-white'
                }`}
              >
                EN
              </button>
            </div>

            {/* Font size adjustments */}
            <div className="hidden sm:flex items-center rounded bg-[#1e2f42] border border-[#334a63] text-xs font-mono">
              <button
                type="button"
                onClick={() => setFontSizeClass('text-sm')}
                className="px-2 py-1 hover:text-white text-white/70"
                title="Decrease font size"
              >
                A-
              </button>
              <span className="text-white/30">|</span>
              <button
                type="button"
                onClick={() => setFontSizeClass('text-base')}
                className="px-2 py-1 hover:text-white text-white font-bold"
                title="Reset font size"
              >
                A
              </button>
              <span className="text-white/30">|</span>
              <button
                type="button"
                onClick={() => setFontSizeClass('text-lg')}
                className="px-2 py-1 hover:text-white text-white/70"
                title="Increase font size"
              >
                A+
              </button>
            </div>

            {/* Print dossier button */}
            <button
              type="button"
              onClick={() => window.print()}
              className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#1e2f42] hover:bg-[#2b415a] border border-[#334a63] text-xs text-white font-medium transition-colors cursor-pointer shadow-xs"
            >
              <span className="material-symbols-outlined text-[16px]">print</span>
              <span>प्रिंट डॉसियर</span>
            </button>

            {/* Official Nodal Officer badge */}
            <div className="flex items-center gap-2 pl-1 border-l border-white/20">
              <div className="w-8 h-8 rounded-full bg-[#d96b27] text-white font-bold font-mono text-xs flex items-center justify-center shrink-0">
                RS
              </div>
              <div className="hidden lg:flex flex-col leading-tight text-left">
                <span className="text-xs font-bold text-white">Dr. R. K. Saxena</span>
                <span className="text-[10px] text-white/60">Nodal Officer (Env) · BMC</span>
              </div>
            </div>
          </div>
        </div>

        {/* Second Navigation Strip (Matches screenshots 1 & 2) */}
        <div className="w-full bg-[#07131f] border-t border-[#1a2c3f]">
          <div className="max-w-[1440px] mx-auto px-4 flex items-center gap-1 overflow-x-auto scrollbar-none py-1">
            {navLinks.map((item) => {
              const isActive =
                item.to === '/'
                  ? location.pathname === '/'
                  : location.pathname.startsWith(item.to);

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-1.5 px-3.5 py-2 rounded text-xs font-semibold whitespace-nowrap transition-colors ${
                    isActive
                      ? 'bg-[#1e2f42] text-white border-b-2 border-[#d96b27] shadow-xs'
                      : 'text-white/70 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <span className="material-symbols-outlined text-[16px] text-[#cbd5e1]">
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                  {item.hasDot && (
                    <span className="w-2 h-2 rounded-full bg-[#d96b27] ml-0.5 animate-pulse"></span>
                  )}
                </NavLink>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-[1440px] mx-auto px-4 md:px-6 py-5">
        {children}
      </main>

      {/* Persistent Proof Drawer Slide-over / Mobile Bottom-sheet */}
      <ProofDrawer />

      {/* Footer matching Screenshot 1 & 2 */}
      <footer className="w-full bg-[#f0f3f6] text-[#43474d] border-t border-[#d8dce2] py-4 px-4 md:px-8 mt-10 text-xs text-center">
        <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-3 text-left">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-[#001428]">
              नमूना डेटा / sample data ·
            </span>
            <span>
              Bhopal Municipal Corporation &amp; MPPCB Statutory Surveillance Grid protocols. Governed strictly by CPCB Class B (Outdoor Bathing) Criteria.
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium text-[#43474d] shrink-0">
            <Link to="/about" className="hover:underline">CPCB Criteria</Link>
            <span>•</span>
            <Link to="/about" className="hover:underline">Methodology</Link>
            <span>•</span>
            <span className="hover:underline cursor-pointer">Grievance Redressal</span>
          </div>
        </div>
        <div className="max-w-[1440px] mx-auto mt-2 pt-2 border-t border-[#e2e8f0] text-[11px] text-[#74777e] flex flex-col sm:flex-row items-center justify-between">
          <span>© 2026 भोपाल नगर निगम (BMC) &amp; MPPCB. Sample data - नमूना डेटा</span>
          <span>Environment &amp; Lake Conservation Wing, Vallabh Bhawan Road, Bhopal (M.P.)</span>
        </div>
      </footer>
    </div>
  );
}
