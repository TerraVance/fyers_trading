import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import BrokerPage from './pages/BrokerPage';
import DataCenterPage from './pages/DataCenterPage';
import StrategyLabPage from './pages/StrategyLabPage';
import BacktestPage from './pages/BacktestPage';
import PaperPage from './pages/PaperPage';
import LivePage from './pages/LivePage';

const App = () => {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<BrokerPage />} />
          <Route path="/data" element={<DataCenterPage />} />
          <Route path="/strategy" element={<StrategyLabPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
          <Route path="/paper" element={<PaperPage />} />
          <Route path="/live" element={<LivePage />} />
        </Routes>
      </AppLayout>
    </Router>
  );
};

export default App;
