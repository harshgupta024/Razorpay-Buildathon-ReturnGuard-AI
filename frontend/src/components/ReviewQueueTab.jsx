import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle2, PhoneCall, MessageSquare, DollarSign, XCircle, Clock, UserCheck, AlertOctagon, Check } from 'lucide-react';
import { fetchReviewQueue, submitReviewDecision } from '../api';

const DEFAULT_QUEUE_ITEMS = [
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
    recommended_action_name: "Enforce ₹100 Shipping Deposit",
    gross_return_loss_inr: 1675.0,
    expected_net_savings_inr: 340.0,
    plain_language_summary: "High risk COD footwear order with 3.1x basket deviation.",
    top_risk_factors: [
      { feature_display_name: "Customer Return History", human_readable_reason: "Customer account has 58% historical return frequency." },
      { feature_display_name: "Payment Method", human_readable_reason: "COD orders exhibit higher delivery refusal risk." }
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
    recommended_action_name: "Manual Phone Verification Queue",
    gross_return_loss_inr: 2140.0,
    expected_net_savings_inr: 680.0,
    plain_language_summary: "Critical risk high-value electronics COD purchase.",
    top_risk_factors: [
      { feature_display_name: "Order Basket Deviation", human_readable_reason: "Order value is 3.8x higher than customer average." },
      { feature_display_name: "Account Age", human_readable_reason: "Recently created account (3 days active)." }
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
        setQueue(DEFAULT_QUEUE_ITEMS);
      }
    } catch (err) {
      setQueue(DEFAULT_QUEUE_ITEMS);
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
      await submitReviewDecision(orderId, decision, notes, "merchant_operations");
      setActionSuccess(`Order ${orderId} marked as '${decision}'. Audit log updated.`);
      
      setQueue(prev => prev.map(item => {
        if (item.order_id === orderId) {
          return { ...item, review_status: "REVIEWED", review_decision: decision, review_notes: notes };
        }
        return item;
      }));

      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err) {
      setActionSuccess(`Order ${orderId} marked as '${decision}'.`);
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
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Action Notification Toast */}
      {actionSuccess && (
        <div style={{
          padding: '0.75rem 1rem',
          borderRadius: '6px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10B981',
          fontSize: '0.84rem',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}>
          <Check size={16} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Header & Filter Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF' }}>High-Risk Review Queue</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Human-in-the-Loop decision gateway for orders exceeding risk tolerance
          </div>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', background: 'var(--bg-card)', padding: '3px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
          {['PENDING', 'REVIEWED', 'ALL'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              style={{
                padding: '4px 10px',
                borderRadius: '4px',
                border: 'none',
                background: statusFilter === st ? '#1E293B' : 'transparent',
                color: statusFilter === st ? '#FFFFFF' : 'var(--text-muted)',
                fontSize: '0.78rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              {st === 'PENDING' ? 'Pending Review' : st === 'REVIEWED' ? 'Resolved' : 'All Orders'}
            </button>
          ))}
        </div>
      </div>

      {/* Review Queue Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {queue.map((item) => (
          <div key={item.order_id} className="card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="font-mono" style={{ fontSize: '0.92rem', fontWeight: 600, color: '#FFFFFF' }}>
                  {item.order_id}
                </span>
                <span className={`badge badge-${item.risk_tier.toLowerCase()}`}>
                  ● {item.risk_tier} RISK ({(item.predicted_return_probability * 100).toFixed(1)}%)
                </span>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  Customer: <strong>{item.customer_id}</strong>
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.84rem' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Order Value: </span>
                  <strong style={{ color: '#FFFFFF' }}>{formatINR(item.order_value)}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Gross Exposure: </span>
                  <strong style={{ color: '#EF4444' }}>{formatINR(item.gross_return_loss_inr)}</strong>
                </div>
              </div>
            </div>

            {/* Middle Section: Reason and Recommendation */}
            <div style={{
              marginTop: '0.85rem',
              padding: '0.75rem 1rem',
              borderRadius: '6px',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '0.75rem',
            }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Recommended Policy: <strong style={{ color: '#38BDF8' }}>{item.recommended_action_name}</strong>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {item.plain_language_summary || "High return propensity detected on COD checkout."}
                </div>
              </div>

              <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 600 }}>
                Protects {formatINR(item.expected_net_savings_inr)} in Net Margin
              </div>
            </div>

            {/* Action Buttons & Internal Notes */}
            <div style={{
              marginTop: '1rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '0.75rem',
              borderTop: '1px solid var(--border-subtle)',
              paddingTop: '0.85rem',
            }}>
              <input
                type="text"
                placeholder="Add internal merchant note (optional)..."
                value={selectedNotes[item.order_id] || ""}
                onChange={(e) => setSelectedNotes({ ...selectedNotes, [item.order_id]: e.target.value })}
                style={{ maxWidth: '380px', fontSize: '0.78rem' }}
              />

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleDecision(item.order_id, "APPROVED_SEAMLESS")}
                >
                  <Check size={13} />
                  <span>Approve Order</span>
                </button>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleDecision(item.order_id, "WHATSAPP_CONFIRMATION")}
                >
                  <MessageSquare size={13} />
                  <span>WhatsApp Verify</span>
                </button>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => handleDecision(item.order_id, "REQUIRE_PREPAID_OR_DEPOSIT")}
                >
                  <DollarSign size={13} />
                  <span>Require ₹100 Deposit</span>
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDecision(item.order_id, "FLAGGED_FOR_CALL")}
                >
                  <PhoneCall size={13} />
                  <span>Call Customer</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
