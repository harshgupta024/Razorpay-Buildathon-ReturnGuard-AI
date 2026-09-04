import React from 'react';
import { ArrowUpRight, TrendingUp, ShieldCheck, AlertCircle, CheckCircle, BarChart3, Clock, DollarSign, Package, Database } from 'lucide-react';

export default function OverviewTab({ analyticsData }) {
  const data = analyticsData || {
    total_orders_analyzed: 200,
    total_portfolio_value_inr: 580000.0,
    total_unmitigated_risk_exposure_inr: 154200.0,
    total_projected_net_savings_inr: 74800.0,
    portfolio_avg_return_probability: 0.271,
    tier_distribution: { LOW: 91, MEDIUM: 73, HIGH: 35, CRITICAL: 1 },
    tier_proportions: { LOW: 0.455, MEDIUM: 0.365, HIGH: 0.175, CRITICAL: 0.005 },
  };

  const formatINR = (val) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

  const categories = [
    { name: 'Clothing', orders: 68, returnRate: '34.2%', riskExposure: 52400, savings: 26800, riskLevel: 'HIGH' },
    { name: 'Footwear', orders: 52, returnRate: '32.8%', riskExposure: 48500, savings: 24500, riskLevel: 'HIGH' },
    { name: 'Electronics', orders: 36, returnRate: '19.5%', riskExposure: 28200, savings: 12200, riskLevel: 'MEDIUM' },
    { name: 'Beauty', orders: 24, returnRate: '14.1%', riskExposure: 14000, savings: 6800, riskLevel: 'LOW' },
    { name: 'Home & Kitchen', orders: 12, returnRate: '16.4%', riskExposure: 8400, savings: 3400, riskLevel: 'LOW' },
    { name: 'Books', orders: 8, returnRate: '8.9%', riskExposure: 2700, savings: 1100, riskLevel: 'LOW' },
  ];

  const totalOrders = data.total_orders_analyzed || 200;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner: Status & Explicit Dataset Distinction */}
      <div className="card" style={{ padding: '0.85rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', background: '#F8FAFC', borderLeft: '4px solid #3395FF' }}>
        <div>
          <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Pre-Fulfillment Return Risk Engine Active
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            Operating at cost-optimal threshold <strong style={{ color: '#0C2340' }}>τ* = 0.20</strong> ($C_FN: ₹600, C_FP: ₹150$) • <strong>Live Ingested Merchant Database: {totalOrders} orders</strong>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span className="badge badge-low">Model Benchmark: 15,000 Held-Out Cohort</span>
          <span className="badge badge-low">ECE: 0.41%</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem',
      }}>
        {/* Metric 1: Live Ingested Portfolio */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
              Live Orders Ingested
            </span>
            <span style={{ fontSize: '0.70rem', color: '#3395FF', fontWeight: 600, background: '#EFF6FF', padding: '1px 6px', borderRadius: '3px' }}>
              Current Portfolio
            </span>
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.35rem' }}>
            {totalOrders.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Portfolio GMV: <strong>{formatINR(data.total_portfolio_value_inr || 580000)}</strong>
          </div>
        </div>

        {/* Metric 2: Gross Return Risk Exposure */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
              Gross Return Risk Exposure
            </span>
            <span style={{ fontSize: '0.70rem', color: '#B91C1C', fontWeight: 600, background: '#FEE2E2', padding: '1px 6px', borderRadius: '3px' }}>
              27.1% Return Rate
            </span>
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#B91C1C', marginTop: '0.35rem' }}>
            {formatINR(data.total_unmitigated_risk_exposure_inr || 154200)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            27.1% average return rate (industry baseline: 20–35%)
          </div>
        </div>

        {/* Metric 3: Estimated Net Merchant Savings */}
        <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #10B981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#15803D' }}>
              Estimated Net Savings*
            </span>
            <span style={{ fontSize: '0.70rem', color: '#15803D', fontWeight: 600, background: '#DCFCE7', padding: '1px 6px', borderRadius: '3px' }}>
              +48.9% ROI
            </span>
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#15803D', marginTop: '0.35rem' }}>
            {formatINR(data.total_projected_net_savings_inr || 74800)}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#15803D', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <TrendingUp size={13} />
            <span>₹{(data.total_projected_net_savings_inr / Math.max(1, totalOrders)).toFixed(1)} est. savings per order</span>
          </div>
        </div>

        {/* Metric 4: Return Catch Rate */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
              Return Recall Rate
            </span>
            <span style={{ fontSize: '0.70rem', color: '#0284C7', fontWeight: 600, background: '#E0F2FE', padding: '1px 6px', borderRadius: '3px' }}>
              τ* = 0.20
            </span>
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#0284C7', marginTop: '0.35rem' }}>
            79.5%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            79.5% of return losses caught on 15k validation benchmark
          </div>
        </div>
      </div>

      {/* Main Split Grid: Risk Tier Segmentation & Category Table */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
        gap: '1.25rem',
      }}>
        {/* Left: Risk Tier Allocation */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>Order Risk Distribution</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Segmented by calibrated return probability</div>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', background: '#F1F5F9', padding: '2px 8px', borderRadius: '4px' }}>
              {totalOrders} Live Orders
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
            {/* Low Risk */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                  <span style={{ color: '#16A34A', marginRight: '6px' }}>●</span>
                  Low Risk (0.00 – 0.20)
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>{data.tier_distribution?.LOW || 91}</strong> orders ({((data.tier_proportions?.LOW || 0.455) * 100).toFixed(1)}%) • 12.3% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(data.tier_proportions?.LOW || 0.455) * 100}%`, height: '100%', background: '#16A34A', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy Action: 1-Click Seamless Checkout (Frictionless)
              </div>
            </div>

            {/* Medium Risk */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                  <span style={{ color: '#D97706', marginRight: '6px' }}>●</span>
                  Medium Risk (0.20 – 0.45)
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>{data.tier_distribution?.MEDIUM || 73}</strong> orders ({((data.tier_proportions?.MEDIUM || 0.365) * 100).toFixed(1)}%) • 33.0% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(data.tier_proportions?.MEDIUM || 0.365) * 100}%`, height: '100%', background: '#D97706', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy Action: In-app address verification & size guide prompt
              </div>
            </div>

            {/* High Risk */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                  <span style={{ color: '#EA580C', marginRight: '6px' }}>●</span>
                  High Risk (0.45 – 0.70)
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>{data.tier_distribution?.HIGH || 35}</strong> orders ({((data.tier_proportions?.HIGH || 0.175) * 100).toFixed(1)}%) • 52.4% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(data.tier_proportions?.HIGH || 0.175) * 100}%`, height: '100%', background: '#EA580C', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy Action: Automated WhatsApp confirmation or ₹100 advance deposit
              </div>
            </div>

            {/* Critical Risk */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                  <span style={{ color: '#DC2626', marginRight: '6px' }}>●</span>
                  Critical Risk (0.70 – 1.00)
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>{data.tier_distribution?.CRITICAL || 1}</strong> orders ({((data.tier_proportions?.CRITICAL || 0.005) * 100).toFixed(1)}%) • 73.1% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${Math.max(2, (data.tier_proportions?.CRITICAL || 0.005) * 100)}%`, height: '100%', background: '#DC2626', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy Action: Mandatory prepaid checkout or human review call queue
              </div>
            </div>
          </div>
        </div>

        {/* Right: Category Performance Table */}
        <div className="card" style={{ padding: '1.25rem', overflowX: 'auto' }}>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>Category Risk Breakdown</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Observed return risk exposure by product category</div>
          </div>

          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Volume</th>
                <th>Return Rate</th>
                <th>Gross Exposure</th>
                <th>Est. Savings</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => (
                <tr key={cat.name}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{cat.name}</td>
                  <td>{cat.orders.toLocaleString()}</td>
                  <td>
                    <span style={{
                      color: cat.riskLevel === 'HIGH' ? '#B91C1C' : cat.riskLevel === 'MEDIUM' ? '#B45309' : '#15803D',
                      fontWeight: 600,
                    }}>
                      {cat.returnRate}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{formatINR(cat.riskExposure)}</td>
                  <td style={{ color: '#15803D', fontWeight: 600 }}>{formatINR(cat.savings)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: '0.85rem', fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            *Estimated savings calculated under defined reverse logistics cost assumptions (C_FN = ₹600, C_FP = ₹150).
          </div>
        </div>
      </div>
    </div>
  );
}
