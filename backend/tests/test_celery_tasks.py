from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from core.domain.models import Tenant, Project, User, Page, Deployment
from ai.models import AICreditBalance
from core.tasks import run_project_generation_workflow_task

class CeleryTasksTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(company_name="Task Test Tenant", plan_level="growth")
        self.user = User.objects.create(
            username="taskuser",
            email="taskuser@test.com",
            tenant=self.tenant
        )
        self.project = Project.objects.create(
            tenant=self.tenant,
            project_name="Task Project",
            subdomain="task-project",
            design_system={"colors": ["#111"]}
        )
        self.index_page = Page.objects.create(
            project=self.project,
            slug="index",
            title="Home",
            raw_content="Placeholder"
        )
        self.deployment = Deployment.objects.create(
            project=self.project,
            status="queued"
        )
        # Provision credits
        AICreditBalance.objects.create(tenant=self.tenant, balance=Decimal("100.00"))

    @patch('ai.services.workflow_engine.WorkflowEngine.execute_business_generation_workflow')
    def test_run_project_generation_workflow_task_updates_project_and_pages(self, mock_workflow_exec):
        # Mocking workflow engine response
        mock_workflow_exec.return_value = {
            "design_system": {
                "colors": ["#8b5cf6", "#ec4899"],
                "font_family": "Outfit",
                "tone": "playful"
            },
            "copy": "Dynamic generated conversion copy text content.",
            "seo": {"title": "Test Title"}
        }

        # Execute task synchronously
        res = run_project_generation_workflow_task(
            project_id=str(self.project.id),
            user_id=self.user.id,
            user_prompt="Build a SaaS store"
        )

        self.assertEqual(res["status"], "success")
        
        # Verify project design system was updated in DB
        self.project.refresh_from_db()
        self.assertEqual(self.project.design_system["font_family"], "Outfit")
        
        # Verify index page content updated
        self.index_page.refresh_from_db()
        self.assertIn("Dynamic generated conversion copy text content.", self.index_page.raw_content)
        self.assertIn("#8b5cf6", self.index_page.raw_content)

        # Verify deployment was updated to success
        self.deployment.refresh_from_db()
        self.assertEqual(self.deployment.status, "success")
        self.assertEqual(self.deployment.deploy_url, "https://task-project.bevhub.ai")
