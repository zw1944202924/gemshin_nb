from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.core.authentication import build_auth_token


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="demo",
            password="pass123456",
            first_name="Demo",
            last_name="User",
        )

    def test_login_returns_token_and_user(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "demo", "password": "pass123456"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "demo")

    def test_invalid_credentials_return_400(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "demo", "password": "bad-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "用户名或密码错误")

    def test_authenticated_endpoints_require_bearer_token(self):
        token = build_auth_token(self.user)

        denied = self.client.get("/api/v1/auth/me/")
        self.assertEqual(denied.status_code, 401)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        session_response = self.client.get("/api/v1/auth/me/")
        protected_response = self.client.get("/api/v1/protected/")

        self.assertEqual(session_response.status_code, 200)
        self.assertEqual(session_response.data["user"]["username"], "demo")
        self.assertEqual(protected_response.status_code, 200)
        self.assertEqual(protected_response.data["scope"], "authenticated")
