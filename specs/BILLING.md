# BevHub AI Subsystem Specification — Billing & Subscriptions

This document provides the technical blueprint for the **Billing** engine in BevHub AI.

---

## 1. Overview & Objective
The **Billing** system manages platform monetization, subscription tiers, and credit allowances.
- **Tiers**: `free` (1 workspace, 1 active project), `growth` (5 workspaces, 10 active projects), `enterprise` (unlimited, custom domains).
- **Credits System**: Tracks consumption of AI execution tokens. Each agent call consumes tokens, which deduct credits from the workspace balance.
- **Stripe Webhooks**: Listens to Stripe events to update plan status and activate accounts.

---

## 2. Platform Pricing Tier Schema

| Plan | Workspaces Limit | Projects Limit | Monthly Credits | Price |
|---|---|---|---|---|
| Free | 1 | 1 | 100 credits | $0 / mo |
| Growth | 5 | 10 | 10,000 credits | $49 / mo |
| Enterprise | Unlimited | Unlimited | 100,000 credits | $199 / mo |

---

## 3. Stripe Integration API Contracts

### Create Subscription Checkout Session
- **Endpoint**: `POST /api/billing/checkout/`
- **Request Payload**:
  ```json
  {
    "plan": "growth"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "checkout_url": "https://checkout.stripe.com/pay/cs_live_..."
  }
  ```

### Stripe Webhook Receiver
- **Endpoint**: `POST /api/billing/webhooks/stripe/`
- **Headers**: Includes `Stripe-Signature` for signature checking.
- **Handled Events**:
  - `checkout.session.completed`: Locates user and tenant, and updates tenant plan to the requested tier.
  - `customer.subscription.deleted`: Downgrades tenant to `free` plan.
  - `invoice.payment_succeeded`: Refills monthly credit allowances.

---

## 4. Enforcement Decorators
Every critical action (like running agents or creating projects) must be wrapped with a credit and tier validation decorator:
```python
# Conceptual execution gate
def validate_tier_limits(action_type):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            tenant = request.user.tenant
            if action_type == "project_create":
                count = Project.objects.filter(tenant=tenant).count()
                if count >= get_limit_for_plan(tenant.plan_level):
                    return Response({"error": "Plan limit reached"}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```
