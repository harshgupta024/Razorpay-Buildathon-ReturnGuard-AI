import React, { useState, useEffect } from 'react';
import { Search, Filter, RefreshCw, ExternalLink } from 'lucide-react';
import { fetchOrders } from '../api';

const MOCK_ORDERS = [
  { order_id: "ORD-066174", customer_id: "CUST-02233", product_category: "Sports", payment_method: "UPI", order_value: 4175.0, assessment: { risk_score: 8.4, risk_tier: "LOW", recommended_action_name: "1-Click Seamless Checkout", expected_net_savings_inr: 0.0 } },
  { order_id: "ORD-091823", customer_id: "CUST-01452", product_category: "Clothing", payment_method: "COD", order_value: 2999.0, assessment: { risk_score: 34.2, risk_tier: "MEDIUM", recommended_action_name: "Address Verification", expected_net_savings_inr: 45.0 } },
  { order_id: "ORD-041890", customer_id: "CUST-08819", product_category: "Footwear", payment_method: "COD", order_value: 7500.0, assessment: { risk_score: 58.1, risk_tier: "HIGH", recommended_action_name: "WhatsApp Confirmation", expected_net_savings_inr: 210.0 } },
  { order_id: "ORD-012903", customer_id: "CUST-00912", product_category: "Electronics", payment_method: "Credit Card", order_value: 12000.0, assessment: { risk_score: 14.5, risk_tier: "LOW", recommended_action_name: "1-Click Seamless Checkout", expected_net_savings_inr: 0.0 } },
  { order_id: "ORD-077391", customer_id: "CUST-04419", product_category: "Clothing", payment_method: "COD", order_value: 9200.0, assessment: { risk_score: 72.8, risk_tier: "CRITICAL", recommended_action_name: "Require Rs. 100 Deposit", expected_net_savings_inr: 450.0 } },
];

export default function OrdersFeedTab() {
  const [orders, setOrders] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [tierFilter, setTierFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await fetchOrders(tierFilter === "ALL" ? null : tierFilter, 100, 0);
      if (data.orders && data.orders.length > 0) {
        setOrders(data.orders);
      } else {
        setOrders(MOCK_ORDERS);
      }
    } catch (err) {
      console.warn("Using fallback orders feed:", err);
      setOrders(MOCK_ORDERS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [tierFilter]);

  const filteredOrders = orders.filter((o) => {
    const term = searchTerm.toLowerCase();
    return (
      o.order_id.toLowerCase().includes(term) ||
      o.customer_id.toLowerCase().includes(term) ||
      o.product_category.toLowerCase().includes(term) ||
      o.payment_method.toLowerCase().includes(term)
    );
  });

  const formatINR = (val) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val || 0);

  const getTierColor = (tier) => {
    switch (tier) {
      case 'LOW': return { text: '#10B981', bg: 'rgba(16, 185, 129, 0.12)' };
      case 'MEDIUM': return { text: '#F59E0B', bg: 'rgba(245, 158, 11, 0.12)' };
      case 'HIGH': return { text: '#F97316', bg: 'rgba(249, 115, 22, 0.12)' };
      default: return { text: '#EF4444', bg: 'rgba(239, 68, 68, 0.12)' };
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Controls Bar */}
      <div className="glass-panel" style={{ padding: '1rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-surface)', padding: '6px 12px', borderRadius: '8px', border: '1px solid var(--border-subtle)', minWidth: '280px' }}>
          <Search size={16} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search by Order ID, Customer, Category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#FFFFFF', fontSize: '0.82rem', outline: 'none', width: '100%' }}
          />
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <Filter size={14} />
            <span>Tier:</span>
            <select
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value)}
              style={{ background: '#1F2937', color: '#FFFFFF', border: '1px solid var(--border-subtle)', padding: '4px 8px', borderRadius: '6px', fontSize: '0.78rem' }}
            >
              <option value="ALL">All Tiers</option>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="CRITICAL">Critical Risk</option>
            </select>
          </div>

          <button
            onClick={loadOrders}
            style={{ padding: '6px 10px', borderRadius: '6px', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#3B82F6', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem' }}
          >
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
      </div>

      {/* Orders Table */}
      <div className="glass-panel" style={{ padding: '1rem', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-medium)', textAlign: 'left', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '10px 12px' }}>Order ID</th>
              <th style={{ padding: '10px 12px' }}>Customer ID</th>
              <th style={{ padding: '10px 12px' }}>Category</th>
              <th style={{ padding: '10px 12px' }}>Payment</th>
              <th style={{ padding: '10px 12px' }}>Order Value</th>
              <th style={{ padding: '10px 12px' }}>Risk Score</th>
              <th style={{ padding: '10px 12px' }}>Tier</th>
              <th style={{ padding: '10px 12px' }}>Recommended Policy</th>
              <th style={{ padding: '10px 12px' }}>Net Savings</th>
            </tr>
          </thead>
          <tbody>
            {filteredOrders.map((o, idx) => {
              const tier = o.assessment?.risk_tier || 'LOW';
              const colors = getTierColor(tier);
              return (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)', background: idx % 2 === 0 ? 'rgba(255, 255, 255, 0.01)' : 'transparent' }}>
                  <td style={{ padding: '10px 12px', fontWeight: 700, color: '#FFFFFF' }}>{o.order_id}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>{o.customer_id}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--text-primary)' }}>{o.product_category}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>{o.payment_method}</td>
                  <td style={{ padding: '10px 12px', fontWeight: 600, color: '#FFFFFF' }}>{formatINR(o.order_value)}</td>
                  <td style={{ padding: '10px 12px', fontWeight: 700, color: colors.text }}>
                    {o.assessment?.risk_score?.toFixed(1) || '0.0'}
                  </td>
                  <td style={{ padding: '10px 12px' }}>
                    <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700, background: colors.bg, color: colors.text }}>
                      {tier}
                    </span>
                  </td>
                  <td style={{ padding: '10px 12px', color: 'var(--text-secondary)', fontSize: '0.78rem' }}>
                    {o.assessment?.recommended_action_name || '1-Click Seamless Checkout'}
                  </td>
                  <td style={{ padding: '10px 12px', fontWeight: 700, color: '#10B981' }}>
                    {formatINR(o.assessment?.expected_net_savings_inr || 0)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
