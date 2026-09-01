import React from 'react';
import { ArrowUpRight, TrendingUp, ShieldCheck, AlertCircle, CheckCircle, BarChart3, Clock, DollarSign, Package } from 'lucide-react';

export default function OverviewTab({ analyticsData }) {
  const data = analyticsData || {
    total_orders_analyzed: 15000,
    total_portfolio_value_inr: 42500000.0,
    total_unmitigated_risk_exposure_inr: 2439000.0,
    total_projected_net_savings_inr: 1191900.0,
    portfolio_avg_return_probability: 0.271,
    tier_distribution: { LOW: 6829, MEDIUM: 5462, HIGH: 2684, CRITICAL: 26 },
    tier_proportions: { LOW: 0.4552, MEDIUM: 0.3641, HIGH: 0.1789, CRITICAL: 0.0017 },
  };

  const formatINR = (val) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

  const categories = [
    { name: 'Clothing', orders: 4850, returnRate: '34.2%', riskExposure: 924000, savings: 488000, riskLevel: 'HIGH' },
    { name: 'Footwear', orders: 3620, returnRate: '32.8%', riskExposure: 785000, savings: 395000, riskLevel: 'HIGH' },
    { name: 'Electronics', orders: 2410, returnRate: '19.5%', riskExposure: 412000, savings: 172000, riskLevel: 'MEDIUM' },
    { name: 'Beauty', orders: 1980, returnRate: '14.1%', riskExposure: 184000, savings: 78000, riskLevel: 'LOW' },
    { name: 'Home & Kitchen', orders: 1340, returnRate: '16.4%', riskExposure: 104000, savings: 44000, riskLevel: 'LOW' },
    { name: 'Books', orders: 800, returnRate: '8.9%', riskExposure: 30000, savings: 14900, riskLevel: 'LOW' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner: Status Notice */}
      <div className="card" style={{ padding: '0.85rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', background: '#F8FAFC', borderLeft: '4px solid #3395FF' }}>
        <div>
          <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Pre-Fulfillment Return Risk Engine Active
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            Operating at cost-optimal threshold <strong style={{ color: '#0C2340' }}>τ* = 0.20</strong> ($C_FN: ₹600, C_FP: ₹150$) • 15,000 orders evaluated
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className="badge badge-low">Zero Leakage</span>
          <span className="badge badge-low">Calibration ECE: 0.41%</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem',
      }}>
        {/* Metric 1 */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
            Total Orders Analyzed
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.35rem' }}>
            {data.total_orders_analyzed.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Portfolio GMV: <strong>{formatINR(data.total_portfolio_value_inr)}</strong>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
            Gross Return Risk Exposure
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#B91C1C', marginTop: '0.35rem' }}>
            {formatINR(data.total_unmitigated_risk_exposure_inr)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            27.1% baseline return rate across portfolio
          </div>
        </div>

        {/* Metric 3 */}
        <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #10B981' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#15803D' }}>
            Net Merchant Savings (ROI)
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#15803D', marginTop: '0.35rem' }}>
            {formatINR(data.total_projected_net_savings_inr)}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#15803D', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <TrendingUp size={13} />
            <span>₹{(data.total_projected_net_savings_inr / Math.max(1, data.total_orders_analyzed)).toFixed(1)} net savings per order</span>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
            Return Catch Rate (Recall)
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#0284C7', marginTop: '0.35rem' }}>
            79.5%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            3,232 of 4,065 returns intercepted pre-dispatch
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
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Portfolio segmented by calibrated return probability</div>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', background: '#F1F5F9', padding: '2px 8px', borderRadius: '4px' }}>15,000 Orders</span>
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
                  <strong>6,829</strong> orders (45.5%) • 12.3% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: '45.5%', height: '100%', background: '#16A34A', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy: 1-Click Seamless Checkout (Frictionless)
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
                  <strong>5,462</strong> orders (36.4%) • 33.0% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: '36.4%', height: '100%', background: '#D97706', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy: In-app address verification & size guide prompt
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
                  <strong>2,684</strong> orders (17.9%) • 52.4% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: '17.9%', height: '100%', background: '#EA580C', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy: Automated WhatsApp confirmation or ₹100 partial shipping deposit
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
                  <strong>26</strong> orders (0.2%) • 73.1% return rate
                </span>
              </div>
              <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: '2%', height: '100%', background: '#DC2626', borderRadius: '3px' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Policy: Mandatory prepaid checkout or human review call queue
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
                <th>Gross Loss</th>
                <th>Net Savings</th>
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
        </div>
      </div>
    </div>
  );
}
