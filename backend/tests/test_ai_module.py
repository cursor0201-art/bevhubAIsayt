from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from core.domain.models import Tenant, Project, User
from ai.models import AICreditBalance, AICreditTransaction, ProjectMemory
from ai.services.context_engine import ContextEngine
from ai.services.credit_service import CreditService
from ai.services.validation_engine import ValidationEngine
from ai.services.workflow_engine import WorkflowEngine

class AICoreTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(company_name="Vapor Labs", plan_level="growth")
        self.user = User.objects.create(
            username="gamer", 
            email="gamer@vaporlabs.io", 
            tenant=self.tenant
        )
        self.project = Project.objects.create(
            tenant=self.tenant,
            project_name="Retro Arcade",
            subdomain="retro-arcade",
            design_system={"color": "purple"}
        )

    def test_context_engine_packages_correct_fields(self):
        # Trigger context packaging
        ctx = ContextEngine.get_generation_context(self.project, self.user)
        
        self.assertEqual(ctx["project"]["name"], "Retro Arcade")
        self.assertEqual(ctx["user"]["preferred_language"], "English")
        
        # Verify memory created
        memory = ProjectMemory.objects.get(project=self.project)
        self.assertEqual(memory.preferred_language, "English")

    def test_credit_service_calculates_and_deducts_balances(self):
        # Verify initial balance creation (default 100.00)
        balance = AICreditBalance.objects.create(tenant=self.tenant, balance=Decimal("50.00"))
        
        # Calculate cost: openai, 1000 input + 1000 output tokens = 2000 tokens * 0.02/1000 = 0.04 credits
        cost = CreditService.calculate_cost("openai", 1000, 1000)
        self.assertEqual(cost, Decimal("0.04"))

        # Check sufficiency
        self.assertTrue(CreditService.has_sufficient_credits(self.tenant, Decimal("10.00")))
        self.assertFalse(CreditService.has_sufficient_credits(self.tenant, Decimal("60.00")))

        # Record usage
        recorded_cost = CreditService.record_usage(
            tenant=self.tenant,
            provider="openai",
            input_tokens=1000,
            output_tokens=1000,
            task_desc="Test Completion"
        )
        self.assertEqual(recorded_cost, Decimal("0.04"))
        
        # Verify balance updated
        balance.refresh_from_db()
        self.assertEqual(balance.balance, Decimal("49.96"))

        # Verify transaction logged
        tx = AICreditTransaction.objects.filter(tenant=self.tenant).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.amount_consumed, Decimal("0.04"))
        self.assertEqual(tx.task_description, "Test Completion")

    @patch('ai.services.validation_engine.AIRouterService')
    def test_validation_engine_repair_flow(self, mock_router_class):
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        
        # Setup mock provider that corrects output on second call
        mock_provider = MagicMock()
        mock_provider.generate_text.side_effect = [
            MagicMock(text='{"bad_json": '),  # First repair output is invalid
            MagicMock(text='{"good_json": true}')  # Second repair output is valid
        ]
        
        mock_router.select_best_provider_for_task.return_value = "mock_provider"
        mock_router.get_provider.return_value = mock_provider

        validator = ValidationEngine()
        
        # Run validate and repair loop
        final_output = validator.validate_and_repair(
            task_name="test_task",
            prompt="Write valid JSON",
            system_instruction="Return JSON",
            raw_output='{"invalid": ',
            validation_fn=ValidationEngine.is_valid_json,
            max_attempts=3
        )

        self.assertEqual(final_output, '{"good_json": true}')
        self.assertEqual(mock_provider.generate_text.call_count, 2)

    @patch('ai.agents.branding_agent.BrandingAgent.run')
    @patch('ai.agents.copywriting_agent.CopywritingAgent.run')
    @patch('ai.agents.seo_agent.SEOAgent.run')
    def test_workflow_engine_coordination(self, mock_seo, mock_copy, mock_branding):
        # Mock agent responses
        mock_branding.return_value = {"design_system": {"font": "Roboto"}}
        mock_copy.return_value = {"copy": "Headline Text"}
        mock_seo.return_value = {"seo": {"title": "SEO Title"}}

        # Fund tenant credits
        AICreditBalance.objects.create(tenant=self.tenant, balance=Decimal("10.00"))

        workflow = WorkflowEngine()
        results = workflow.execute_business_generation_workflow(
            project=self.project,
            user=self.user,
            prompt="Cyberpunk store"
        )

        self.assertEqual(results["design_system"]["font"], "Roboto")
        self.assertEqual(results["copy"], "Headline Text")
        self.assertEqual(results["seo"]["title"], "SEO Title")

        # Verify credits deducted for 3 agents
        balance = AICreditBalance.objects.get(tenant=self.tenant)
        self.assertLess(balance.balance, Decimal("10.00"))
