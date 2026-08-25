from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from core.domain.models import Tenant
from ai.models import AICreditBalance
from billing.models import SubscriptionPlan, Subscription, Invoice, PromoCode
from billing.services import BillingService
from payments.models import PaymentAttempt
from payments.services import PaymentGatewayFactory, StripeGateway, PayPalGateway

class BillingAndPaymentsTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(company_name="Delta Tech", plan_level="free")
        
        # Setup subscription plans
        self.pro_plan = SubscriptionPlan.objects.create(
            name="Pro Tier",
            slug="pro",
            monthly_price=Decimal("49.00"),
            yearly_price=Decimal("490.00"),
            ai_credits_allowance=1000,
            storage_limit_gb=50,
            projects_limit=15,
            team_members_limit=5
        )

    def test_create_subscription_allocates_limits_and_credits(self):
        # Initial balance starts empty (mock check)
        credits_balance, _ = AICreditBalance.objects.get_or_create(tenant=self.tenant, defaults={'balance': Decimal("10.00")})
        
        sub = BillingService.create_subscription(self.tenant, self.pro_plan)
        
        self.assertEqual(sub.tenant, self.tenant)
        self.assertEqual(sub.plan, self.pro_plan)
        self.assertEqual(sub.status, "active")
        
        # Check Tenant plan level updated
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.plan_level, "pro")

        # Check AI credits awarded (10 + 1000 = 1010 credits)
        credits_balance.refresh_from_db()
        self.assertEqual(credits_balance.balance, Decimal("1010.00"))

    def test_invoice_settlement(self):
        # Setup Subscription & Invoice
        sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.pro_plan,
            status='past_due',
            renewal_date=timezone.now()
        )
        invoice = Invoice.objects.create(
            invoice_number="INV-2026-0001",
            tenant=self.tenant,
            subscription=sub,
            amount=Decimal("49.00"),
            status="open",
            payment_provider="Stripe"
        )

        settled_invoice = BillingService.settle_invoice_payment("INV-2026-0001")
        self.assertEqual(settled_invoice.status, "paid")
        
        sub.refresh_from_db()
        self.assertEqual(sub.status, "active")

    def test_apply_promo_code_adds_credits(self):
        promo = PromoCode.objects.create(
            code="SUMMER500",
            extra_credits=500,
            is_active=True
        )
        
        credits_balance = AICreditBalance.objects.create(tenant=self.tenant, balance=Decimal("100.00"))
        
        success = BillingService.apply_promo_code(self.tenant, "SUMMER500")
        self.assertTrue(success)
        
        credits_balance.refresh_from_db()
        self.assertEqual(credits_balance.balance, Decimal("600.00"))

    def test_payment_gateway_factory_returns_correct_adapters(self):
        stripe = PaymentGatewayFactory.get_gateway("stripe")
        self.assertIsInstance(stripe, StripeGateway)
        
        paypal = PaymentGatewayFactory.get_gateway("paypal")
        self.assertIsInstance(paypal, PayPalGateway)

        checkout_url = stripe.create_checkout_session(self.tenant, Decimal("49.00"), "USD")
        self.assertIn("checkout.stripe.com", checkout_url)


class BillingViewsTests(TestCase):
    def setUp(self):
        from core.domain.models import User
        from rest_framework_simplejwt.tokens import AccessToken
        self.tenant = Tenant.objects.create(company_name="Delta Tech", plan_level="free")
        self.user = User.objects.create_user(
            username="testbillinguser",
            email="test@delta.io",
            password="SecurePassword123!",
            tenant=self.tenant
        )
        token = str(AccessToken.for_user(self.user))
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'

    def test_get_billing_dashboard_seeds_plans_and_returns_balance(self):
        response = self.client.get('/api/billing/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("balance", response.json())
        self.assertIn("subscription", response.json())
        self.assertIn("plans", response.json())
        
        # Verify plans are seeded automatically
        self.assertTrue(SubscriptionPlan.objects.filter(slug="growth").exists())

    def test_subscribe_plan_view_updates_plan_level(self):
        # Trigger plan seed first
        self.client.get('/api/billing/dashboard/')
        
        response = self.client.post(
            '/api/billing/subscribe/',
            data={"plan_slug": "growth", "billing_cycle": "monthly"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["plan_name"], "Growth Scale Pro")

        # Verify tenant updated
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.plan_level, "growth")

    def test_apply_promo_view_adds_credits(self):
        response = self.client.post(
            '/api/billing/promo/',
            data={"code": "WELCOME50"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("balance", response.json())
        
        # Check credit balance
        balance = AICreditBalance.objects.get(tenant=self.tenant)
        self.assertEqual(balance.balance, Decimal("150.00")) # 100 default + 50 promo

    def test_preferences_flow(self):
        # 1. Check initial defaults
        response = self.client.get('/api/ai/preferences/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["writing_style"], "Professional")
        
        # 2. Update preferences
        response = self.client.post(
            '/api/ai/preferences/',
            data={
                "writing_style": "Playful",
                "favorite_colors": ["#10b981", "#3b82f6"],
                "preferred_language": "Russian"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["writing_style"], "Playful")
        self.assertEqual(response.json()["preferred_language"], "Russian")


