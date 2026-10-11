import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext.jsx';
import SharedLayout from './components/SharedLayout.jsx';

import Overview from './pages/Overview.jsx';
import GhatDetail from './pages/GhatDetail.jsx';
import ParameterDetail from './pages/ParameterDetail.jsx';
import Coverage from './pages/Coverage.jsx';
import MapPage from './pages/MapPage.jsx';
import WorkOrders from './pages/WorkOrders.jsx';
import Brief from './pages/Brief.jsx';
import About from './pages/About.jsx';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <SharedLayout>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/ghat/:id" element={<GhatDetail />} />
            <Route path="/ghat/:id/:param" element={<ParameterDetail />} />
            <Route path="/coverage" element={<Coverage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/work-orders" element={<WorkOrders />} />
            <Route path="/brief" element={<Brief />} />
            <Route path="/about" element={<About />} />
            {/* Fallback */}
            <Route path="*" element={<Overview />} />
          </Routes>
        </SharedLayout>
      </BrowserRouter>
    </AppProvider>
  );
}
