from unittest.mock import MagicMock, patch
from django.test import TestCase
from core.domain.models import Tenant, Project, Page, Deployment
from core.domain.events import EventDispatcher, ProjectCreatedEvent
from core.services.generation_service import GenerationService
from core.services.ai_router import DecomposedTasksSpec

class GenerationServiceTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(company_name="Acme Inc", plan_level="growth")
        self.generation_service = GenerationService()

    @patch('core.services.generation_service.AIRouterService.parse_intent')
    def test_business_generation_creates_records_and_dispatches_events(self, mock_parse_intent):
        # Mock the AI output blueprint spec
        mock_blueprint = DecomposedTasksSpec(
            business_name="Retro Gaming Store",
            tagline="Play like it's 1989",
            theme_colors=["#000000", "#ff0000", "#ffffff"],
            pages_to_generate=["index", "catalog", "contact"],
            logo_generation_prompt="Retro game logo",
            banner_generation_prompt="Retro banner image",
            copywriting_tone="retro",
            seo_keywords=["retro", "games", "nintendo"]
        )
        mock_parse_intent.return_value = mock_blueprint

        # Capture dispatched events
        dispatched_events = []
        def mock_listener(event):
            dispatched_events.append(event)

        EventDispatcher.register(ProjectCreatedEvent, mock_listener)

        # Run creation process
        project = self.generation_service.generate_business_infrastructure(
            tenant=self.tenant,
            user_prompt="I want to create a retro gaming store"
        )

        # Assert records created
        self.assertIsInstance(project, Project)
        self.assertEqual(project.project_name, "Retro Gaming Store")
        self.assertEqual(project.tenant, self.tenant)
        self.assertEqual(project.design_system["tone"], "retro")

        # Assert pages created
        pages = Page.objects.filter(project=project)
        self.assertEqual(len(pages), 3)
        self.assertTrue(pages.filter(slug="index").exists())
        self.assertTrue(pages.filter(slug="catalog").exists())
        self.assertTrue(pages.filter(slug="contact").exists())

        # Assert deployment created
        deployment = Deployment.objects.filter(project=project).first()
        self.assertIsNotNone(deployment)
        self.assertEqual(deployment.status, "queued")

        # Assert event dispatched
        self.assertEqual(len(dispatched_events), 1)
        event = dispatched_events[0]
        self.assertIsInstance(event, ProjectCreatedEvent)
        self.assertEqual(event.project_id, project.id)
        self.assertEqual(event.tenant_id, self.tenant.id)
        self.assertEqual(event.project_name, "Retro Gaming Store")
