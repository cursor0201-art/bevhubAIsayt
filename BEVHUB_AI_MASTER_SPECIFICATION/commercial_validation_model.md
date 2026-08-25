# BevHub AI: Financial Unit Economics & Pricing Model
**Phase 2.5 — Commercial Validation**

---

## 1. Core Cost Structure (Gross COGS vs. Net Operations)

To ensure the long-term profitability of BevHub AI, we distinguish between **Gross COGS** (direct generation, build compute, and container hosting) and **Net Operational Expenses** (payment gateway fees, storage, CDN bandwidth, customer support, and marketing).

### A. AI Generation Cost (Per Task)
Token consumption per average code generation task (15,000 input tokens, 4,000 output tokens):
*   **GPT-4o-mini:** **$0.0047** per step.
*   **GPT-4o:** **$0.0775** per step.
*   **Claude 3.5 Sonnet:** **$0.1050** per step.
*   **Blended Router** *(60% mini, 30% standard, 10% premium)*: **$0.0240** per step.

### B. Stripe Fees & Project Sync Overhead (Per Paid Subscription)
*   **Stripe Fees:** 2.9% + $0.30 of transaction volume (e.g., $1.72 on a $49.00 payment).
*   **Persistent Storage Sync & CDN Backups:** ~$0.08 per user / month.

### C. Monthly Infrastructure Container Overhead (Per Active Organization)
*   **Active Sandbox Containers:** $1.20 / user / month (runs on-demand with 15-minute idle auto-suspension).
*   **Database Sync (SQLite Cloud) & Logging Ingestion:** $0.30 / user / month.

---

## 2. Sensitivity Analysis: Three Financial Scenarios

Below we model three pricing and resource usage scenarios for the **Growth Plan ($49.00 / month)**:

| Parameter | Pessimistic | Base | Optimistic |
| :--- | :---: | :---: | :---: |
| **Free → Paid Conversion** | 2.0% | 5.0% | 10.0% |
| **Avg Token Consumption** | High (35k tokens) | Medium (19k tokens) | Low (10k tokens) |
| **Avg Cost / Gen (LLM)** | $0.150 (Claude-only) | $0.024 (Blended Router) | $0.005 (GPT-4o-mini-only) |
| **Generations / Mo / User** | 120 generations | 80 generations | 50 generations |
| **Avg Sandbox Cost / User / Mo**| $3.00 | $1.20 | $0.80 |
| **Stripe Fees + CDN Sync** | $2.50 | $1.80 | $1.60 |
| **Total Monthly COGS / User** | **$23.50** | **$4.92** | **$2.65** |
| **Gross Margin (%)** | **52.0%** | **89.9%** | **94.6%** |

---

## 3. Dynamic Customer Health & Churn Metrics

### A. Lifetime Value (LTV) Formula
LTV is calculated dynamically based on average revenue, gross margins, and churn:
$$\text{LTV} = \frac{\text{ARPU} \times \text{Gross Margin}}{\text{Monthly Churn Rate}}$$

### B. Churn Sensitivity Impact (on Growth Plan ARPU = $49.00, Gross Margin = 89.9%)

| Monthly Churn | LTV ($) | Customer Lifetime | Business Growth Impact |
| :---: | :---: | :---: | :--- |
| **2% (Excellent)** | $2,202.55 | 50 months | High exponential growth; excellent product market fit. |
| **5% (Normal)** | $881.02 | 20 months | Steady growth; standard developer SaaS benchmark. |
| **10% (Dangerous)**| $440.51 | 10 months | Growth leaks out; team must freeze acquisition and solve churn. |
| **20% (Terminal)** | $220.25 | 5 months | Churn overrides CAC; business cannot scale sustainably. |

### C. Payback Period
$$\text{Payback Period} = \frac{\text{CAC}}{\text{ARPU} \times \text{Gross Margin}}$$
*Assuming a target customer acquisition cost (CAC) of **$40.00** through organic indie hacker community outreach, the payback period on a Growth Plan ($49/mo) is:*
$$\text{Payback Period} = \frac{\$40.00}{\$49.00 \times 89.9\%} \approx 0.91 \text{ months}$$

---

## 4. Cash Flow & Working Capital Dynamics

Operating a SaaS requires managing cash cycle timing to avoid bank accounts running dry during billing delay windows:

```
[Customer Payment]
       ↓ (Instant)
[Stripe Balance]
       ↓ (7-Day Stripe Payout Hold Delay)
[Business Bank Account]
       ↓ (Monthly Invoice Cycles)
[LLM APIs (Paid Postpaid)] / [Infrastructure Containers (Paid Prepaid Monthly)] / [Payroll & Contractors]
```

