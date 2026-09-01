import React, { useState, useEffect } from 'react';
import { Search, Filter, RefreshCw, X, ArrowUpRight, ShieldCheck, Clock } from 'lucide-react';
import { fetchOrders, fetchOrderDetail } from '../api';

const DEFAULT_ORDERS = [
  { order_id: "ORD-066174", customer_id: "CUST-02233", product_category: "Books", payment_method: "UPI", order_value: 1850.0, assessment: { predicted_return_probability: 0.084, risk_tier: "LOW", recommended_action_name: "1-Click Seamless Checkout", expected_net_savings_inr: 0.0 } },
  { order_id: "ORD-091823", customer_id: "CUST-01452", product_category: "Clothing", payment_method: "COD", order_value: 3600.0, assessment: { predicted_return_probability: 0.324, risk_tier: "MEDIUM", recommended_action_name: "In-App Address Verification", expected_net_savings_inr: 45.0 } },
  { order_id: "ORD-041890", customer_id: "CUST-08819", product_category: "Footwear", payment_method: "COD", order_value: 8900.0, assessment: { predicted_return_probability: 0.581, risk_tier: "HIGH", recommended_action_name: "Require ₹100 Shipping Deposit", expected_net_savings_inr: 575.0 } },
  { order_id: "ORD-012903", customer_id: "CUST-00912", product_category: "Electronics", payment_method: "Credit Card", order_value: 12000.0, assessment: { predicted_return_probability: 0.145, risk_tier: "LOW", recommended_action_name: "1-Click Seamless Checkout", expected_net_savings_inr: 0.0 } },
  { order_id: "ORD-077391", customer_id: "CUST-04419", product_category: "Electronics", payment_method: "COD", order_value: 14500.0, assessment: { predicted_return_probability: 0.742, risk_tier: "CRITICAL", recommended_action_name: "Prepaid Only / Support Call", expected_net_savings_inr: 680.0 } },
];

export default function OrdersFeedTab() {
  const [orders, setOrders] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [tierFilter, setTierFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await fetchOrders(tierFilter === "ALL" ? null : tierFilter, 100, 0);
      if (data.orders && data.orders.length > 0) {
        setOrders(data.orders);
      } else {
        setOrders(DEFAULT_ORDERS);
      }
    } catch (err) {
      setOrders(DEFAULT_ORDERS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [tierFilter]);

  const handleRowClick = async (order) => {
    try {
      const detail = await fetchOrderDetail(order.order_id);
      setSelectedOrder(detail);
    } catch (err) {
      setSelectedOrder(order);
    }
  };

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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Controls Bar */}
      <div className="card" style={{ padding: '0.85rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.85rem' }}>
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-app)', padding: '5px 10px', borderRadius: '6px', border: '1px solid var(--border-subtle)', minWidth: '300px' }}>
          <Search size={14} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Filter by Order ID, Customer, Category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#FFFFFF', fontSize: '0.82rem', padding: 0 }}
          />
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span>Filter Tier:</span>
            <select
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value)}
              style={{ padding: '3px 8px', fontSize: '0.78rem', width: 'auto' }}
            >
              <option value="ALL">All Tiers</option>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="CRITICAL">Critical Risk</option>
            </select>
          </div>

          <button className="btn btn-secondary btn-sm" onClick={loadOrders}>
            <RefreshCw size={12} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Main Table Ledger */}
      <div className="card" style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Category</th>
              <th>Payment</th>
              <th>Order Value</th>
              <th>Return Probability</th>
              <th>Risk Tier</th>
              <th>Recommended Policy</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredOrders.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  No matching orders found.
                </td>
              </tr>
            ) : (
              filteredOrders.map((o) => {
                const tier = o.assessment?.risk_tier || 'LOW';
                const prob = o.assessment?.predicted_return_probability || 0;
                return (
                  <tr key={o.order_id} style={{ cursor: 'pointer' }} onClick={() => handleRowClick(o)}>
                    <td className="font-mono" style={{ fontWeight: 600, color: '#38BDF8' }}>
                      {o.order_id}
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{o.customer_id}</td>
                    <td>{o.product_category}</td>
                    <td>
                      <span style={{
                        fontSize: '0.75rem',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        background: o.payment_method === 'COD' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(37, 99, 235, 0.1)',
                        color: o.payment_method === 'COD' ? '#F87171' : '#60A5FA',
                        fontWeight: 500,
                      }}>
                        {o.payment_method}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{formatINR(o.order_value)}</td>
                    <td className="font-mono">{(prob * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`badge badge-${tier.toLowerCase()}`}>
                        ● {tier}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      {o.assessment?.recommended_action_name || "1-Click Seamless Checkout"}
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm" style={{ padding: '2px 8px', fontSize: '0.72rem' }}>
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Order Detail Modal / Slide-over */}
      {selectedOrder && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: '100%',
          maxWidth: '460px',
          background: 'var(--bg-card)',
          borderLeft: '1px solid var(--border-default)',
          zIndex: 100,
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.7)',
          overflowY: 'auto',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Transaction Record</div>
              <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF' }}>
                {selectedOrder.order_id}
              </div>
            </div>
            <button
              onClick={() => setSelectedOrder(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={18} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.84rem' }}>
            <div className="card-subtle" style={{ padding: '1rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Evaluation Assessment
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.4rem' }}>
                <span className={`badge badge-${(selectedOrder.assessment?.risk_tier || 'LOW').toLowerCase()}`}>
                  ● {selectedOrder.assessment?.risk_tier || 'LOW'} RISK
                </span>
                <span className="font-mono" style={{ color: '#FFFFFF', fontWeight: 600 }}>
                  {((selectedOrder.assessment?.predicted_return_probability || 0) * 100).toFixed(1)}% Return Propensity
                </span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Policy: <strong>{selectedOrder.assessment?.recommended_action_name || '1-Click Checkout'}</strong>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="card-subtle" style={{ padding: '0.75rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Customer ID</div>
                <div style={{ fontWeight: 600, marginTop: '2px' }}>{selectedOrder.customer_id}</div>
              </div>
              <div className="card-subtle" style={{ padding: '0.75rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Order Value</div>
                <div style={{ fontWeight: 600, marginTop: '2px' }}>{formatINR(selectedOrder.order_value)}</div>
              </div>
              <div className="card-subtle" style={{ padding: '0.75rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Category</div>
                <div style={{ fontWeight: 600, marginTop: '2px' }}>{selectedOrder.product_category}</div>
              </div>
              <div className="card-subtle" style={{ padding: '0.75rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Payment Method</div>
                <div style={{ fontWeight: 600, marginTop: '2px' }}>{selectedOrder.payment_method}</div>
              </div>
            </div>

            {selectedOrder.assessment?.action_rationale && (
              <div className="card-subtle" style={{ padding: '0.85rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Decision Rationale
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  {selectedOrder.assessment.action_rationale}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
