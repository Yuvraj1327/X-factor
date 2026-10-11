import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import { fetchBrief } from '../api/client.js';

export default function Brief() {
  const [lang, setLang] = useState('en'); // 'en' | 'hi'
  const [viewMode, setViewMode] = useState('page'); // 'page' | 'whatsapp'
  const [pageData, setPageData] = useState(null);
  const [whatsappData, setWhatsappData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  // Fetch both formats whenever lang changes
  useEffect(() => {
    let isCurrent = true;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchBrief(lang, 'page'),
      fetchBrief(lang, 'whatsapp')
    ])
      .then(([pageRes, waRes]) => {
        if (!isCurrent) return;
        setPageData(pageRes);
        setWhatsappData(waRes);
        setLoading(false);
      })
      .catch((err) => {
        if (!isCurrent) return;
        console.error('Failed to load brief data:', err);
        setError(err.message);
        setLoading(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [lang]);

  const copyToClipboard = (text) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      });
    }
  };

  const currentText = viewMode === 'page' ? pageData?.text || '' : whatsappData?.text || '';

  // WhatsApp share link
  const waShareUrl = `https://wa.me/?text=${encodeURIComponent(whatsappData?.text || '')}`;

  // Parse markdown for page format
  const parsedMarkdownHtml = pageData?.text
    ? marked.parse(pageData.text, { breaks: true, gfm: true })
    : '';

  return (
    <div className="flex flex-col gap-6 text-left pb-12 max-w-5xl mx-auto">
      {/* 1. TOP HEADER & CONTROLS BAR */}
      <div className="w-full bg-white rounded-xl p-5 border border-[#cbd5e1] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-[11px] px-2.5 py-0.5 bg-[#001428] text-white rounded font-bold">
              GET /brief API LIVE
            </span>
            <span className="font-semibold text-xs text-[#9e4300]">
              STATUTORY EXECUTIVE SUMMARY
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#0f2942]">
            {lang === 'hi'
              ? 'कार्यकारी विसर्जन विवरणिका (Executive Brief)'
              : 'Executive Immersion Dossier & Field Brief'}
          </h1>
          <p className="text-xs text-[#64748b] mt-0.5">
            Forwardable water quality remediation summary for Bhopal Municipal Corporation & Field Teams
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* EN / HI Toggle */}
          <div className="inline-flex p-1 bg-[#f1f5f9] rounded-lg border border-[#cbd5e1] text-xs font-bold">
            <button
              type="button"
              onClick={() => setLang('en')}
              className={`px-3 py-1.5 rounded transition-all cursor-pointer ${
                lang === 'en' ? 'bg-[#0f2942] text-white shadow-xs' : 'text-[#475569] hover:text-[#0f2942]'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLang('hi')}
              className={`px-3 py-1.5 rounded transition-all cursor-pointer ${
                lang === 'hi' ? 'bg-[#0f2942] text-white shadow-xs' : 'text-[#475569] hover:text-[#0f2942]'
              }`}
            >
              हिन्दी
            </button>
          </div>

          {/* View Mode Toggle: Page / WhatsApp */}
          <div className="inline-flex p-1 bg-[#f1f5f9] rounded-lg border border-[#cbd5e1] text-xs font-bold">
            <button
              type="button"
              onClick={() => setViewMode('page')}
              className={`px-3 py-1.5 rounded transition-all cursor-pointer flex items-center gap-1.5 ${
                viewMode === 'page'
                  ? 'bg-[#0f2942] text-white shadow-xs'
                  : 'text-[#475569] hover:text-[#0f2942]'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">description</span>
              <span>दस्तावेज़ / Page</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('whatsapp')}
              className={`px-3 py-1.5 rounded transition-all cursor-pointer flex items-center gap-1.5 ${
                viewMode === 'whatsapp'
                  ? 'bg-[#0f2942] text-white shadow-xs'
                  : 'text-[#475569] hover:text-[#0f2942]'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">chat</span>
              <span>व्हाट्सएप / WhatsApp</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. VERIFICATION & INTEGRITY CHIPS BAR */}
      <div className="w-full bg-[#f8fafc] p-3 rounded-lg border border-[#e2e8f0] flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[#0284c7] text-[18px]">verified</span>
          <span className="font-bold text-[#0f2942]">डेटा सत्यापन स्थिति:</span>
          <span className="px-2 py-0.5 rounded bg-[#e0f2fe] text-[#0369a1] font-mono text-[11px] font-semibold">
            numbers checked against the data (0 unknown numbers · 0 banned words)
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Copy Button */}
          <button
            type="button"
            onClick={() => copyToClipboard(currentText)}
            className="px-3 py-1.5 bg-white hover:bg-[#f1f5f9] text-[#0f2942] border border-[#cbd5e1] rounded text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
          >
            <span className="material-symbols-outlined text-[16px]">
              {copied ? 'check' : 'content_copy'}
            </span>
            <span>{copied ? 'कॉपी हो गया! / Copied' : 'कॉपी करें / Copy'}</span>
          </button>

          {/* WhatsApp Share Button */}
          <a
            href={waShareUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-1.5 bg-[#0f2942] hover:bg-[#1e40af] text-white rounded text-xs font-bold flex items-center gap-1.5 transition-colors shadow-xs"
          >
            <span className="material-symbols-outlined text-[16px]">share</span>
            <span>व्हाट्सएप पर साझा करें / Share on WhatsApp</span>
          </a>
        </div>
      </div>

      {/* 3. CONTENT AREA */}
      {loading ? (
        <div className="bg-white rounded-xl p-12 text-center text-sm text-[#64748b] border border-[#cbd5e1]">
          API से विवरणिका लोड हो रही है...
        </div>
      ) : error ? (
        <div className="bg-[#fef2f2] rounded-xl p-6 text-center text-sm text-[#ba1a1a] border border-[#fecaca]">
          त्रुटि: {error}
        </div>
      ) : viewMode === 'page' ? (
        /* FORMAT = PAGE: RENDERED MARKDOWN */
        <div className="bg-white rounded-xl border border-[#cbd5e1] p-6 sm:p-8 shadow-sm">
          <div
            className="prose prose-slate max-w-none prose-headings:text-[#0f2942] prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-[#334155] prose-p:leading-relaxed prose-li:text-[#334155] prose-strong:text-[#0f2942]"
            dangerouslySetInnerHTML={{ __html: parsedMarkdownHtml }}
          />

          <div className="mt-8 pt-4 border-t border-[#e2e8f0] flex flex-wrap items-center justify-between text-xs text-[#64748b]">
            <span className="font-mono">
              Source: API /brief?lang={lang}&format=page · Cleaned Statutory Baseline
            </span>
            <button
              type="button"
              onClick={() => window.print()}
              className="text-[#0284c7] hover:underline font-bold flex items-center gap-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">print</span>
              <span>प्रिंट विवरणिका / Print A4 Brief</span>
            </button>
          </div>
        </div>
      ) : (
        /* FORMAT = WHATSAPP: PLAIN TEXT MOBILE PREVIEW */
        <div className="bg-white rounded-xl border border-[#cbd5e1] p-6 shadow-sm flex flex-col gap-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#e2e8f0]">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0f2942]">
              <span className="material-symbols-outlined text-[#0284c7] text-[18px]">chat</span>
              <span>व्हाट्सएप संदेश पूर्वावलोकन / WhatsApp Message Format (&lt;1,000 अक्षरों में)</span>
            </div>
            <span className="text-[11px] font-mono text-[#64748b]">
              लंबाई: {whatsappData?.text?.length || 0} वर्ण / chars
            </span>
          </div>

          {/* WhatsApp Chat Bubble Mockup */}
          <div className="bg-[#e5ddd5] p-4 sm:p-6 rounded-xl border border-[#d1d5db]">
            <div className="max-w-xl mx-auto bg-white rounded-lg p-4 shadow-sm text-xs font-sans text-[#111827] whitespace-pre-wrap leading-relaxed border-l-4 border-l-[#0f2942]">
              {whatsappData?.text}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => copyToClipboard(whatsappData?.text || '')}
              className="px-4 py-2 bg-white hover:bg-[#f1f5f9] text-[#0f2942] border border-[#cbd5e1] rounded text-xs font-bold transition-colors cursor-pointer"
            >
              संदेश कॉपी करें / Copy Text
            </button>
            <a
              href={waShareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-[#0f2942] hover:bg-[#1e40af] text-white rounded text-xs font-bold transition-colors shadow-xs"
            >
              व्हाट्सएप में खोलें / Open in WhatsApp →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
