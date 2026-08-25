from unittest.mock import MagicMock, patch
from django.test import TestCase
from core.domain.models import Tenant, Workspace, AITask, User, Project, ProjectFile, Page, Deployment
from ai.services.orchestrator import AIOrchestrator
from ai.agents.base_agent import AgentOutput

class AIOrchestratorTests(TestCase):
    def setUp(self):
        self.redis_patcher = patch('ai.services.orchestrator.AIOrchestrator.publish_event')
        self.redis_patcher.start()
        self.tenant = Tenant.objects.create(company_name="Tea Co", plan_level="growth")
        self.user = User.objects.create_user(
            username="teabuilder",
            email="builder@tea.co",
            password="securepassword",
            tenant=self.tenant
        )
        self.workspace = Workspace.objects.create(
            tenant=self.tenant,
            name="Tea Sandbox"
        )
        self.task = AITask.objects.create(
            workspace=self.workspace,
            prompt="Create a luxury tea subscription store",
            status="queued",
            progress=0
        )


    def tearDown(self):
        self.redis_patcher.stop()

    def test_orchestration_synthesizes_custom_codebase(self):


        # Configure mock for ReasoningEngine.analyze
        from ai.services.reasoning_engine import ReasoningResult, RequestClass, ThinkingMode, ComplexityLevel, QualityScore, CandidateSolution

        mock_reasoning_result = ReasoningResult(
            prompt=self.task.prompt,
            request_class=RequestClass.WEBSITE,
            thinking_mode=ThinkingMode.CREATIVE,
            complexity=ComplexityLevel.MEDIUM,
            problems={},
            risks=["Risk A", "Risk B"],
            candidates=[],
            chosen_solution=CandidateSolution("Mock Solution", "Desc"),
            required_parts=[13, 14, 18, 24, 26, 27, 28, 30, 31, 32, 33, 36, 37],
            quality=QualityScore(10, 10, 10, 10, 10, 10),
            insights=["Insight A"]
        )

        # For predictability, let's configure a mock mapping inside our test
        mock_outputs = {
            13: AgentOutput("planner_agent", True, {"plan": "Mock Plan"}, "Decided plan", [], None, "mock", 10),
            31: AgentOutput("business_analyst_agent", True, {"business_analysis": "Luxury tea market analysis"}, "BA reasoning", [], None, "mock", 10),
            30: AgentOutput("product_manager_agent", True, {"product_spec": "Subscription tea box tiers"}, "PM reasoning", [], None, "mock", 10),
            32: AgentOutput("solution_architect_agent", True, {"architecture": "API-first microservices"}, "Arch reasoning", [], None, "mock", 10),
            26: AgentOutput("database_designer_agent", True, {"ddl_schema": "CREATE TABLE tea_orders (id UUID PRIMARY KEY);"}, "DB reasoning", [], None, "mock", 10),
            24: AgentOutput("code_studio_agent", True, {"code": '{"endpoints": [{"path": "/api/tea"}]}'}, "Backend reasoning", [], None, "mock", 10),
            18: AgentOutput("branding_agent", True, {
                "design_system": {
                    "primary_color": "#0f766e",
                    "secondary_color": "#be123c",
                    "background_color": "#020617",
                    "font_family": "Playfair Display",
                    "border_radius": "0.5rem"
                }
            }, "Branding reasoning", [], None, "mock", 10),
            14: AgentOutput("ui_designer_agent", True, {"ui_spec": "Responsive layout spec"}, "UI reasoning", [], None, "mock", 10),
            36: AgentOutput("seo_agent", True, {"seo_strategy": "title: Exclusive Tea Subscriptions\ndescription: Premium organic tea deliveries"}, "SEO reasoning", [], None, "mock", 10),
            37: AgentOutput("copywriting_agent", True, {"copy": "Savor the world's finest handpicked organic tea leaves delivered directly to your doorstep monthly."}, "Copy reasoning", [], None, "mock", 10),
            27: AgentOutput("devops_agent", True, {"devops_config": "FROM python:3.11"}, "DevOps reasoning", [], None, "mock", 10),
            28: AgentOutput("qa_agent", True, {"test_suite": "def test_tea(): assert True"}, "QA reasoning", [], None, "mock", 10),
            33: AgentOutput("cto_agent", True, {"cto_review": "Codebase is clean, optimized, and ready."}, "CTO reasoning", [], None, "mock", 10),
        }

        # Override run_agent to bypass live LLM calls and return the structured outputs defined above
        original_run_agent = AIOrchestrator.run_agent
        def mock_run_agent(self_instance, part_number, agent_title, task_name, prompt, context):
            out = mock_outputs.get(part_number)
            if out:
                # Mock context updates like BrandingAgent would do
                if part_number == 18:
                    context["project"]["design_system"] = out.data["design_system"]
                return out.data
            return {}

        def mock_perform_code_review(project):
            from core.domain.models import ProjectReview
            return ProjectReview.objects.create(
                project=project,
                overall_score=98,
                architecture_score=98,
                performance_score=98,
                security_score=98,
                seo_score=98,
                accessibility_score=98,
                ux_score=98,
                typescript_score=98,
                react_score=98,
                deployment_score=98,
                issues=[],
                recommendations=[]
            )

        with patch.object(AIOrchestrator, 'run_agent', new=mock_run_agent), \
             patch('ai.services.reasoning_engine.ReasoningEngine.analyze', return_value=mock_reasoning_result), \
             patch('ai.services.review_engine.ReviewService.perform_code_review', side_effect=mock_perform_code_review):

            orchestrator = AIOrchestrator(self.task)
            project = orchestrator.execute(self.user)

            # Assert project properties
            self.assertIsInstance(project, Project)
            self.assertEqual(project.project_name, "Generated Create A Luxury Tea Subscription Store")
            self.assertEqual(project.design_system["primary_color"], "#0f766e")
            self.assertEqual(project.design_system["font_family"], "Playfair Display")

            # Assert generated files
            readme = ProjectFile.objects.get(project=project, path="README.md")
            self.assertIn("Subscription tea box tiers", readme.content)
            self.assertIn("Luxury tea market analysis", readme.content)
            self.assertIn("API-first microservices", readme.content)
            self.assertIn("Codebase is clean, optimized, and ready.", readme.content)

            sql = ProjectFile.objects.get(project=project, path="src/database/schema.sql")
            self.assertEqual(sql.content, "CREATE TABLE tea_orders (id UUID PRIMARY KEY);")

            routes = ProjectFile.objects.get(project=project, path="src/api/routes.json")
            self.assertIn("/api/tea", routes.content)

            dockerfile = ProjectFile.objects.get(project=project, path="Dockerfile")
            self.assertEqual(dockerfile.content, "FROM python:3.11")

            tests = ProjectFile.objects.get(project=project, path="tests/test_suite.py")
            self.assertEqual(tests.content, "def test_tea(): assert True")

            reasoning_rep = ProjectFile.objects.get(project=project, path="src/reasoning_report.md")
            self.assertIn("Create a luxury tea subscription store", reasoning_rep.content)
            self.assertIn("Risk A", reasoning_rep.content)
            self.assertIn("Mock Solution", reasoning_rep.content)

            # Assert pages
            index_page = Page.objects.get(project=project, slug="index")
            self.assertIn("Exclusive Tea Subscriptions", index_page.raw_content)
            self.assertIn("Premium organic tea deliveries", index_page.raw_content)
            self.assertIn("Playfair Display", index_page.raw_content)
            self.assertIn("#0f766e", index_page.raw_content)
            self.assertIn("Savor the world's finest handpicked organic tea leaves", index_page.raw_content)

            # Assert deployment status
            deployment = Deployment.objects.get(project=project)
            self.assertEqual(deployment.status, "success")
            self.assertEqual(deployment.deploy_url, f"https://{project.subdomain}.bevhub.ai")

            # Assert task completion status
            self.task.refresh_from_db()
            self.assertEqual(self.task.status, "completed")
            self.assertEqual(self.task.progress, 100)

    @patch('core.services.ai_router.AIRouterService.select_best_provider_for_task')
    @patch('core.services.ai_router.AIRouterService.get_provider')
    def test_ai_edit_endpoint(self, mock_get_provider, mock_select_provider):
        # Create a mock project
        project = Project.objects.create(
            tenant=self.tenant,
            project_name="Tea Hub",
            subdomain="teahub-sub",
            design_system={"colors": ["#000000"]}
        )
        
        # Create a project file
        proj_file = ProjectFile.objects.create(
            project=project,
            path="src/pages/index.html",
            content="<div>Old Tea Store</div>"
        )
        
        # Setup mock provider generate_text return value
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "<div>New Violet Tea Store</div>"
        mock_provider.generate_text.return_value = mock_response
        mock_get_provider.return_value = mock_provider
        mock_select_provider.return_value = "mock-provider-name"
        
        # Call the endpoint
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = f"/api/projects/{project.id}/ai-edit/"
        response = client.post(url, {
            "prompt": "change to violet theme and write New Violet Tea Store",
            "filepath": "src/pages/index.html"
        }, format="json")
        
        self.assertEqual(response.status_code, 200)
        proj_file.refresh_from_db()
        self.assertEqual(proj_file.content, "<div>New Violet Tea Store</div>")
        
        # Check that page slug is updated
        page = Page.objects.get(project=project, slug="index")
        self.assertEqual(page.raw_content, "<div>New Violet Tea Store</div>")

    def test_ai_edit_endpoint_path_traversal_prevention(self):
        project = Project.objects.create(
            tenant=self.tenant,
            project_name="Tea Hub",
            subdomain="teahub-sub-traversal",
            design_system={"colors": ["#000000"]}
        )
        
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = f"/api/projects/{project.id}/ai-edit/"
        
        # Test directory traversal path
        response = client.post(url, {
            "prompt": "change to violet theme",
            "filepath": "src/pages/../../etc/passwd"
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid or unsafe filepath")

        # Test absolute path
        response = client.post(url, {
            "prompt": "change to violet theme",
            "filepath": "/etc/passwd"
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid or unsafe filepath")

    @patch('core.services.ai_router.AIRouterService.select_best_provider_for_task')
    @patch('core.services.ai_router.AIRouterService.get_provider')
    def test_code_review_endpoint(self, mock_get_provider, mock_select_provider):
        import json
        project = Project.objects.create(
            tenant=self.tenant,
            project_name="Tea Hub",
            subdomain="teahub-review",
            design_system={"colors": ["#000000"]}
        )
        ProjectFile.objects.create(
            project=project,
            path="src/pages/index.html",
            content="<div>Storefront</div>"
        )
        Page.objects.create(
            project=project,
            slug="index",
            title="Index Page",
            raw_content="<div>Storefront</div>"
        )

        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "overall_score": 98,
            "architecture": 96,
            "performance": 97,
            "security": 100,
            "seo": 99,
            "accessibility": 94,
            "ux": 98,
            "typescript": 97,
            "react": 98,
            "deployment": 100,
            "issues": [
                {
                    "severity": "critical",
                    "title": "Missing CSP Header",
                    "description": "Content Security Policy is missing."
                }
            ],
            "recommendations": [
                "Implement strict CSP headers",
                "Ensure images use alt tags"
            ]
        })
        mock_provider.generate_text.return_value = mock_response
        mock_get_provider.return_value = mock_provider
        mock_select_provider.return_value = "mock-provider"

        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken

        client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Call POST to trigger review
        url = f"/api/projects/{project.id}/review/"
        response = client.post(url, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["overall_score"], 98)
        self.assertEqual(data["architecture_score"], 96)
        self.assertTrue(len(data["issues"]) >= 1)
        issue_titles = [issue["title"] for issue in data["issues"]]
        self.assertIn("Missing CSP Header", issue_titles)

        # Call GET to fetch reviews list
        get_url = f"/api/projects/{project.id}/reviews/"
        get_response = client.get(get_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.json()), 1)
