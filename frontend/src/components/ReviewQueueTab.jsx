import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle2, PhoneCall, MessageSquare, DollarSign, XCircle, Clock, UserCheck, AlertOctagon } from 'lucide-react';
import { fetchReviewQueue, submitReviewDecision } from '../api';

const MOCK_REVIEW_QUEUE = [
  {
    order_id: "ORD-928104",
    customer_id: "CUST-4192",
    product_id: "PROD-FASH-102",
    order_value: 8499.0,
    product_category: "Footwear",
    payment_method: "COD",
    created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    risk_score: 64.8,
    predicted_return_probability: 0.648,
    risk_tier: "HIGH",
    recommended_action: "REQUIRE_PREPAID_OR_DEPOSIT",
    recommended_action_name: "Require Rs. 100 Deposit or UPI",
    gross_return_loss_inr: 1675.0,
    expected_net_savings_inr: 340.0,
    plain_language_summary: "High risk COD footwear order with 3.1x basket deviation.",
    top_risk_factors: [
      { feature_display_name: "Customer Historical Return Rate", raw_value: "58%", human_readable_reason: "Customer account has elevated historical return frequency (58% of prior purchases)." },
      { feature_display_name: "Payment Method", raw_value: "COD", human_readable_reason: "Cash on Delivery (COD) orders exhibit lower delivery acceptance commitment." }
    ],
    review_status: "PENDING",
  },
  {
    order_id: "ORD-928105",
    customer_id: "CUST-8812",
    product_id: "PROD-ELEC-409",
    order_value: 14500.0,
    product_category: "Electronics",
    payment_method: "COD",
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    risk_score: 74.2,
    predicted_return_probability: 0.742,
    risk_tier: "CRITICAL",
    recommended_action: "MANUAL_REVIEW_CALL",
    recommended_action_name: "Manual Review Queue & Support Call",
    gross_return_loss_inr: 2140.0,
    expected_net_savings_inr: 680.0,
    plain_language_summary: "Critical risk high-value electronics COD purchase.",
    top_risk_factors: [
      { feature_display_name: "Order Basket Deviation", raw_value: "3.8x", human_readable_reason: "Order value is 3.8x higher than customer's historical average order." },
      { feature_display_name: "Customer Account Longevity", raw_value: "3 days", human_readable_reason: "Recently created account (3 days active)." }
    ],
    review_status: "PENDING",
  }
];

