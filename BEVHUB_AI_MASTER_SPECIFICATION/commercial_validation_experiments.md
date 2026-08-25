# BevHub AI: Commercial Validation Experiments Plan
**Phase 2.5 — Hypotheses Verification**

To transition from an engineering prototype to a validated commercial product, we must test our critical business assumptions using structured experiments during the Closed Beta, prioritizing product value before payment validation.

---

## Experiment 1: The "Aha! Moment" Quota Calibration (Priority 1)
*   **Core Hypothesis:** A free limit of 5 system generations and 2 deployments is the optimal threshold that lets a user experience the complete compile-and-deploy loop without exhausting API token budgets.
*   **Experiment Method:**
    *   Segment beta users into two A/B groups:
        *   **Group A (Current Limit):** 5 generations, 2 deploys.
        *   **Group B (Extended Limit):** 10 generations, 5 deploys.
    *   Track the point in the funnel where users drop off, and correlation with final satisfaction scores.
*   **Success Metrics:**
    *   **Value Realization:** $> 75\%$ of users in Group A complete at least one build and view a preview before reaching the quota limit.
    *   **Friction Drop-off:** $< 10\%$ of users abandon the workspace due to hitting the quota limit too early.

---

## Experiment 2: 7-Day User Retention & Cohort Engagement (Priority 2)
*   **Core Hypothesis:** Active builders return to make edits within 7 days of creating their first project.
*   **Experiment Method:**
    *   Monitor 7-day retention cohorts across different registration weeks using the cohort dashboard.
    *   Trigger automated onboarding checks or outreach emails for users who do not return within 3 days: *"Hey! I saw your workspace is ready. Need any help adding features?"*
*   **Success Metrics:**
    *   **7-Day Retention Rate:** $> 35\%$ of active builders return to execute a generation or code edit in Week 2.
    *   **Re-engagement Response:** $> 20\%$ click-through rate on personalized telemetry-based re-engagement outreach.

---

## Experiment 3: Price Point Willingness Test ($49/mo) (Priority 3)
*   **Core Hypothesis:** Solo founders and freelance builders are willing to pay $49/mo to deploy and host their MVPs with SQLite databases and custom domains.
*   **Target Segment:** Active Closed Beta participants who have successfully built and edited at least one project and returned within 7 days.
*   **Experiment Method:**
    1.  Upon clicking the "Deploy Custom Domain" or "Sync SQLite Cloud" buttons, display a payment gateway modal.
    2.  Show a checkout screen priced at **$49/mo (Growth)** with a 50% discount for early beta users ($24.50/mo).
    3.  Integrate a sandbox Stripe interface.
*   **Success Metrics:**
    *   **Intent Conversion Rate:** $> 15\%$ of active users click the payment button when hitting the lock screen.
    *   **Paid Conversion Rate:** $> 5\%$ of all active Closed Beta users complete the card details entry (simulated sandbox checkout).
