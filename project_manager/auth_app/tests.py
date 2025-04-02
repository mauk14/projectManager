from django.test import TestCase
from rest_framework.test import APITestCase
from .models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class AuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="TestPassword123")
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.logout_url = "/api/auth/logout/"

    def test_register_user(self):
        data = {"username": "newuser", "email": "new@example.com", "password": "newpassword"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_user_invalid_data(self):
        data = {"username": "", "password": "short"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        data = {"username": "testuser", "email": "unique@example.com", "password": "testpassword"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_email(self):
        data = {"username": "uniqueuser", "email": "test@example.com", "password": "testpassword"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_successful(self):
        data = {"username": "testuser", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)    

    def test_logout_successful(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post(self.logout_url, {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)    

    def test_logout_without_token(self):
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)    

    def test_logout_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.post(self.logout_url, {"refresh": "invalid_token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)