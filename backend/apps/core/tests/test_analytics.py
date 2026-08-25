from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.services.marketplace_sdk import MarketplaceSDK

User = get_user_model()

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testanalytics', password='password123', email='test@bevhub.ai')
        self.client.force_authenticate(user=self.user)

    def test_revenue_dashboard_view(self):
        """
        Verify the revenue metrics engine computes unit economics successfully.
        """
        response = self.client.get('/api/analytics/revenue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn('mrr', data)
        self.assertIn('arr', data)
        self.assertIn('profit', data)
        self.assertIn('margin', data)
        self.assertIn('ltv', data)
        self.assertIn('cac', data)

    def test_quality_dashboard_view(self):
        """
        Verify the AI Quality evaluator returns category statistics.
        """
        response = self.client.get('/api/analytics/quality/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn('average_score', data)
        self.assertIn('categories', data)
        self.assertIn('audit_logs', data)
        self.assertTrue(len(data['categories']) > 0)

    def test_marketplace_sdk_registration(self):
        """
        Verify Marketplace plugin registration and retrieval.
        """
        MarketplaceSDK.register_extension(
            extension_type="validators",
            name="custom_w3c_validator",
            class_path="django.test.TestCase",  # Exists and can be resolved
            metadata={"rule": "w3_compliance"}
        )
        plugin_class = MarketplaceSDK.get_extension("validators", "custom_w3c_validator")
        self.assertIsNotNone(plugin_class)
        self.assertEqual(plugin_class, TestCase)

    def test_telemetry_ingestion_and_dashboard(self):
        """
        Verify telemetry ingestion API parses client-side events,
        records them to DB, and is summarized by Product Intelligence Dashboard.
        """
        # Test telemetry ingestion (unauthenticated post is allowed)
        client = APIClient()
        payload = {
            "step": "registration",
            "status": "success",
            "device": "desktop",
            "browser": "Chrome",
            "duration_ms": 1500,
            "error_message": "",
            "logs": "Successful sign-up",
            "workspace_id": ""
        }
        response = client.post('/api/analytics/telemetry/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test incident reporting ingestion
        failed_payload = {
            "step": "generation_completed",
            "status": "failed",
            "device": "mobile",
            "browser": "Safari",
            "duration_ms": 12000,
            "error_message": "Compiler error: missing semicolon",
            "logs": "stack trace line 1\nstack trace line 2",
            "workspace_id": "ws_beta_1"
        }
        response = client.post('/api/analytics/telemetry/', failed_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify Product Intelligence View fetches the aggregated funnel & incidents
        # Auth client
        auth_response = self.client.get('/api/analytics/product-intelligence/')
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        data = auth_response.data
        self.assertIn('funnel', data)
        self.assertIn('insights', data)
        self.assertIn('onboarding_problems', data)
        self.assertIn('incidents', data)
        
        # Verify our failed incident is captured in the database reports
        incidents = data['incidents']
        self.assertTrue(len(incidents) >= 1)
        self.assertEqual(incidents[0]['error_message'], "Compiler error: missing semicolon")
