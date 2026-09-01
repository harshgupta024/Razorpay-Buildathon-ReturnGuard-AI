import React from 'react';
import { ShieldCheck, Zap, Activity, Sliders, ChevronDown } from 'lucide-react';

export default function Header({
  activeTab,
  setActiveTab,
  apiStatus,
  strategyPreset,
  onPresetChange,
  presetsList,
}) {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(11, 15, 25, 0.95)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '0.85rem 2rem',
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        {/* Brand & Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #3395FF 0%, #0052CC 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(51, 149, 255, 0.4)',
          }}>
            <ShieldCheck size={26} color="#FFFFFF" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFFFFF' }}>
                ReturnGuard <span style={{ color: 'var(--color-razorpay)' }}>AI</span>
              </h1>
              <span style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                background: 'rgba(51, 149, 255, 0.15)',
                color: '#3395FF',
                border: '1px solid rgba(51, 149, 255, 0.3)',
                padding: '2px 8px',
                borderRadius: '12px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                Razorpay Track 02
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Pre-Fulfillment Return Risk Intelligence & Cost-Aware Decision Engine
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{
          display: 'flex',
          background: 'rgba(31, 41, 55, 0.6)',
          padding: '4px',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)',
          gap: '4px',
        }}>
          {[
            { id: 'overview', label: '📊 Command Center' },
            { id: 'simulator', label: '⚡ Risk Simulator' },
            { id: 'review', label: '🛡️ Review Queue' },
            { id: 'orders', label: '📜 Orders Feed' },
          ].map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '6px 14px',
                  borderRadius: '7px',
                  border: 'none',
                  fontSize: '0.85rem',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  background: isActive ? 'var(--color-primary)' : 'transparent',
                  color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                  boxShadow: isActive ? '0 2px 8px rgba(59, 130, 246, 0.4)' : 'none',
                }}
              >
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* Strategy Preset Selector & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '0.8rem',
          }}>
            <Sliders size={14} color="var(--text-muted)" />
            <span style={{ color: 'var(--text-muted)' }}>Strategy:</span>
            <select
              value={strategyPreset}
              onChange={(e) => onPresetChange(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-primary)',
                fontWeight: 600,
                fontSize: '0.8rem',
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              <option value="Balanced" style={{ background: '#1F2937' }}>Balanced (Cost-Optimal)</option>
              <option value="Conservative" style={{ background: '#1F2937' }}>Conservative (Frictionless)</option>
              <option value="Aggressive" style={{ background: '#1F2937' }}>Aggressive (Margin Defense)</option>
            </select>
          </div>

          {/* Connection Status Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 10px',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 600,
            background: apiStatus === 'online' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
            color: apiStatus === 'online' ? '#10B981' : '#EF4444',
            border: `1px solid ${apiStatus === 'online' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: apiStatus === 'online' ? '#10B981' : '#EF4444',
              boxShadow: apiStatus === 'online' ? '0 0 8px #10B981' : 'none',
              animation: apiStatus === 'online' ? 'pulseGlow 2s infinite' : 'none',
            }} />
            {apiStatus === 'online' ? 'Engine Active (v1.0.0)' : 'Offline'}
          </div>
        </div>
      </div>
    </header>
  );
}
