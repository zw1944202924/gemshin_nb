from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
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
        UserProfile.objects.create(
            user=self.user,
            display_name="Demo User",
            must_change_password=False,
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
        self.assertIn("roles", response.data["user"])
        self.assertIn("must_change_password", response.data["user"])

    def test_invalid_credentials_return_400(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "demo", "password": "bad-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "用户名或密码错误")

    def test_disabled_user_cannot_login(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "demo", "password": "pass123456"},
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

    def test_must_change_password_user_can_access_session_but_not_protected_endpoint(self):
        profile = self.user.profile
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password"])

        token = build_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        session_response = self.client.get("/api/v1/auth/me/")
        protected_response = self.client.get("/api/v1/protected/")

        self.assertEqual(session_response.status_code, 200)
        self.assertTrue(session_response.data["user"]["must_change_password"])
        self.assertEqual(protected_response.status_code, 403)
        self.assertEqual(protected_response.data["detail"], "请先完成密码修改")

    def test_must_change_password_user_can_logout(self):
        profile = self.user.profile
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password"])

        token = build_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        logout_response = self.client.post("/api/v1/auth/logout/")
        self.assertEqual(logout_response.status_code, 204)

        session_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(session_response.status_code, 401)

    def test_logout_revokes_current_token(self):
        token = build_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        logout_response = self.client.post("/api/v1/auth/logout/")
        self.assertEqual(logout_response.status_code, 204)

        session_response = self.client.get("/api/v1/auth/me/")
        protected_response = self.client.get("/api/v1/protected/")

        self.assertEqual(session_response.status_code, 401)
        self.assertEqual(protected_response.status_code, 401)

    def test_deactivated_user_existing_token_is_rejected(self):
        token = build_auth_token(self.user)
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        session_response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(session_response.status_code, 401)

    def test_new_api_proxy_auth_accepts_gemshin_cookie(self):
        token = build_auth_token(self.user)
        self.client.cookies["gemshin_token"] = token

        response = self.client.get("/api/v1/assistant/new-api/auth/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["X-Gemshin-User-Id"], str(self.user.pk))
        self.assertEqual(response["X-Gemshin-Username"], "demo")
        self.assertEqual(response["X-Gemshin-Oidc-Subject"], str(self.user.profile.oidc_subject))

    def test_new_api_proxy_auth_rejects_missing_or_revoked_session(self):
        denied = self.client.get("/api/v1/assistant/new-api/auth/")
        self.assertEqual(denied.status_code, 401)

        token = build_auth_token(self.user)
        self.client.cookies["gemshin_token"] = token
        self.user.profile.auth_revoked_at = timezone.now()
        self.user.profile.save(update_fields=["auth_revoked_at"])

        revoked = self.client.get("/api/v1/assistant/new-api/auth/")
        self.assertEqual(revoked.status_code, 401)

    def test_new_api_proxy_auth_rejects_must_change_password_user(self):
        self.user.profile.must_change_password = True
        self.user.profile.save(update_fields=["must_change_password"])
        self.client.cookies["gemshin_token"] = build_auth_token(self.user)

        response = self.client.get("/api/v1/assistant/new-api/auth/")

        self.assertEqual(response.status_code, 403)