### Cash Flow Timing Gates:
1.  **Stripe Payout Lag:** Card deposits take up to **7 rolling days** to settle in the business bank account in standard jurisdictions.
2.  **LLM Invoicing (Postpaid):** LLM API bills (OpenAI, Anthropic) are paid monthly based on usage, giving the business a 30-day interest-free buffer.
3.  **Hosting & Sandbox Compute (Prepaid):** Container servers must be funded at the start of the billing period, requiring front-loaded cash reserves.

---

## 5. Capacity Planning & Infrastructure Scaling

The following matrix details computing resource expectations and costs at scaling inflection points:

| Metric / Scale | 10 Users | 100 Users | 1,000 Users | 10,000 Users |
| :--- | :---: | :---: | :---: | :---: |
| **Avg RPS** | 0.05 | 0.5 | 5.0 | 50.0 |
| **Max Concurrent Generations** | 1 | 5 | 30 | 250 |
| **App Node RAM** | 2 GB | 4 GB | 16 GB | 64 GB (Distributed) |
| **App Node CPU** | 1 vCPU | 2 vCPU | 8 vCPU | 32 vCPU |
| **Database Connections** | < 5 | < 15 | < 100 (Pooler) | < 500 (PgBouncer) |
| **Redis Cache Memory** | 256 MB | 512 MB | 2 GB | 8 GB (HA Cluster) |
| **Celery Queue Workers** | 1 default | 2 default | 8 distributed | 32 dynamic-scaled |
| **Est. Monthly Server Bill** | **$15.00** | **$120.00** | **$850.00** | **$6,200.00** |

---

## 6. Vendor Risk & Mitigations Matrix

We identify and plan for external API vendor failures:

| Vendor Risk Event | Probability | Impact | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **OpenAI raises token prices by 50%** | Medium | High | Blended router dynamically redirects 90% of traffic to Claude or DeepSeek. |
| **Claude API downtime** | Medium | Medium | Automated failover route fallback to standard GPT-4o-mini workspace build steps. |
| **API Rate Limits reached** | High | Medium | Task queue retry-backoff algorithms with Celery enqueueing buffers. |
| **Total external API service block** | Low | Critical | Switch backend to local DeepSeek-Coder models hosted on on-demand runpod nodes. |

---

## 7. Disaster Recovery (DR) Plan
*   **Target Recovery Time Objective (RTO):** 15 minutes (maximum service down time).
*   **Target Recovery Point Objective (RPO):** 5 minutes (maximum data loss threshold).

### Incident Runbooks:
*   **Database Sync Failure:** Auto-switch to secondary read replica. Point-in-time recovery backups (PITR) execute every 15 minutes to S3 storage.
*   **Redis Death:** Fallback configurations shift session cache to memory-backend fallback handlers instantly.
*   **Celery Jam:** Divert long-duration generation requests to high-priority task queues, protecting dashboard analytics.
*   **Stripe Downtime:** Store subscription metadata state on client localstorage, retrying transaction webhook logs up to 48 hours.

---

## 8. Multi-Dimensional Readiness Index

Our readiness metrics across all SaaS domains:

*   **Engineering Readiness: 95%** (29/29 backend tests green, TypeScript type checks safe).
*   **Business Readiness: 20%** (Financial model documented, experiments designed, validation starting).
*   **Operations Readiness: 35%** (CS dashboard integrated; disaster recovery runbooks documented but untested).
*   **Security Readiness: 43%** (Rate limiting, audit logging, and JWT rotation active; CSP, secrets, and MFA pending).
*   **Commercial Readiness: 15%** (Tier quotas modeled; sandbox Stripe checks and trial logic pending live beta verification).

---

## 9. Business Validation Scorecard (Objective Calculations)

Points are calculated using strict quantitative metrics:

| Validation Criteria | Weight | Current Score | Objective Scoring Formula |
| :--- | :---: | :---: | :--- |
| **Unit Economics** | 20 | **20 / 20** | Blended Router Gross Margin: $>80\%$ (20 pts), $70\text{--}80\%$ (15 pts), $<70\%$ (0 pts). |
| **Aha! Moment Verified** | 20 | **0 / 20** | Free users completing project build: $>75\%$ (20 pts), $50\text{--}75\%$ (10 pts), $<50\%$ (0 pts). |
| **7-Day Retention** | 20 | **0 / 20** | Return rate at Week 2: $>35\%$ (20 pts), $20\text{--}35\%$ (10 pts), $<20\%$ (0 pts). |
| **Pricing Validation** | 20 | **0 / 20** | Paywall click-through rate: $>15\%$ (20 pts), $5\text{--}15\%$ (10 pts), $<5\%$ (0 pts). |
| **10 Paying Customers** | 20 | **0 / 20** | Count of paying accounts: $\ge 10$ (20 pts), $5\text{--}9$ (10 pts), $1\text{--}4$ (5 pts), 0 (0 pts). |

**Overall Business Readiness Index Score:** **20 / 100**
