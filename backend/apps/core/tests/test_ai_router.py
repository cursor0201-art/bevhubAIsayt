import json
from unittest.mock import MagicMock, patch
from django.test import SimpleTestCase
from core.services.ai_router import AIRouterService, DecomposedTasksSpec
from core.infrastructure.ai_adapters import AIResult, BaseAIProvider

class MockAIProvider(BaseAIProvider):
    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema = None) -> AIResult:
        mock_data = {
            "business_name": "Cyber Accessories",
            "tagline": "Gear for the next century",
            "theme_colors": ["#000000", "#ff00ff", "#00ffff"],
            "pages_to_generate": ["index", "products", "about"],
            "logo_generation_prompt": "A cyber logo",
            "banner_generation_prompt": "A cyber banner",
            "copywriting_tone": "cyberpunk",
            "seo_keywords": ["cyber", "accessories"]
        }
        return AIResult(
            text=json.dumps(mock_data),
            raw_response={"mock": True},
            provider="mock"
        )

    def generate_image(self, prompt: str, size: str = "1024x1024"):
        raise NotImplementedError()


class AIRouterServiceTests(SimpleTestCase):
    def setUp(self):
        self.router = AIRouterService()
        self.mock_provider = MockAIProvider()
        self.router.register_provider("mock", self.mock_provider)

    def test_provider_registration_and_retrieval(self):
        provider = self.router.get_provider("mock")
        self.assertEqual(provider, self.mock_provider)

    def test_routing_policy_picks_appropriate_model(self):
        self.assertEqual(self.router.select_best_provider_for_task("decompose_intent"), "openai")
        self.assertEqual(self.router.select_best_provider_for_task("layout_code_generation"), "claude")
        self.assertEqual(self.router.select_best_provider_for_task("copywriting_text"), "deepseek")

    @patch('core.services.ai_router.AIRouterService.select_best_provider_for_task')
    def test_intent_parsing_returns_valid_spec(self, mock_select):
        mock_select.return_value = "mock"
        
        spec = self.router.parse_intent("I want to create a cyberpunk computer store")
        
        self.assertIsInstance(spec, DecomposedTasksSpec)
        self.assertEqual(spec.business_name, "Cyber Accessories")
        self.assertEqual(spec.copywriting_tone, "cyberpunk")
        self.assertEqual(len(spec.theme_colors), 3)
        self.assertIn("index", spec.pages_to_generate)
