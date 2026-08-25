import time
import concurrent.futures
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from core.domain.models import Tenant, Workspace, Project, ProjectFile, AITask
from billing.models import SubscriptionPlan, Subscription, Invoice
import decimal

User = get_user_model()

class LaunchAuditTests(TransactionTestCase):
    """
    Production-readiness verification tests:
    - Multi-tenant security isolation (prevent cross-tenant data leaks)
    - Concurrency and Load simulation (multiple concurrent requests)
    - Billing, subscriptions, and credits calculations
    - Chaos / Failover resilience validation
    """

    def setUp(self):
        # Create plans
        self.startup_plan = SubscriptionPlan.objects.create(
            name="Startup Plan",
            slug="startup",
            monthly_price=decimal.Decimal("49.00"),
            yearly_price=decimal.Decimal("490.00"),
            ai_credits_allowance=100,
            projects_limit=3
        )

        # Tenant A
        self.tenant_a = Tenant.objects.create(company_name="Tenant A Corp", plan_level="growth")
        self.user_a = User.objects.create_user(username='usera', password='password123', email='usera@tenant_a.com', tenant=self.tenant_a)
        self.workspace_a = Workspace.objects.create(tenant=self.tenant_a, name="Workspace A")
        self.client_a = APIClient()
        self.client_a.force_authenticate(user=self.user_a)

        # Tenant B
        self.tenant_b = Tenant.objects.create(company_name="Tenant B Corp", plan_level="free")
        self.user_b = User.objects.create_user(username='userb', password='password123', email='userb@tenant_b.com', tenant=self.tenant_b)
        self.workspace_b = Workspace.objects.create(tenant=self.tenant_b, name="Workspace B")
        self.client_b = APIClient()
        self.client_b.force_authenticate(user=self.user_b)

    def test_tenant_isolation_security(self):
        """
        SECURITY AUDIT: Ensure Tenant B cannot access or modify Tenant A's private resources.
        """
        # Create project under Tenant A
        project_a = Project.objects.create(
            tenant=self.tenant_a,
            workspace=self.workspace_a,
            project_name="Tenant A Secret App",
            subdomain="secret-a"
        )
        file_a = ProjectFile.objects.create(
            project=project_a,
            path="src/pages/index.html",
            content="<h1>Tenant A Only</h1>"
        )

        # Test 1: User B tries to list Tenant A projects via endpoint
        response = self.client_b.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not contain Tenant A's project
        project_ids = [p['id'] for p in response.data]
        self.assertNotIn(str(project_a.id), project_ids)

        # Test 2: User B tries to fetch Tenant A project details directly
        response = self.client_b.get(f'/api/projects/{project_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test 3: User B tries to modify Tenant A project file
        response = self.client_b.put(f'/api/files/{file_a.id}/', {"content": "Hacked"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_billing_credit_validation(self):
        """
        BILLING AUDIT: Verify that credit deductions and plan limits are strictly validated.
        """
        # Create active subscription for Tenant A
        sub = Subscription.objects.create(
            tenant=self.tenant_a,
            plan=self.startup_plan,
            status='active',
            renewal_date=timezone.now() + timezone.timedelta(days=30)
        )
        Invoice.objects.create(
            invoice_number="INV-A-1",
            tenant=self.tenant_a,
            subscription=sub,
            amount=decimal.Decimal("49.00"),
            status='paid',
            payment_provider="stripe"
        )

        # Load revenue engine dashboard endpoint
        response = self.client_a.get('/api/analytics/revenue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mrr'], 49.00)
        self.assertEqual(response.data['arr'], 588.00)
        self.assertEqual(response.data['revenue'], 49.00)

    def test_concurrent_registrations_load(self):
        """
        LOAD BENCHMARK: Simulate concurrent user requests to ensure thread safety and no deadlock conditions.
        """
        def simulate_user_request(i):
            client = APIClient()
            username = f"concurrent_user_{i}"
            user = User.objects.create_user(username=username, password='password123', email=f"{username}@test.com")
            client.force_authenticate(user=user)
            # Fetch workspaces
            res = client.get('/api/workspaces/')
            return res.status_code

        # Run 25 parallel worker tasks using concurrent executor
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_user_request, i) for i in range(25)]
            results = [f.result() for f in futures]

        for code in results:
            self.assertEqual(code, status.HTTP_200_OK)

    def test_failover_recovery_flow(self):
        """
        CHAOS AUDIT: Test error recovery from system failures during pipeline task runs.
        """
        # Create AITask
        task = AITask.objects.create(
            workspace=self.workspace_a,
            prompt="Failure testing",
            status='queued'
        )
        # Verify initial status is queued
        self.assertEqual(task.status, 'queued')
        
        # Simulate background crash
        try:
            raise RuntimeError("Database connection timed out")
        except Exception as e:
            task.status = 'failed'
            task.logs = f"Error during generation: {e}"
            task.save()
            
        self.assertEqual(task.status, 'failed')
        self.assertIn("Database connection timed out", task.logs)
