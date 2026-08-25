import json
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from core.domain.models import Tenant, Workspace, Project, ProjectFile, Page, ProjectReview, ProjectSnapshot, ProjectFixRun
from apps.ai.services.bug_fixer import SnapshotService, RollbackService, FixPlanner, FixExecutor, BugFixService

User = get_user_model()

class BugFixerTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(company_name="BugFix QA Corp", plan_level="growth")
        self.workspace = Workspace.objects.create(tenant=self.tenant, name="QA Sandbox")
        self.user = User.objects.create_user(
            username="fixer_agent",
            email="fixer@bevhub.ai",
            password="Password123!",
            tenant=self.tenant,
            role="owner"
        )
        self.project = Project.objects.create(
            tenant=self.tenant,
            workspace=self.workspace,
            owner=self.user,
            project_name="Vulnerable Shop",
            subdomain="vulnshop",
            design_system={"colors": ["#111111"]}
        )
        self.file = ProjectFile.objects.create(
            project=self.project,
            path="src/pages/index.html",
            content="<div>Old Body</div>"
        )
        self.page = Page.objects.create(
            project=self.project,
            slug="index",
            title="Index Page",
            raw_content="<div>Old Body</div>"
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_snapshot_and_rollback(self):
        # 1. Create Snapshot
        snapshot = SnapshotService.create_snapshot(self.project, "Initial state")
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.snapshot_data["files"][0]["content"], "<div>Old Body</div>")

        # 2. Modify project state
        self.file.content = "<div>Modified Hack</div>"
        self.file.save()
        self.page.raw_content = "<div>Modified Hack</div>"
        self.page.save()

        # 3. Trigger rollback
        RollbackService.rollback(snapshot)

        # 4. Verify restore
        self.file = self.project.files.get(path="src/pages/index.html")
        self.page = self.project.pages.get(slug="index")
        self.assertEqual(self.file.content, "<div>Old Body</div>")
        self.assertEqual(self.page.raw_content, "<div>Old Body</div>")


    def test_fix_planner_heuristics(self):
        review = ProjectReview.objects.create(
            project=self.project,
            overall_score=70,
            architecture_score=70,
            performance_score=70,
            security_score=70,
            seo_score=70,
            accessibility_score=70,
            ux_score=70,
            typescript_score=70,
            react_score=70,
            deployment_score=70,
            issues=[
                {"severity": "critical", "title": "Secret Key Exposed", "description": "Found key in file"},
                {"severity": "low", "title": "Missing Alt Attribute", "description": "Image needs alt"}
            ]
        )

        planner = FixPlanner()
        plan = planner.build_plan(self.project, review)

        self.assertEqual(len(plan), 2)
        # Critical should have higher risk and be sorted first
        self.assertEqual(plan[0]["severity"], "critical")
        self.assertEqual(plan[1]["severity"], "low")

    @patch('core.services.ai_router.AIRouterService.select_best_provider_for_task')
    @patch('core.services.ai_router.AIRouterService.get_provider')
    def test_fix_executor_successful_run(self, mock_get_provider, mock_select_provider):
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "files": [
                {"path": "src/pages/index.html", "content": "<div>Fixed Content</div>"}
            ],
            "lines_modified": "Line 1-3",
            "explanation": "Applied proper CTA structure"
        })
        mock_provider.generate_text.return_value = mock_response
        mock_get_provider.return_value = mock_provider
        mock_select_provider.return_value = "mock-model"

        executor = FixExecutor()
        fix = {
            "id": "fix-ux",
            "severity": "medium",
            "reason": "Missing CTA",
            "root_cause": "No conversion path",
            "affected_files": ["src/pages/index.html"],
            "fix_strategy": "Rewrite file"
        }
        res = executor.execute_fix(self.project, fix)
        self.assertTrue(res["success"])
        self.file.refresh_from_db()
        self.assertEqual(self.file.content, "<div>Fixed Content</div>")

    @patch('core.services.ai_router.AIRouterService.select_best_provider_for_task')
    @patch('core.services.ai_router.AIRouterService.get_provider')
    def test_bug_fix_pipeline_improved(self, mock_get_provider, mock_select_provider):
        # Setup mock review answers
        # Initial review will return 70
        # Post-fix review will return 95 (improved)
        mock_provider = MagicMock()
        
        # Planner response -> FixExecutor response -> Review engine responses
        mock_plan = json.dumps([
            {
                "id": "fix-seo",
                "severity": "high",
                "reason": "Missing meta tag",
                "root_cause": "No metadata",
                "affected_files": ["src/pages/index.html"],
                "fix_strategy": "Add tags",
                "confidence": 95,
                "estimated_risk": 20
            }
        ])
        mock_execute = json.dumps({
            "files": [{"path": "src/pages/index.html", "content": "<div>Fixed SEO tags</div>"}],
            "lines_modified": "Line 1",
            "explanation": "Added tags"
        })
        
        # We need mock to return:
        # 1. plan JSON
        # 2. executor JSON
        # 3. AI review engine refined report JSON (when ReviewService is called inside after-fix review)
        mock_review_refined = json.dumps({
            "overall_score": 95,
            "architecture": 95,
            "performance": 95,
            "security": 95,
            "seo": 95,
            "accessibility": 95,
            "ux": 95,
            "typescript": 95,
            "react": 95,
            "deployment": 95,
            "issues": [],
            "recommendations": []
        })

        mock_responses = [MagicMock(text=mock_plan), MagicMock(text=mock_execute), MagicMock(text=mock_review_refined)]
        mock_provider.generate_text.side_effect = mock_responses
        mock_get_provider.return_value = mock_provider
        mock_select_provider.return_value = "mock-model"

        # Create initial review (70)
        ProjectReview.objects.create(
            project=self.project,
            overall_score=70,
            architecture_score=70,
            performance_score=70,
            security_score=70,
            seo_score=70,
            accessibility_score=70,
            ux_score=70,
            typescript_score=70,
            react_score=70,
            deployment_score=70,
            issues=[{"severity": "high", "title": "Missing meta tag", "description": "No metadata"}],
            recommendations=[]
        )

        url = f"/api/projects/{self.project.id}/fix/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["before_score"], 70)
        self.assertEqual(data["after_score"], 95)
        self.assertEqual(data["fixed"], 1)
        self.assertFalse(data["rollback_available"])

        self.file.refresh_from_db()
        self.assertEqual(self.file.content, "<div>Fixed SEO tags</div>")

    @patch('core.services.ai_router.AIRouterService.select_best_provider_for_task')
    @patch('core.services.ai_router.AIRouterService.get_provider')
    def test_bug_fix_pipeline_rollback_on_worse_score(self, mock_get_provider, mock_select_provider):
        mock_provider = MagicMock()
        
        mock_plan = json.dumps([
            {
                "id": "fix-seo",
                "severity": "high",
                "reason": "Missing meta tag",
                "root_cause": "No metadata",
                "affected_files": ["src/pages/index.html"],
                "fix_strategy": "Add tags",
                "confidence": 95,
                "estimated_risk": 20
            }
        ])
        mock_execute = json.dumps({
            "files": [{"path": "src/pages/index.html", "content": "<div>Broken CSS/JS</div>"}],
            "lines_modified": "Line 1",
            "explanation": "Introduced syntax error"
        })
        
        # Post-fix review score drops to 50
        mock_review_refined = json.dumps({
            "overall_score": 50,
            "architecture": 50,
            "performance": 50,
            "security": 50,
            "seo": 50,
            "accessibility": 50,
            "ux": 50,
            "typescript": 50,
            "react": 50,
            "deployment": 50,
            "issues": [{"severity": "critical", "title": "Syntax Error", "description": "Crash"}],
            "recommendations": []
        })

        mock_responses = [MagicMock(text=mock_plan), MagicMock(text=mock_execute), MagicMock(text=mock_review_refined)]
        mock_provider.generate_text.side_effect = mock_responses
        mock_get_provider.return_value = mock_provider
        mock_select_provider.return_value = "mock-model"

        # Create initial review (70)
        ProjectReview.objects.create(
            project=self.project,
            overall_score=70,
            architecture_score=70,
            performance_score=70,
            security_score=70,
            seo_score=70,
            accessibility_score=70,
            ux_score=70,
            typescript_score=70,
            react_score=70,
            deployment_score=70,
            issues=[{"severity": "high", "title": "Missing meta tag", "description": "No metadata"}],
            recommendations=[]
        )

        url = f"/api/projects/{self.project.id}/fix/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["before_score"], 70)
        self.assertEqual(data["after_score"], 70) # Remains 70 due to rollback
        self.assertTrue(data["rollback_available"])

        # File content must rollback to old content
        self.file = self.project.files.get(path="src/pages/index.html")
        self.assertEqual(self.file.content, "<div>Old Body</div>")
