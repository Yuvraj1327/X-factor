import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchRanking, getPdfUrl } from '../api/client.js';
import fallbackRanking from '../data/rankingFallback.json';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [lang, setLang] = useState('en'); // 'en' | 'hi'
  const [rankingData, setRankingData] = useState(fallbackRanking);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Proof Panel slide-over state
  const [proof, setProof] = useState({
    isOpen: false,
    reportYear: '2025',
    reportPage: '28',
    rawValue: '0.0 mg/L',
    cleanedValue: '0.0',
    unit: 'mg/L',
    param: 'Dissolved Oxygen (Oxygen)',
    station: 'Bairagarh (Sant Hirdaram) kund',
    standard: 'CPCB Class B limit: ≥ 5.0 mg/L',
    dataState: '● Measured Titration',
    pdfUrl: '',
    qualityFlag: ''
  });

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetchRanking();
      setRankingData(res);
    } catch (err) {
      console.warn('API ranking fetch failed, using bundled fallback:', err);
      setError(err.message);
      // Fallback already preloaded
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const openProof = (details) => {
    setProof((prev) => ({
      ...prev,
      ...details,
      pdfUrl: details.pdf ? getPdfUrl(details.pdf) : details.pdfUrl || prev.pdfUrl,
      isOpen: true
    }));
  };

  const closeProof = () => {
    setProof((prev) => ({ ...prev, isOpen: false }));
  };

  return (
    <AppContext.Provider
      value={{
        lang,
        setLang,
        rankingData,
        ghats: rankingData?.ghats || [],
        loading,
        error,
        refreshRanking: loadData,
        proof,
        openProof,
        closeProof,
        getPdfUrl
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