export default function ReviewQueueTab() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("PENDING");
  const [selectedNotes, setSelectedNotes] = useState({});
  const [actionSuccess, setActionSuccess] = useState(null);

  const loadQueue = async () => {
    setLoading(true);
    try {
      const data = await fetchReviewQueue(statusFilter);
      if (data.queue && data.queue.length > 0) {
        setQueue(data.queue);
      } else {
        setQueue(MOCK_REVIEW_QUEUE);
      }
    } catch (err) {
      console.warn("Using fallback queue data:", err);
      setQueue(MOCK_REVIEW_QUEUE);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, [statusFilter]);

  const handleDecision = async (orderId, decision) => {
    const notes = selectedNotes[orderId] || "";
    try {
      await submitReviewDecision(orderId, decision, notes, "merchant_lead");
      setActionSuccess(`Order ${orderId} decision '${decision}' successfully recorded & logged.`);
      
      // Update local state
      setQueue(prev => prev.map(item => {
        if (item.order_id === orderId) {
          return { ...item, review_status: "REVIEWED", review_decision: decision, review_notes: notes };
        }
        return item;
      }));

      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err) {
      console.warn("Backend decision recording offline, updating locally:", err);
      setActionSuccess(`Order ${orderId} decision '${decision}' recorded (offline demo mode).`);
      setQueue(prev => prev.map(item => {
        if (item.order_id === orderId) {
          return { ...item, review_status: "REVIEWED", review_decision: decision, review_notes: notes };
        }
        return item;
      }));
      setTimeout(() => setActionSuccess(null), 4000);
    }
  };

  const formatINR = (val) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val || 0);

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header with Title & Filter Controls */}
      <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <ShieldAlert size={22} color="#F97316" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF' }}>
              Human-in-the-Loop Merchant Review Queue (Phase 15)
            </h3>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Flagged HIGH & CRITICAL orders awaiting manual verification or policy override
          </p>
        </div>

        {/* Status Filter Buttons */}
        <div style={{ display: 'flex', background: 'rgba(31, 41, 55, 0.6)', padding: '3px', borderRadius: '8px', gap: '4px' }}>
          {['PENDING', 'REVIEWED', 'ALL'].map((f) => (
            <button
              key={f}
              onClick={() => setStatusFilter(f)}
              style={{
                padding: '5px 12px',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.78rem',
                fontWeight: statusFilter === f ? 700 : 500,
                background: statusFilter === f ? 'var(--color-primary)' : 'transparent',
                color: statusFilter === f ? '#FFFFFF' : 'var(--text-secondary)',
                cursor: 'pointer',
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Success Notification Alert */}
      {actionSuccess && (
        <div style={{
          padding: '10px 16px',
          borderRadius: '8px',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#10B981',
          fontSize: '0.85rem',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}>
          <CheckCircle2 size={18} />
          {actionSuccess}
        </div>
      )}

      {/* Review Queue Orders List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {queue.length === 0 ? (
          <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <CheckCircle2 size={40} color="#10B981" style={{ margin: '0 auto 0.75rem' }} />
            <h4 style={{ color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700 }}>Review Queue Clear</h4>
            <p style={{ fontSize: '0.85rem', marginTop: '4px' }}>No high-risk orders currently pending review.</p>
          </div>
        ) : (
          queue.map((item) => (
            <div
              key={item.order_id}
              className="glass-panel"
              style={{
                padding: '1.25rem',
                borderLeft: `4px solid ${item.risk_tier === 'CRITICAL' ? '#EF4444' : '#F97316'}`,
              }}
            >
              {/* Order Meta Bar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ fontWeight: 800, fontSize: '1rem', color: '#FFFFFF' }}>{item.order_id}</span>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      background: item.risk_tier === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(249, 115, 22, 0.2)',
                      color: item.risk_tier === 'CRITICAL' ? '#EF4444' : '#F97316',
                    }}>
                      {item.risk_tier} RISK ({((item.predicted_return_probability || 0.6) * 100).toFixed(1)}%)
                    </span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      Customer: {item.customer_id}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    <span>Category: <strong style={{ color: 'var(--text-primary)' }}>{item.product_category}</strong></span>
                    <span>Payment: <strong style={{ color: 'var(--text-primary)' }}>{item.payment_method}</strong></span>
                    <span>Order Value: <strong style={{ color: '#FFFFFF' }}>{formatINR(item.order_value)}</strong></span>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>EXPOSURE / ROI</span>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#EF4444' }}>
                    Loss Exp: {formatINR(item.gross_return_loss_inr)}
                  </div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#10B981' }}>
                    Net Save: {formatINR(item.expected_net_savings_inr)}
                  </div>
                </div>
              </div>

              {/* Rationale & Explainability */}
              <div style={{
                marginTop: '0.75rem',
                padding: '0.75rem',
                borderRadius: '6px',
                background: 'rgba(31, 41, 55, 0.4)',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.8rem',
              }}>
                <div style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>
                  💡 <strong>Automated Recommendation:</strong> {item.recommended_action_name}
                </div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.76rem' }}>
                  {item.plain_language_summary}
                </div>
              </div>

              {/* Action Decision Controls */}
              {item.review_status === "PENDING" ? (
                <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  <input
                    type="text"
                    placeholder="Merchant review notes (optional)..."
                    value={selectedNotes[item.order_id] || ""}
                    onChange={(e) => setSelectedNotes({ ...selectedNotes, [item.order_id]: e.target.value })}
                    style={{
                      padding: '7px 12px',
                      borderRadius: '6px',
                      background: 'var(--bg-surface)',
                      border: '1px solid var(--border-subtle)',
                      color: '#FFFFFF',
                      fontSize: '0.8rem',
                    }}
                  />

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <button
                      onClick={() => handleDecision(item.order_id, "APPROVED_SEAMLESS")}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        background: 'rgba(16, 185, 129, 0.15)',
                        border: '1px solid rgba(16, 185, 129, 0.4)',
                        color: '#10B981',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <CheckCircle2 size={14} /> Approve (1-Click)
                    </button>

                    <button
                      onClick={() => handleDecision(item.order_id, "WHATSAPP_CONFIRMATION")}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        background: 'rgba(51, 149, 255, 0.15)',
                        border: '1px solid rgba(51, 149, 255, 0.4)',
                        color: '#3395FF',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <MessageSquare size={14} /> Send WhatsApp Verify
                    </button>

                    <button
                      onClick={() => handleDecision(item.order_id, "REQUIRE_PREPAID_OR_DEPOSIT")}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        background: 'rgba(245, 158, 11, 0.15)',
                        border: '1px solid rgba(245, 158, 11, 0.4)',
                        color: '#F59E0B',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <DollarSign size={14} /> Require ₹100 Deposit
                    </button>

                    <button
                      onClick={() => handleDecision(item.order_id, "MANUAL_CALL_CANCEL")}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        background: 'rgba(239, 68, 68, 0.15)',
                        border: '1px solid rgba(239, 68, 68, 0.4)',
                        color: '#EF4444',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <XCircle size={14} /> Cancel / Support Call
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{
                  marginTop: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  fontSize: '0.8rem',
                  color: '#10B981',
                }}>
                  <UserCheck size={16} />
                  <span>
                    Reviewed: <strong>{item.review_decision}</strong> {item.review_notes ? `— "${item.review_notes}"` : ''}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
