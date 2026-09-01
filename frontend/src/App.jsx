import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
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
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-app)' }}>
      {/* Authentic Razorpay Dark Navy Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingReviewCount={2}
      />

      {/* Main Merchant Portal Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopNav
          activeTab={activeTab}
          strategyPreset={strategyPreset}
          onPresetChange={handlePresetChange}
          apiStatus={apiStatus}
        />

        <main style={{
          padding: '1.5rem 2rem 3rem',
          maxWidth: '1400px',
          width: '100%',
          margin: '0 auto',
          flex: 1,
        }}>
          {activeTab === 'overview' && <OverviewTab analyticsData={analyticsData} />}
          {activeTab === 'simulator' && <SimulatorTab />}
          {activeTab === 'review' && <ReviewQueueTab />}
          {activeTab === 'orders' && <OrdersFeedTab />}
        </main>
      </div>
    </div>
  );
}
