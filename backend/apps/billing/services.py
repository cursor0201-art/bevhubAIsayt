from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from core.domain.models import Tenant
from ai.models import AICreditBalance
from billing.models import SubscriptionPlan, Subscription, Invoice, PromoCode

class BillingService:
    """
    Orchestrates SaaS subscription plans, invoice state settlements, and promo discount bindings.
    """

    @classmethod
    @transaction.atomic
    def create_subscription(cls, tenant: Tenant, plan: SubscriptionPlan, billing_cycle: str = 'monthly') -> Subscription:
        now = timezone.now()
        duration_days = 365 if billing_cycle == 'yearly' else 30
        renewal = now + timedelta(days=duration_days)

        # Create or update subscription
        subscription, created = Subscription.objects.update_or_create(
            tenant=tenant,
            defaults={
                'plan': plan,
                'status': 'active',
                'renewal_date': renewal,
                'expiration_date': renewal + timedelta(days=3)  # grace period
            }
        )

        # Provision AI credits based on plan allowance
        credits_balance, _ = AICreditBalance.objects.get_or_create(
            tenant=tenant, 
            defaults={'balance': Decimal("100.00")}
        )
        credits_balance.balance += Decimal(plan.ai_credits_allowance)
        credits_balance.save()

        # Update Tenant plan details
        tenant.plan_level = plan.slug
        tenant.save(update_fields=['plan_level'])

        return subscription

    @classmethod
    @transaction.atomic
    def settle_invoice_payment(cls, invoice_number: str) -> Invoice:
        invoice = Invoice.objects.get(invoice_number=invoice_number)
        if invoice.status == 'paid':
            return invoice

        # Transition invoice status to paid
        invoice.status = 'paid'
        invoice.save(update_fields=['status'])

        # Ensure subscription is marked active
        if invoice.subscription:
            sub = invoice.subscription
            sub.status = 'active'
            # Slide renewal date forward
            sub.renewal_date = timezone.now() + timedelta(days=30)
            sub.save(update_fields=['status', 'renewal_date'])

        return invoice

    @classmethod
    @transaction.atomic
    def apply_promo_code(cls, tenant: Tenant, code_str: str) -> bool:
        promo = PromoCode.objects.filter(code=code_str, is_active=True).first()
        if not promo:
            return False

        # If promo has expired
        if promo.expiration_date and promo.expiration_date < timezone.now():
            return False

        # Award promotional credits if available
        if promo.extra_credits > 0:
            credits_balance, _ = AICreditBalance.objects.get_or_create(
                tenant=tenant, 
                defaults={'balance': Decimal("100.00")}
            )
            credits_balance.balance += Decimal(promo.extra_credits)
            credits_balance.save()

        return True
