from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.domain.models import Tenant, Workspace, User, AITask

class AITaskStreamAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(company_name="Acme Inc", plan_level="growth")
        self.user = User.objects.create_user(
            username="devuser",
            email="dev@acme.com",
            password="securepassword123",
            tenant=self.tenant
        )
        self.workspace = Workspace.objects.create(tenant=self.tenant, name="Development Workspace")
        self.task = AITask.objects.create(
            workspace=self.workspace,
            prompt="Generate a clean coffee shop website",
            status="queued",
            progress=0,
            logs="Initializing..."
        )
        self.client.force_authenticate(user=self.user)

    @patch('redis.Redis.from_url')
    def test_stream_returns_event_stream_with_initial_payload(self, mock_redis_from_url):
        # Configure mock for redis client & pubsub
        mock_redis = MagicMock()
        mock_pubsub = MagicMock()
        
        # Make the subscription listen return an empty list or immediately exit
        mock_pubsub.listen.return_value = []
        mock_redis.pubsub.return_value = mock_pubsub
        mock_redis_from_url.return_value = mock_redis

        url = reverse('ai_tasks-stream', args=[str(self.task.id)])
        response = self.client.get(url)

        # Assert status and content type
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/event-stream')
        self.assertEqual(response['Cache-Control'], 'no-cache')
        self.assertEqual(response['X-Accel-Buffering'], 'no')

        # Read yielded event stream
        content_items = list(response.streaming_content)
        self.assertTrue(len(content_items) > 0)
        
        # Verify first item yielded is the initial task status
        first_event = content_items[0].decode('utf-8')
        self.assertIn("initial", first_event)
        self.assertIn("Generate a clean coffee shop website", first_event)
        self.assertIn("queued", first_event)
