from decimal import Decimal
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from core.domain.models import Tenant
from ai.models import AICreditBalance, AICreditTransaction
from billing.models import SubscriptionPlan, Subscription
from billing.services import BillingService


class BillingDashboardView(APIView):
    """
    Exposes the SaaS monetization metrics, subscription statuses, available plans, 
    and transaction records. Automatically seeds default plans if empty.
    """
    permission_classes = [IsAuthenticated]

    def _seed_plans_if_empty(self):
        if not SubscriptionPlan.objects.exists():
            SubscriptionPlan.objects.create(
                name="Developer (Free Sandbox)",
                slug="developer",
                monthly_price=Decimal("0.00"),
                yearly_price=Decimal("0.00"),
                ai_credits_allowance=100,
                projects_limit=3,
                team_members_limit=1
            )
            SubscriptionPlan.objects.create(
                name="Growth Scale Pro",
                slug="growth",
                monthly_price=Decimal("29.00"),
                yearly_price=Decimal("290.00"),
                ai_credits_allowance=1000,
                projects_limit=15,
                team_members_limit=5
            )
            SubscriptionPlan.objects.create(
                name="Enterprise Authority",
                slug="enterprise",
                monthly_price=Decimal("149.00"),
                yearly_price=Decimal("1490.00"),
                ai_credits_allowance=10000,
                projects_limit=999,
                team_members_limit=50
            )

    def get(self, request):
        self._seed_plans_if_empty()
        user = request.user
        tenant = user.tenant

        # 1. Fetch/Create credit balance
        balance_obj, _ = AICreditBalance.objects.get_or_create(
            tenant=tenant, 
            defaults={'balance': Decimal("100.00")}
        )

        # 2. Get active subscription details
        active_sub = Subscription.objects.filter(tenant=tenant).first()
        sub_data = None
        if active_sub:
            sub_data = {
                "plan_name": active_sub.plan.name,
                "plan_slug": active_sub.plan.slug,
                "status": active_sub.status,
                "renewal_date": active_sub.renewal_date.isoformat()
            }
        else:
            # Fallback to Developer plan by default
            dev_plan = SubscriptionPlan.objects.get(slug="developer")
            active_sub = BillingService.create_subscription(tenant, dev_plan)
            sub_data = {
                "plan_name": active_sub.plan.name,
                "plan_slug": active_sub.plan.slug,
                "status": active_sub.status,
                "renewal_date": active_sub.renewal_date.isoformat()
            }

        # 3. List all plans
        plans = SubscriptionPlan.objects.all()
        plans_list = [{
            "name": p.name,
            "slug": p.slug,
            "monthly_price": str(p.monthly_price),
            "ai_credits": p.ai_credits_allowance,
            "projects_limit": p.projects_limit
        } for p in plans]

        # 4. Fetch recent transactions
        transactions = AICreditTransaction.objects.filter(tenant=tenant).order_by('-created_at')[:20]
        tx_list = [{
            "id": tx.id,
            "provider": tx.model_name,
            "amount": str(tx.amount_consumed),
            "task": tx.task_description,
            "created_at": tx.created_at.isoformat()
        } for tx in transactions]

        return Response({
            "balance": str(balance_obj.balance),
            "subscription": sub_data,
            "plans": plans_list,
            "transactions": tx_list
        })


class SubscribePlanView(APIView):
    """
    Subscribes the user's organization to a plan. In sandbox mode, it directly creates
    the subscription and awards the credit allowance.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = request.user.tenant
        plan_slug = request.data.get("plan_slug")
        cycle = request.data.get("billing_cycle", "monthly")

        if not plan_slug:
            return Response({"error": "plan_slug is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                plan = SubscriptionPlan.objects.get(slug=plan_slug)
                subscription = BillingService.create_subscription(tenant, plan, billing_cycle=cycle)
                
                # Create a mock Invoice for sandbox record keeping
                from billing.models import Invoice
                import uuid
                amount = plan.monthly_price if cycle == 'monthly' else plan.yearly_price
                invoice = Invoice.objects.create(
                    invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                    tenant=tenant,
                    subscription=subscription,
                    amount=amount,
                    status='paid',
                    payment_provider='stripe'
                )

                # Log subscription_completed success telemetry event (with idempotency guard)
                from core.domain.models import UserJourneyEvent
                invoice_ref = invoice.invoice_number
                if not UserJourneyEvent.objects.filter(step='subscription_completed', logs__contains=invoice_ref).exists():
                    UserJourneyEvent.objects.create(
                        user=request.user,
                        step='subscription_completed',
                        status='success',
                        duration_ms=int(amount * 100),  # Save revenue amount in cents
                        logs=f"Invoice: {invoice_ref}, Plan: {plan.slug}, Cycle: {cycle}, Amount: ${amount}"
                    )

            return Response({
                "message": "Subscription updated successfully!",
                "plan_name": plan.name,
                "status": subscription.status,
                "renewal_date": subscription.renewal_date.isoformat()
            })
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription plan not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            from core.domain.models import UserJourneyEvent
            UserJourneyEvent.objects.create(
                user=request.user,
                step='subscription_completed',
                status='failed',
                error_message=str(e)
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApplyPromoCodeView(APIView):
    """
    Claims promotional coupon codes for credits in sandbox mode.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = request.user.tenant
        code = request.data.get("code")

        if not code:
            return Response({"error": "code is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Seed promo code if welcome promo is input
        from billing.models import PromoCode
        code_upper = code.upper()
        
        # Seed known promo codes on first use
        KNOWN_PROMOS = {
            "WELCOME50": {"extra_credits": 50},
            "BEVHUB2026": {"extra_credits": 100},
            "LAUNCH100": {"extra_credits": 100},
        }
        if code_upper in KNOWN_PROMOS and not PromoCode.objects.filter(code=code_upper).exists():
            PromoCode.objects.create(
                code=code_upper,
                extra_credits=KNOWN_PROMOS[code_upper]["extra_credits"],
                is_active=True
            )

        success = BillingService.apply_promo_code(tenant, code_upper)
        if success:
            balance_obj = AICreditBalance.objects.get(tenant=tenant)
            return Response({
                "message": "Promo code applied successfully!",
                "balance": str(balance_obj.balance)
            })
        return Response({"error": "Invalid, expired, or inactive promo code"}, status=status.HTTP_400_BAD_REQUEST)
