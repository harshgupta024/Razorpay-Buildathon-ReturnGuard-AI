import React from 'react';
import { Search, ChevronRight, SlidersHorizontal, Bell, HelpCircle } from 'lucide-react';

export default function TopNav({
  activeTab,
  strategyPreset,
  onPresetChange,
  apiStatus,
}) {
  const tabTitles = {
    overview: 'Overview & Margin Performance',
    simulator: 'Order Risk Inspector',
    review: 'High-Risk Review Queue',
    orders: 'Orders Ledger',
  };

  return (
    <div style={{
      background: '#FFFFFF',
      borderBottom: '1px solid var(--border-subtle)',
      padding: '0.85rem 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 40,
    }}>
      {/* Breadcrumb Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.84rem' }}>
        <span style={{ color: 'var(--text-muted)' }}>ReturnGuard</span>
        <ChevronRight size={14} color="var(--text-muted)" />
        <span style={{ color: 'var(--text-secondary)' }}>Risk Operations</span>
        <ChevronRight size={14} color="var(--text-muted)" />
        <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
          {tabTitles[activeTab] || 'Dashboard'}
        </span>
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Strategy Preset Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            Policy Mode:
          </span>
          <select
            value={strategyPreset}
            onChange={(e) => onPresetChange(e.target.value)}
            style={{
              background: '#F8FAFC',
              border: '1px solid var(--border-default)',
              color: 'var(--text-primary)',
              fontSize: '0.8rem',
              fontWeight: 600,
              padding: '4px 8px',
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

        {/* Engine Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          fontSize: '0.75rem',
          color: apiStatus === 'online' ? '#15803D' : '#B91C1C',
          background: apiStatus === 'online' ? '#DCFCE7' : '#FEE2E2',
          border: `1px solid ${apiStatus === 'online' ? '#BBF7D0' : '#FECACA'}`,
          padding: '2px 8px',
          borderRadius: '4px',
          fontWeight: 600,
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: apiStatus === 'online' ? '#16A34A' : '#DC2626',
          }} />
          <span>{apiStatus === 'online' ? 'Engine Online' : 'Offline'}</span>
        </div>
      </div>
    </div>
  );
}
