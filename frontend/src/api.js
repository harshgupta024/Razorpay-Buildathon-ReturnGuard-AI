/**
 * ReturnGuard AI — API Client
 */

const API_BASE_URL = "http://localhost:8000/api/v1";

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return await res.json();
  } catch (err) {
    return { status: "offline", error: err.message };
  }
}

export async function fetchAnalyticsSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/summary`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("Using fallback analytics data:", err);
    return {
      total_orders_analyzed: 15000,
      total_portfolio_value_inr: 42500000.0,
      total_unmitigated_risk_exposure_inr: 2439000.0,
      total_projected_net_savings_inr: 1191900.0,
      portfolio_avg_return_probability: 0.271,
      tier_distribution: { LOW: 6829, MEDIUM: 5462, HIGH: 2684, CRITICAL: 26 },
      tier_proportions: { LOW: 0.4552, MEDIUM: 0.3641, HIGH: 0.1789, CRITICAL: 0.0017 },
      category_breakdown: [
        { category: "Clothing", order_count: 3820, avg_return_risk: 0.365, projected_savings_inr: 412000.0 },
        { category: "Footwear", order_count: 2750, avg_return_risk: 0.342, projected_savings_inr: 320000.0 },
        { category: "Electronics", order_count: 2410, avg_return_risk: 0.210, projected_savings_inr: 185000.0 },
        { category: "Beauty", order_count: 1890, avg_return_risk: 0.285, projected_savings_inr: 145000.0 },
        { category: "Home", order_count: 1620, avg_return_risk: 0.198, projected_savings_inr: 89000.0 },
        { category: "Sports", order_count: 1210, avg_return_risk: 0.180, projected_savings_inr: 40900.0 },
      ],
      recommended_actions_breakdown: {
        ALLOW_SEAMLESS: 6829,
        SOFT_CONFIRMATION: 4100,
        WHATSAPP_CONFIRMATION: 3000,
        REQUIRE_PREPAID_OR_DEPOSIT: 1045,
        MANUAL_REVIEW_CALL: 26,
      },
    };
  }
}

export async function scoreSingleOrder(orderPayload) {
  try {
    const res = await fetch(`${API_BASE_URL}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(orderPayload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("Backend score endpoint unreachable:", err);
    throw err;
  }
}

export async function fetchOrders(tier = null, limit = 50, offset = 0) {
  try {
    let url = `${API_BASE_URL}/orders?limit=${limit}&offset=${offset}`;
    if (tier) url += `&tier=${tier}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { total_count: 0, orders: [] };
  }
}

export async function fetchOrderDetail(orderId) {
  try {
    const res = await fetch(`${API_BASE_URL}/orders/${orderId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    throw err;
  }
}

export async function fetchReviewQueue(statusFilter = "PENDING") {
  try {
    const res = await fetch(`${API_BASE_URL}/review/queue?status_filter=${statusFilter}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { total_queue_count: 0, queue: [] };
  }
}

export async function submitReviewDecision(orderId, decision, notes = "", reviewerId = "merchant_admin") {
  const res = await fetch(`${API_BASE_URL}/review/${orderId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, notes, reviewer_id: reviewerId }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function fetchThresholdConfig() {
  try {
    const res = await fetch(`${API_BASE_URL}/config/thresholds`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      active_preset: "Balanced (Default Cost-Optimal)",
      active_cutoffs: { low: 0.20, medium: 0.45, high: 0.70 },
      available_presets: {},
    };
  }
}

export async function updateThresholdPreset(presetName) {
  const res = await fetch(`${API_BASE_URL}/config/thresholds`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset_name: presetName }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}
