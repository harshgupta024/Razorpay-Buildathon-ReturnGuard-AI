import React from 'react';
import { Shield, ChevronDown, SlidersHorizontal, Search, Bell, ExternalLink } from 'lucide-react';

export default function Header({
  activeTab,
  setActiveTab,
  apiStatus,
  strategyPreset,
  onPresetChange,
  pendingReviewCount = 2,
}) {
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'simulator', label: 'Risk Inspector' },
    { id: 'review', label: 'Review Queue', badge: pendingReviewCount },
    { id: 'orders', label: 'Orders Ledger' },
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.08)',
    }}>
      {/* Top Razorpay Navy Bar */}
      <div style={{
        background: '#0C2340',
        padding: '0.65rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        color: '#FFFFFF',
      }}>
        {/* Left: Razorpay Brand & Merchant Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '4px',
              background: '#3395FF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
            }}>
              <Shield size={16} />
            </div>
            <div>
              <span style={{ fontSize: '0.92rem', fontWeight: 700, letterSpacing: '-0.01em' }}>
                Razorpay <span style={{ color: '#3395FF', fontWeight: 500 }}>ReturnGuard</span>
              </span>
            </div>
          </div>

          <div style={{ height: '14px', width: '1px', background: 'rgba(255, 255, 255, 0.2)' }} />

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.78rem',
            color: '#E2E8F0',
            cursor: 'pointer',
            padding: '3px 8px',
            borderRadius: '4px',
            background: 'rgba(255, 255, 255, 0.08)',
          }}>
            <span>D2C Merchant Account (MID: 894120)</span>
            <ChevronDown size={13} color="#94A3B8" />
          </div>
        </div>

        {/* Right: Policy Preset & Environment Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Policy Preset Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Threshold Mode:</span>
            <select
              value={strategyPreset}
              onChange={(e) => onPresetChange(e.target.value)}
              style={{
                background: '#1A3353',
                border: '1px solid #2B4B73',
                color: '#FFFFFF',
                fontSize: '0.78rem',
                fontWeight: 500,
                padding: '3px 8px',
                borderRadius: '4px',
                cursor: 'pointer',
                width: 'auto',
              }}
            >
              <option value="Conservative">Conservative (High Approval)</option>
              <option value="Balanced">Balanced (Cost-Optimal τ=0.20)</option>
              <option value="Aggressive">Aggressive (Strict Margin)</option>
            </select>
          </div>

          {/* Live Mode Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            fontSize: '0.72rem',
            fontWeight: 600,
            color: '#10B981',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            padding: '2px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase',
          }}>
            <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#10B981' }} />
            <span>Live Mode</span>
          </div>
        </div>
      </div>

      {/* Sub White Navigation Bar */}
      <div style={{
        background: '#FFFFFF',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '0 1.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '0.75rem 1rem',
                  border: 'none',
                  background: 'transparent',
                  fontSize: '0.84rem',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? '#0C2340' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  borderBottom: isActive ? '2px solid #3395FF' : '2px solid transparent',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                }}
              >
                <span>{tab.label}</span>
                {tab.badge && (
                  <span style={{
                    background: '#FEE2E2',
                    color: '#B91C1C',
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    padding: '1px 5px',
                    borderRadius: '10px',
                  }}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          API SLA: <strong style={{ color: '#15803D' }}>0.002 ms</strong>
        </div>
      </div>
    </header>
  );
}
