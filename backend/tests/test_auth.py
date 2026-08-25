from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from core.domain.models import Tenant

User = get_user_model()

class AuthAPITests(APITestCase):
    def test_user_registration_creates_tenant_and_returns_tokens(self):
        url = reverse('auth_register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "company_name": "Test Agency"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        
        # Verify user creation
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertIsNotNone(user.tenant)
        self.assertEqual(user.tenant.company_name, "Test Agency")

    def test_token_obtain_and_generation_flow(self):
        # Register a user first
        tenant = Tenant.objects.create(company_name="Acme Inc")
        user = User.objects.create_user(
            username="acmeuser",
            email="acme@example.com",
            password="SecurePassword123!",
            tenant=tenant
        )

        url = reverse('token_obtain_pair')
        data = {
            "username": "acmeuser",
            "password": "SecurePassword123!"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_weak_password_fails_registration(self):
        url = reverse('auth_register')
        data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123",
            "company_name": "Weak Agency"
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
