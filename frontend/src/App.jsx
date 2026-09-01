import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import OverviewTab from './components/OverviewTab';
import SimulatorTab from './components/SimulatorTab';
import ReviewQueueTab from './components/ReviewQueueTab';
import OrdersFeedTab from './components/OrdersFeedTab';
import { fetchHealth, fetchAnalyticsSummary, fetchThresholdConfig, updateThresholdPreset } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [apiStatus, setApiStatus] = useState('checking');
  const [strategyPreset, setStrategyPreset] = useState('Balanced');
  const [analyticsData, setAnalyticsData] = useState(null);

  const checkStatusAndData = async () => {
    const health = await fetchHealth();
    setApiStatus(health.status === 'healthy' ? 'online' : 'offline');

    const analytics = await fetchAnalyticsSummary();
    setAnalyticsData(analytics);
  };

  useEffect(() => {
    checkStatusAndData();
    const interval = setInterval(checkStatusAndData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handlePresetChange = async (newPreset) => {
    setStrategyPreset(newPreset);
    try {
      await updateThresholdPreset(newPreset);
    } catch (err) {
      console.warn("Could not update backend preset dynamically:", err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-main)' }}>
      {/* Top Navigation Bar */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiStatus={apiStatus}
        strategyPreset={strategyPreset}
        onPresetChange={handlePresetChange}
      />

      {/* Main Content Area */}
      <main style={{
        maxWidth: '1440px',
        width: '100%',
        margin: '0 auto',
        padding: '1.5rem 2rem 3rem',
        flex: 1,
      }}>
        {activeTab === 'overview' && <OverviewTab analyticsData={analyticsData} />}
        {activeTab === 'simulator' && <SimulatorTab />}
        {activeTab === 'review' && <ReviewQueueTab />}
        {activeTab === 'orders' && <OrdersFeedTab />}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '1rem 2rem',
        textAlign: 'center',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
      }}>
        ReturnGuard AI • Razorpay Buildathon 2026 • AI-Powered E-Commerce Return Risk & Decision Intelligence
      </footer>
    </div>
  );
}
