import json
from hashlib import sha256
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from jwcrypto import jwk, jwt
from jwcrypto.common import base64url_encode
from oauth2_provider.models import get_application_model

from apps.accounts.models import Role, UserProfile, UserRole
from apps.core.authentication import build_auth_token
from apps.oidc.keys import (
    get_oidc_private_key,
    get_test_oidc_private_key,
    is_local_debug_environment,
    is_test_settings_module,
)
from apps.oidc.session import invalidate_user_sessions


Application = get_application_model()
User = get_user_model()


class OidcKeyConfigTests(TestCase):
    def test_missing_private_key_raises_outside_test_settings(self):
        with patch.dict("os.environ", {"OIDC_RSA_PRIVATE_KEY": "", "DJANGO_SETTINGS_MODULE": "config.settings.base"}):
            self.assertFalse(is_test_settings_module())
            with self.assertRaisesMessage(ImproperlyConfigured, "OIDC_RSA_PRIVATE_KEY"):
                get_oidc_private_key()

    def test_local_debug_environment_allows_ephemeral_private_key(self):
        self.assertTrue(is_local_debug_environment(debug=True, allowed_hosts=["127.0.0.1", "localhost"]))
        with patch.dict("os.environ", {"OIDC_RSA_PRIVATE_KEY": ""}):
            self.assertTrue(get_oidc_private_key(allow_ephemeral=True).startswith("-----BEGIN PRIVATE KEY-----"))

    def test_non_local_debug_environment_does_not_allow_ephemeral_private_key(self):
        self.assertFalse(is_local_debug_environment(debug=True, allowed_hosts=["example.com"]))


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class OidcFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="oidc-user",
            password="pass123456",
            first_name="Unified",
            last_name="Identity",
        )
        UserProfile.objects.create(
            user=self.user,
            display_name="统一身份用户",
            email="oidc@example.com",
            must_change_password=False,
        )
        self.application = Application.objects.create(
            name="new_api",
            user=self.user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="https://new-api.example.com/callback",
            post_logout_redirect_uris="https://new-api.example.com/logout/callback",
            algorithm=Application.RS256_ALGORITHM,
            skip_authorization=True,
        )
        self.redirect_uri = "https://new-api.example.com/callback"
        self.code_verifier = "verifier-1234567890-abcdef"
        self.code_challenge = base64url_encode(sha256(self.code_verifier.encode("ascii")).digest())

    def _authorize(self, **extra_params):
        self.client.force_login(self.user)
        params = {
            "response_type": "code",
            "client_id": self.application.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email",
            "state": "state-123",
            "nonce": "nonce-123",
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
        params.update(extra_params)
        return self.client.get("/api/v1/oidc/authorize/", params)

    def _exchange_code(self, code, **extra_data):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.application.client_id,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_verifier,
        }
        data.update(extra_data)
        return self.client.post("/api/v1/oidc/token/", data)

    def _decode_id_token(self, raw_token):
        private_key = jwk.JWK.from_pem(get_test_oidc_private_key().encode("utf-8"))
        public_key = jwk.JWK()
        public_key.import_key(**private_key.export_public(as_dict=True))
        parsed = jwt.JWT(key=public_key, jwt=raw_token)
        return json.loads(parsed.claims)

    def test_discovery_and_jwks_endpoints_expose_oidc_metadata(self):
        response = self.client.get("/api/v1/oidc/.well-known/openid-configuration")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["issuer"], "http://testserver/api/v1/oidc")
        self.assertEqual(payload["response_types_supported"], ["code"])
        self.assertEqual(payload["code_challenge_methods_supported"], ["S256"])
        self.assertIn("preferred_username", payload["claims_supported"])

        jwks_response = self.client.get("/api/v1/oidc/.well-known/jwks.json")
        self.assertEqual(jwks_response.status_code, 200)
        self.assertEqual(len(jwks_response.json()["keys"]), 1)

    def test_authorization_code_pkce_flow_returns_expected_claims_and_state_nonce(self):
        response = self._authorize()
        self.assertEqual(response.status_code, 302)

        query = parse_qs(urlparse(response["Location"]).query)
        self.assertEqual(query["state"][0], "state-123")
        self.assertIn("code", query)

        token_response = self._exchange_code(query["code"][0])
        self.assertEqual(token_response.status_code, 200)
        body = token_response.json()
        self.assertIn("id_token", body)
        self.assertIn("refresh_token", body)

        claims = self._decode_id_token(body["id_token"])
        self.assertEqual(claims["nonce"], "nonce-123")
        self.assertEqual(claims["preferred_username"], "oidc-user")
        self.assertEqual(claims["name"], "统一身份用户")
        self.assertEqual(claims["email"], "oidc@example.com")

        userinfo = self.client.get(
            "/api/v1/oidc/userinfo/",
            HTTP_AUTHORIZATION=f"Bearer {body['access_token']}",
        )
        self.assertEqual(userinfo.status_code, 200)
        self.assertEqual(userinfo.json()["sub"], claims["sub"])

    def test_missing_pkce_returns_oauth_error_callback(self):
        response = self._authorize(code_challenge="", code_challenge_method="")
        self.assertEqual(response.status_code, 302)

        query = parse_qs(urlparse(response["Location"]).query)
        self.assertEqual(query["error"][0], "invalid_request")
        self.assertEqual(query["state"][0], "state-123")

    def test_authorization_code_can_only_be_used_once(self):
        response = self._authorize()
        code = parse_qs(urlparse(response["Location"]).query)["code"][0]

        first = self._exchange_code(code)
        second = self._exchange_code(code)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(second.json()["error"], "invalid_grant")

    def test_disabled_account_cannot_continue_using_oidc_access_token(self):
        response = self._authorize()
        code = parse_qs(urlparse(response["Location"]).query)["code"][0]
        token_response = self._exchange_code(code)
        access_token = token_response.json()["access_token"]

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        invalidate_user_sessions(self.user)

        userinfo = self.client.get(
            "/api/v1/oidc/userinfo/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(userinfo.status_code, 401)

    def test_rp_logout_redirects_and_revokes_refresh_token(self):
        response = self._authorize()
        code = parse_qs(urlparse(response["Location"]).query)["code"][0]
        token_response = self._exchange_code(code)
        body = token_response.json()

        self.client.force_login(self.user)
        logout_response = self.client.get(
            "/api/v1/oidc/logout/",
            {
                "id_token_hint": body["id_token"],
                "client_id": self.application.client_id,
                "post_logout_redirect_uri": "https://new-api.example.com/logout/callback",
                "state": "logout-123",
            },
        )

        self.assertEqual(logout_response.status_code, 302)
        self.assertIn("logout-123", logout_response["Location"])

        refresh_response = self.client.post(
            "/api/v1/oidc/token/",
            {
                "grant_type": "refresh_token",
                "client_id": self.application.client_id,
                "refresh_token": body["refresh_token"],
            },
        )
        self.assertEqual(refresh_response.status_code, 400)
        self.assertEqual(refresh_response.json()["error"], "invalid_grant")


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class SessionInvalidationRegressionTests(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.get(code="admin")
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_staff=True,
        )
        UserProfile.objects.create(user=self.admin, display_name="管理员", must_change_password=False)
        UserRole.objects.create(user=self.admin, role=self.admin_role)
        self.admin_token = build_auth_token(self.admin)

        self.user = User.objects.create_user(
            username="member",
            password="memberpass123",
        )
        UserProfile.objects.create(user=self.user, display_name="普通成员", email="member@example.com")
        self.user_token = build_auth_token(self.user)

        self.application = Application.objects.create(
            name="new_api",
            user=self.admin,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="https://new-api.example.com/callback",
            algorithm=Application.RS256_ALGORITHM,
            skip_authorization=True,
        )

    def _issue_refresh_token(self):
        verifier = "refresh-verifier-123456789"
        code_challenge = base64url_encode(sha256(verifier.encode("ascii")).digest())

        self.client.force_login(self.user)
        authorize = self.client.get(
            "/api/v1/oidc/authorize/",
            {
                "response_type": "code",
                "client_id": self.application.client_id,
                "redirect_uri": "https://new-api.example.com/callback",
                "scope": "openid profile",
                "state": "refresh-state",
                "nonce": "refresh-nonce",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
        )
        code = parse_qs(urlparse(authorize["Location"]).query)["code"][0]
        token_response = self.client.post(
            "/api/v1/oidc/token/",
            {
                "grant_type": "authorization_code",
                "client_id": self.application.client_id,
                "code": code,
                "redirect_uri": "https://new-api.example.com/callback",
                "code_verifier": verifier,
            },
        )
        self.assertEqual(token_response.status_code, 200)
        return token_response.json()["refresh_token"]

    def test_change_password_invalidates_existing_local_token_and_oidc_refresh_token(self):
        refresh_token = self._issue_refresh_token()

        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {self.user_token}"
        response = self.client.post(
            "/api/v1/accounts/change-password/",
            data=json.dumps({"old_password": "memberpass123", "new_password": "memberpass456"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        me_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me_response.status_code, 401)

        refresh_response = self.client.post(
            "/api/v1/oidc/token/",
            {
                "grant_type": "refresh_token",
                "client_id": self.application.client_id,
                "refresh_token": refresh_token,
            },
        )
        self.assertEqual(refresh_response.status_code, 400)
        self.assertEqual(refresh_response.json()["error"], "invalid_grant")

    def test_admin_reset_password_invalidates_oidc_refresh_token(self):
        refresh_token = self._issue_refresh_token()

        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {self.admin_token}"
        response = self.client.post(
            f"/api/v1/accounts/admin/users/{self.user.id}/reset-password/",
            data=json.dumps({"new_password": "memberpass789", "must_change_password": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        refresh_response = self.client.post(
            "/api/v1/oidc/token/",
            {
                "grant_type": "refresh_token",
                "client_id": self.application.client_id,
                "refresh_token": refresh_token,
            },
        )
        self.assertEqual(refresh_response.status_code, 400)
        self.assertEqual(refresh_response.json()["error"], "invalid_grant")
