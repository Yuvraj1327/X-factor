// API Client for Visarjan Ghat Watch API
// Base URL: https://api-production-9a4c9.up.railway.app
// Interactive docs: https://api-production-9a4c9.up.railway.app/docs

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://api-production-9a4c9.up.railway.app';

// Geographic coordinates and metadata for the 7 statutory Bhopal sites
export const GHAT_COORDINATES = {
  'Bairagarh (Sant Hirdaram) kund': {
    id: '1',
    rank: 1,
    lat: 23.2750,
    lng: 77.3420,
    nameHi: 'बैरागढ़ (संत हिरदाराम) कुंड',
    ward: 'वार्ड 04',
    basin: 'बड़ा तालाब पश्चिमी तट · Ramsar Inlet Enclosure'
  },
  'Malikhedi kund': {
    id: '2',
    rank: 2,
    lat: 23.2620,
    lng: 77.4680,
    nameHi: 'मालीखेड़ी कुंड',
    ward: 'वार्ड 65',
    basin: 'हलाली / पूर्वी जलग्रहण क्षेत्र · Zone 18'
  },
  'Rani Kamlapati ghat / Kamla Park kund': {
    id: '3',
    rank: 3,
    lat: 23.2435,
    lng: 77.3995,
    nameHi: 'रानी कमलापति घाट / कमला पार्क कुंड',
    ward: 'वार्ड 17',
    basin: 'बड़े और छोटे तालाब के बीच का स्पिलवे [स्थान संशय]'
  },
  'Shahpura lake ghat': {
    id: '4',
    rank: 4,
    lat: 23.2052,
    lng: 77.4320,
    nameHi: 'शाहपुरा विसर्जन घाट',
    ward: 'वार्ड 47',
    basin: 'शाहपुरा झील (दक्षिणी जलग्रहण) · Zone 11'
  },
  'Khatlapura ghat': {
    id: '5',
    rank: 5,
    lat: 23.2425,
    lng: 77.4120,
    nameHi: 'खटलापुरा घाट',
    ward: 'वार्ड 22',
    basin: 'छोटा तालाब पूर्वी खाड़ी · Zone 8'
  },
  'Hathaikheda dam / kund': {
    id: '6',
    rank: 6,
    lat: 23.2680,
    lng: 77.4850,
    nameHi: 'हथाईखेड़ा बांध / कुंड',
    ward: 'वार्ड 62',
    basin: 'हथाईखेड़ा जलाशय पूर्वी परिक्षेत्र · Zone 17'
  },
  'Prempura ghat': {
    id: '7',
    rank: 7,
    lat: 23.2210,
    lng: 77.3620,
    nameHi: 'प्रेमपुरा घाट',
    ward: 'वार्ड 34',
    basin: 'बड़ा तालाब (भदभदा रोड सेक्टर) · Zone 5'
  }
};

/**
 * Fetch ranked dashboard data from GET /ranking
 */
export async function fetchRanking() {
  const res = await fetch(`${API_BASE_URL}/ranking`);
  if (!res.ok) {
    throw new Error(`Failed to fetch ranking: ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Fetch forwardable executive summary from GET /brief
 * @param {('en'|'hi')} lang - Language code
 * @param {('page'|'whatsapp')} format - Output format
 */
export async function fetchBrief(lang = 'en', format = 'page') {
  const params = new URLSearchParams({ lang, format });
  const res = await fetch(`${API_BASE_URL}/brief?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch brief: ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Formats a relative PDF link into an absolute URL pointing to the API host
 * e.g. "/reports/2023_MPPCB_Idol_Immersion_Report.pdf#page=60" -> "https://api-production-9a4c9.up.railway.app/reports/..."
 */
export function getPdfUrl(pdfPath) {
  if (!pdfPath) return '';
  if (pdfPath.startsWith('http://') || pdfPath.startsWith('https://')) {
    return pdfPath;
  }
  return `${API_BASE_URL}${pdfPath}`;
}
