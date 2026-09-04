# ReturnGuard AI — 3-Minute Live Demo Video Script
**Razorpay Buildathon 2026 Submission**

---

### [0:00 – 0:40] Introduction & The Problem
> **[Visual: Camera / Title Slide: ReturnGuard AI — Razorpay Buildathon 2026]**  
> *"Hello judges! In Indian e-commerce, product returns are silent margin killers. Return rates across fashion, footwear, and electronics frequently reach 25% to 35%, costing merchants ₹500 to ₹1,200 for every single return in reverse logistics and inventory depreciation.*  
> *Today, merchants either do nothing and lose lakhs, or blindly reject orders and destroy customer trust.  
> We built **ReturnGuard AI** — an end-to-end, pre-fulfillment return risk intelligence and cost-aware decision engine that turns return losses into net merchant profit."*

---

### [0:40 – 1:20] Overview Command Center Dashboard
> **[Visual: Switch to Browser at `http://127.0.0.1:5173` showing Overview Tab]**  
> *"Here is the ReturnGuard AI Merchant Command Center.  
> You see our live ingested merchant portfolio operating alongside our 15,000-order locked test benchmark.*  
> *1. Our baseline portfolio return propensity is **27.1%**, perfectly matching India's e-commerce baseline.*  
> *2. By optimizing for asymmetric business cost — where missing a return is 4 times more costly than verification friction ($C_{FN}=\text{₹600}, C_{FP}=\text{₹150}$) — we operate at the cost-optimal threshold of **0.20**.*  
> *3. Under these defined reverse logistics cost assumptions, this achieves a **79.5% return recall rate**, delivering an estimated **₹11.92 Lakhs in net profit protection** across our 15,000 benchmark cohort—saving **₹79.46 per order**!*  
> *4. Our multi-tier risk spectrum segments orders into 4 actionable buckets: 45.5% Low Risk, 36.4% Medium Risk, 17.9% High Risk, and 0.2% Critical Risk.*  
> *Merchants can dynamically toggle policy modes between Conservative, Balanced, and Aggressive margin defense."*

---

### [1:20 – 2:15] Interactive Order Risk Inspector & Explainability
> **[Visual: Click on 'Risk Inspector' in the left sidebar]**  
> *"Let's test an order in real time.  
> First, let's select a **Safe UPI Purchase** (repeat customer, ₹1,850 Books).  
> In just **0.002 milliseconds of model compute**, the engine predicts **8.4% return likelihood**, assigns **LOW RISK**, and consistently recommends **1-Click Seamless Checkout** with zero added friction.*  
> *Now, let's switch to a **High-Risk COD Footwear Order** with 60% customer return history and a 3.2x cart spike.  
> Instantly, the engine flags **49.7% return risk**, assigns **HIGH RISK**, and recommends **'Enforce ₹100 Advance Shipping Deposit'**, protecting **₹575 in estimated net margin** on this single order!*  
> *Look at our **Responsible AI Explainability breakdown**: Instead of accusatory terms like 'fraud' or 'scammer', ReturnGuard generates objective, mathematical signals: customer historical return frequency and cart size deviation."*

---

### [2:15 – 2:45] Human-in-the-Loop Review Queue & Orders Ledger
> **[Visual: Click on 'Review Queue' showing [2] pending items, then 'Orders Ledger']**  
> *"High-stakes orders are never blocked blindly. They route directly to this **Human-in-the-Loop Review Queue**.*  
> *The merchant sees the full risk context and can take 1-click action: **'Approve Order'**, **'Send WhatsApp Verification'**, or **'Collect ₹100 Deposit'** with custom review notes.  
> Every single decision is permanently recorded in our immutable audit trail.*  
> *In the **Orders Ledger**, merchants get a real-time, searchable ledger of all historical orders with return probabilities, risk tiers, and one-click detailed slide-overs."*

---

### [2:45 – 3:00] Architecture, Performance & Closing
> **[Visual: Return to Overview Tab / Closing Slide]**  
> *"Under the hood, ReturnGuard AI delivers **0.002 ms pure model compute**, total end-to-end API response under **5 milliseconds**, 100% zero-leakage data integrity, and **146 / 146 automated tests passing**.*  
> *Designed for seamless **Razorpay Magic Checkout** integration, ReturnGuard AI empowers D2C brands to protect margins and deliver frictionless customer experiences.  
> Thank you!"*
