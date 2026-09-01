import React from 'react';
import { TrendingUp, ShieldAlert, DollarSign, CheckCircle2, ArrowUpRight, Percent, Package } from 'lucide-react';

export default function OverviewTab({ analyticsData }) {
  const data = analyticsData || {
    total_orders_analyzed: 15000,
    total_portfolio_value_inr: 42500000.0,
    total_unmitigated_risk_exposure_inr: 2439000.0,
    total_projected_net_savings_inr: 1191900.0,
    portfolio_avg_return_probability: 0.271,
    tier_distribution: { LOW: 6829, MEDIUM: 5462, HIGH: 2684, CRITICAL: 26 },
    tier_proportions: { LOW: 0.4552, MEDIUM: 0.3641, HIGH: 0.1789, CRITICAL: 0.0017 },
    category_breakdown: [],
    recommended_actions_breakdown: {},
  };

  const formatINR = (val) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top 4 KPI Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '1.25rem',
      }}>
        {/* Card 1: Total Portfolio Scored */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Total Orders Analyzed
            </span>
            <div style={{ padding: '6px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.15)', color: '#3B82F6' }}>
              <Package size={18} />
            </div>
          </div>
          <div style={{ marginTop: '0.75rem' }}>
            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#FFFFFF' }}>
              {data.total_orders_analyzed.toLocaleString()}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.25rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <span>Portfolio GMV:</span>
              <strong style={{ color: 'var(--text-primary)' }}>{formatINR(data.total_portfolio_value_inr)}</strong>
            </div>
          </div>
        </div>

        {/* Card 2: Total Return Risk Exposure */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Gross Return Risk Exposure
            </span>
            <div style={{ padding: '6px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.15)', color: '#EF4444' }}>
              <ShieldAlert size={18} />
            </div>
          </div>
          <div style={{ marginTop: '0.75rem' }}>
            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#EF4444' }}>
              {formatINR(data.total_unmitigated_risk_exposure_inr)}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.25rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <span>Baseline Return Rate:</span>
              <strong style={{ color: 'var(--text-primary)' }}>{(data.portfolio_avg_return_probability * 100).toFixed(1)}%</strong>
            </div>
          </div>
        </div>

        {/* Card 3: Net Profit Saved */}
        <div className="glass-panel" style={{ padding: '1.25rem', border: '1px solid rgba(16, 185, 129, 0.35)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#10B981' }}>
              Net Profit Saved (ROI)
            </span>
            <div style={{ padding: '6px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.15)', color: '#10B981' }}>
              <DollarSign size={18} />
            </div>
          </div>
          <div style={{ marginTop: '0.75rem' }}>
            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#10B981' }}>
              {formatINR(data.total_projected_net_savings_inr)}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.25rem', fontSize: '0.78rem', color: '#10B981' }}>
              <TrendingUp size={14} />
              <span>₹{(data.total_projected_net_savings_inr / Math.max(1, data.total_orders_analyzed)).toFixed(1)} avg saved / order</span>
            </div>
          </div>
        </div>

        {/* Card 4: Catch Rate & Cost-Optimal Threshold */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Return Catch Rate (Recall)
            </span>
            <div style={{ padding: '6px', borderRadius: '8px', background: 'rgba(51, 149, 255, 0.15)', color: '#3395FF' }}>
              <CheckCircle2 size={18} />
            </div>
          </div>
          <div style={{ marginTop: '0.75rem' }}>
            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-razorpay)' }}>
              79.5%
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.25rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <span>Operating at Optimal Threshold:</span>
              <strong style={{ color: 'var(--text-primary)' }}>τ* = 0.20</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Tier Risk Spectrum Card */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF' }}>
              Portfolio Return Risk Tier Distribution
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Orders segmented into calibrated risk bands with targeted merchant actions
            </p>
          </div>
        </div>

        {/* Multi-segment Progress Bar */}
        <div style={{
          height: '24px',
          borderRadius: '12px',
          overflow: 'hidden',
          display: 'flex',
          background: '#1F2937',
          border: '1px solid var(--border-subtle)',
          marginBottom: '1.25rem',
        }}>
          <div style={{ width: `${(data.tier_proportions?.LOW || 0.455) * 100}%`, background: 'var(--tier-low)', transition: 'width 0.5s ease' }} title="Low Risk" />
          <div style={{ width: `${(data.tier_proportions?.MEDIUM || 0.364) * 100}%`, background: 'var(--tier-medium)', transition: 'width 0.5s ease' }} title="Medium Risk" />
          <div style={{ width: `${(data.tier_proportions?.HIGH || 0.179) * 100}%`, background: 'var(--tier-high)', transition: 'width 0.5s ease' }} title="High Risk" />
          <div style={{ width: `${Math.max(1, (data.tier_proportions?.CRITICAL || 0.002) * 100)}%`, background: 'var(--tier-critical)', transition: 'width 0.5s ease' }} title="Critical Risk" />
        </div>

        {/* Tier Cards Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          {[
            {
              tier: 'LOW',
              name: 'Low Risk',
              range: '[0.00, 0.20)',
              color: 'var(--tier-low)',
              bg: 'var(--tier-low-bg)',
              border: 'var(--tier-low-border)',
              count: data.tier_distribution?.LOW || 6829,
              pct: ((data.tier_proportions?.LOW || 0.455) * 100).toFixed(1),
              action: '🟢 1-Click Seamless Checkout',
            },
            {
              tier: 'MEDIUM',
              name: 'Medium Risk',
              range: '[0.20, 0.45)',
              color: 'var(--tier-medium)',
              bg: 'var(--tier-medium-bg)',
              border: 'var(--tier-medium-border)',
              count: data.tier_distribution?.MEDIUM || 5462,
              pct: ((data.tier_proportions?.MEDIUM || 0.364) * 100).toFixed(1),
              action: '🟡 Address & Sizing Check',
            },
            {
              tier: 'HIGH',
              name: 'High Risk',
              range: '[0.45, 0.70)',
              color: 'var(--tier-high)',
              bg: 'var(--tier-high-bg)',
              border: 'var(--tier-high-border)',
              count: data.tier_distribution?.HIGH || 2684,
              pct: ((data.tier_proportions?.HIGH || 0.179) * 100).toFixed(1),
              action: '🟠 WhatsApp OTP / ₹100 Deposit',
            },
            {
              tier: 'CRITICAL',
              name: 'Critical Risk',
              range: '[0.70, 1.00]',
              color: 'var(--tier-critical)',
              bg: 'var(--tier-critical-bg)',
              border: 'var(--tier-critical-border)',
              count: data.tier_distribution?.CRITICAL || 26,
              pct: ((data.tier_proportions?.CRITICAL || 0.002) * 100).toFixed(1),
              action: '🔴 Prepaid Only / Manual Queue',
            },
          ].map((t) => (
            <div key={t.tier} style={{
              background: t.bg,
              border: `1px solid ${t.border}`,
              borderRadius: '10px',
              padding: '1rem',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: t.color }}>{t.name}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{t.range}</span>
              </div>
              <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                <strong style={{ fontSize: '1.3rem', color: '#FFFFFF' }}>{t.count.toLocaleString()}</strong>
                <span style={{ fontSize: '0.8rem', color: t.color }}>({t.pct}%)</span>
              </div>
              <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                {t.action}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Category Risk Leaderboard Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.5rem' }}>
          Category Risk & Loss Mitigation Leaderboard
        </h3>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          Product category return propensity and realized merchant savings
        </p>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-medium)', textAlign: 'left', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '10px 14px' }}>Product Category</th>
                <th style={{ padding: '10px 14px' }}>Analyzed Orders</th>
                <th style={{ padding: '10px 14px' }}>Avg Return Risk</th>
                <th style={{ padding: '10px 14px' }}>Projected Savings (INR)</th>
                <th style={{ padding: '10px 14px' }}>Recommended Policy</th>
              </tr>
            </thead>
            <tbody>
              {(data.category_breakdown?.length ? data.category_breakdown : [
                { category: "Clothing", order_count: 3820, avg_return_risk: 0.365, projected_savings_inr: 412000.0 },
                { category: "Footwear", order_count: 2750, avg_return_risk: 0.342, projected_savings_inr: 320000.0 },
                { category: "Electronics", order_count: 2410, avg_return_risk: 0.210, projected_savings_inr: 185000.0 },
                { category: "Beauty", order_count: 1890, avg_return_risk: 0.285, projected_savings_inr: 145000.0 },
                { category: "Home", order_count: 1620, avg_return_risk: 0.198, projected_savings_inr: 89000.0 },
                { category: "Sports", order_count: 1210, avg_return_risk: 0.180, projected_savings_inr: 40900.0 },
              ]).map((row, idx) => (
                <tr key={idx} style={{
                  borderBottom: '1px solid var(--border-subtle)',
                  background: idx % 2 === 0 ? 'rgba(255, 255, 255, 0.01)' : 'transparent',
                }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: '#FFFFFF' }}>{row.category}</td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-secondary)' }}>{row.order_count.toLocaleString()}</td>
                  <td style={{ padding: '12px 14px' }}>
                    <span style={{
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontWeight: 600,
                      fontSize: '0.78rem',
                      background: row.avg_return_risk > 0.30 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                      color: row.avg_return_risk > 0.30 ? '#EF4444' : '#10B981',
                    }}>
                      {(row.avg_return_risk * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ padding: '12px 14px', fontWeight: 700, color: '#10B981' }}>
                    {formatINR(row.projected_savings_inr)}
                  </td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {row.avg_return_risk > 0.30 ? 'Interactive WhatsApp & Size Confirm' : 'Seamless 1-Click Buy'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
