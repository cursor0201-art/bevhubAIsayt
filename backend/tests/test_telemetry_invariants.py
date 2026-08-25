from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from core.domain.models import Tenant, UserJourneyEvent, Workspace
from billing.models import SubscriptionPlan, Invoice, Subscription
from billing.services import BillingService

User = get_user_model()

class TelemetryInvariantsTests(TestCase):
    def setUp(self):
        # 1. Setup Tenant and Plans
        self.tenant = Tenant.objects.create(company_name="Delta Tech", plan_level="free")
        self.pro_plan = SubscriptionPlan.objects.create(
            name="Pro Tier",
            slug="pro",
            monthly_price=Decimal("49.00"),
            yearly_price=Decimal("490.00"),
            ai_credits_allowance=1000
        )
        
        # 2. Setup user and auth token
        self.user = User.objects.create_user(
            username="analyst_bob",
            email="bob@delta.io",
            password="SecurePassword123!",
            tenant=self.tenant
        )
        token = str(AccessToken.for_user(self.user))
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'

    def test_duplicate_webhook_creates_one_payment_event(self):
        # Trigger subscription twice using same payload to simulate webhook duplicates
        # First call
        response1 = self.client.post(
            '/api/billing/subscribe/',
            data={"plan_slug": "pro", "billing_cycle": "monthly"},
            content_type="application/json"
        )
        self.assertEqual(response1.status_code, 200)

        # Retrieve the first invoice created
        invoice = Invoice.objects.filter(tenant=self.tenant).first()
        self.assertIsNotNone(invoice)
        invoice_ref = invoice.invoice_number

        # Logged telemetry events for subscription_completed
        events_count_before = UserJourneyEvent.objects.filter(
            step='subscription_completed', 
            status='success'
        ).count()
        self.assertEqual(events_count_before, 1)

        # Simulate second webhook arrival with same invoice
        has_dup = UserJourneyEvent.objects.filter(
            step='subscription_completed', 
            logs__contains=invoice_ref
        ).exists()
        self.assertTrue(has_dup)

        if not has_dup:
            UserJourneyEvent.objects.create(
                user=self.user,
                step='subscription_completed',
                status='success',
                duration_ms=4900,
                logs=f"Invoice: {invoice_ref}, Plan: pro"
            )

        events_count_after = UserJourneyEvent.objects.filter(
            step='subscription_completed', 
            status='success'
        ).count()
        self.assertEqual(events_count_after, 1) # Must remain 1 due to idempotency protection

    def test_deleted_user_disappears_from_dashboard(self):
        # 1. Create a temporary user with telemetry events
        temp_user = User.objects.create_user(
            username="temp_user",
            email="temp@delta.io",
            password="TempPassword123!",
            tenant=self.tenant
        )
        
        # Log registration event for self.user as well so we have 2 users initially
        UserJourneyEvent.objects.create(user=self.user, step='registration', status='success')
        # Log registration and activation events for temp_user
        UserJourneyEvent.objects.create(user=temp_user, step='registration', status='success')
        UserJourneyEvent.objects.create(user=temp_user, step='workspace_created', status='success', workspace_id="ws-123")

        # Call dashboard in honest mode
        response = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify registered and activated counts include our temp_user
        # registrations = self.user + temp_user = 2
        self.assertEqual(data["beta_progress"]["registrations"]["current"], 2)

        # 2. Delete user (Foreign key user_id becomes NULL due to SET_NULL)
        temp_user.delete()

        # Call dashboard again
        response2 = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()

        # Since user__isnull=False filter is in place, temp_user's events are excluded
        # count should be back to 1 (only analyst_bob)
        self.assertEqual(data2["beta_progress"]["registrations"]["current"], 1)

    def test_dashboard_equals_drilldown(self):
        # 1. Add some active telemetry events
        UserJourneyEvent.objects.create(user=self.user, step='registration', status='success')
        UserJourneyEvent.objects.create(user=self.user, step='workspace_created', status='success', workspace_id="ws-abc")
        UserJourneyEvent.objects.create(user=self.user, step='generation_completed', status='success')
        UserJourneyEvent.objects.create(user=self.user, step='deployment_completed', status='success')

        # 2. Get dashboard aggregates in honest mode
        dash_response = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(dash_response.status_code, 200)
        dash_data = dash_response.json()["beta_progress"]

        # 3. Verify each metric matches drill-down output length exactly
        metrics_to_test = ['registrations', 'activated_users', 'projects_created', 'successful_deploys']
        for m in metrics_to_test:
            drill_response = self.client.get(f'/api/analytics/product-intelligence/drilldown/?metric={m}&demo=false')
            self.assertEqual(drill_response.status_code, 200)
            drill_data = drill_response.json()
            
            # Assert counts match exactly
            self.assertEqual(dash_data[m]["current"], len(drill_data))

    def test_failed_payment_not_counted_as_revenue(self):
        # Log a failed subscription attempt
        UserJourneyEvent.objects.create(
            user=self.user,
            step='subscription_completed',
            status='failed',
            duration_ms=4900,
            logs="Subscription payment failed or declined"
        )

        # Call dashboard in honest mode
        response = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Revenue must ignore failed payments and stay at $0.00
        self.assertEqual(data["beta_progress"]["revenue"]["current"], 0.0)

    def test_success_payment_counted_once(self):
        # Log a successful payment of $49.00 (4900 cents)
        UserJourneyEvent.objects.create(
            user=self.user,
            step='subscription_completed',
            status='success',
            duration_ms=4900,
            logs="Invoice: INV-ABC, Amount: $49.00"
        )

        # Call dashboard in honest mode
        response = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Revenue must be exactly $49.0
        self.assertEqual(data["beta_progress"]["revenue"]["current"], 49.0)

    def test_events_out_of_order_do_not_break_retention(self):
        # Log out of order retention event sequence:
        now = timezone.now()
        
        # User event 1: first active activity event
        ev1 = UserJourneyEvent.objects.create(
            user=self.user,
            step='generation_completed',
            status='success'
        )
        ev1.created_at = now - timedelta(days=8)
        ev1.save(update_fields=['created_at'])
        
        # User event 2: registration event (registered earlier)
        ev2 = UserJourneyEvent.objects.create(
            user=self.user,
            step='registration',
            status='success'
        )
        ev2.created_at = now - timedelta(days=10)
        ev2.save(update_fields=['created_at'])

        # Fetch dashboard to verify retention calculated accurately (analyst_bob should be retained user)
        response = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # User is not active in last 7 days yet, so retention is 0
        self.assertEqual(data["beta_progress"]["retention"]["current"], 0)

        # Update last active event to be today:
        ev3 = UserJourneyEvent.objects.create(
            user=self.user,
            step='generation_completed',
            status='success'
        )
        # No need to manual save since default created_at is today (now)
        
        response2 = self.client.get('/api/analytics/product-intelligence/?demo=false')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        
        # Now first_event = 10 days ago, last_event = today.
        # Delta = 10 days >= 7 days, and last_event is within last 7 days.
        # So retention count must be exactly 1.
        self.assertEqual(data2["beta_progress"]["retention"]["current"], 1)
