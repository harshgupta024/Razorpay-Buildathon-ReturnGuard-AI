# ReturnGuard AI — Judge Pitch Deck & Presentation Architecture
**Razorpay Buildathon 2026 — Track 02 (E-Commerce Risk Intelligence)**

---

## Slide 1: Title & Hook
- **Headline:** ReturnGuard AI: Pre-Fulfillment Return Risk & Decision Intelligence for E-Commerce Merchants
- **Tagline:** Turning return loss into merchant profit with calibrated machine learning and cost-aware decision science.
- **Presenter:** Harsh Gupta

---

## Slide 2: The E-Commerce Crisis in India
- **The Context:** Indian D2C and e-commerce return rates average 25%–35%, with Cash on Delivery (COD) reaching up to 45%.
- **The Financial Bleed:** Every single return incurs forward logistics, reverse shipping, restocking inspection, box write-offs, and markdown depreciation (₹500–₹1,200 loss/return).
- **The Merchant Dilemma:**
  - *Accept All:* Lose ₹150+ per order in logistics waste.
  - *Naive Blocking:* Cancel orders blindly $\rightarrow$ high false positive rate $\rightarrow$ alienate loyal buyers and destroy GMV.

---

## Slide 3: The Innovation — Cost-Aware Machine Learning
- **Core Concept:** Standard ML optimizes for 0.50 accuracy or F1 score, ignoring asymmetric financial reality.
- **Mathematical Reality:** Missing a returned item ($C_{FN} = \text{₹600}$) is **4.0x more expensive** than customer verification friction ($C_{FP} = \text{₹150}$).
- **The Solution:** Exact cost-optimal threshold optimization ($\tau^* = 0.20$):
  - Intercepts **79.5% of all returns**.
  - Slashes return loss by **₹11.92 Lakhs per 15,000 orders** (saving **₹79.46 per order**).

---

## Slide 4: End-to-End Technical Architecture
- **Pipeline:** Preprocessing (36 features) $\rightarrow$ Champion `HistGradientBoosting` $\rightarrow$ 5-Fold Isotonic Probability Calibration (ECE: 0.41%) $\rightarrow$ Business Cost Engine $\rightarrow$ Ethical SHAP Explainer.
- **Serving Layer:** Production FastAPI REST API (< 5ms latency, > 15,000 orders/sec throughput).
- **Frontend Dashboard:** React 18 + Vite + Glassmorphic UI with real-time risk gauges, scenario simulator, and review queue.

---

## Slide 5: Actionable 4-Tier Risk System
- **🟢 LOW Risk (0.00 – 0.20):** 45.5% of orders (12.3% return rate) $\rightarrow$ 1-Click Seamless Checkout.
- **🟡 MEDIUM Risk (0.20 – 0.45):** 36.4% of orders (33.0% return rate) $\rightarrow$ In-app address validation popup & sizing reminder.
- **🟠 HIGH Risk (0.45 – 0.70):** 17.9% of orders (52.4% return rate) $\rightarrow$ Automated WhatsApp size confirmation or ₹100 deposit.
- **🔴 CRITICAL Risk (0.70 – 1.00):** 0.2% of orders (73.1% return rate) $\rightarrow$ Prepaid-only / dedicated merchant review queue.

---

## Slide 6: Responsible AI & Zero-Leakage Governance
- **Defensive & Non-Accusatory:** Zero usage of defamatory words (*"fraudster"*, *"abuser"*).
- **Sub-group Demographic Fairness:** Evaluated across customer segments with max ROC-AUC gap of only 0.0105.
- **Zero Post-Fulfillment Leakage:** Strictly pre-fulfillment signals only.
- **Human-in-the-Loop:** Complete merchant override workflow with immutable audit logs.

---

## Slide 7: Business ROI & Razorpay Integration Opportunity
- **Immediate Value:** A merchant doing 100,000 orders/month saves **₹79.5 Lakhs annually** in preventable return logistics.
- **Razorpay Magic Checkout Integration:** ReturnGuard AI can sit directly inside Razorpay's checkout SDK, dynamically enabling 1-click buy for low risk and prompting UPI prepayment incentives for elevated risk orders.
