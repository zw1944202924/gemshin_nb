from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import AuditLog, Role, UserProfile, UserRole
from apps.core.authentication import build_auth_token
from apps.modules.models import Module

User = get_user_model()


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class ProfileAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.token = build_auth_token(self.user)
        self.profile = UserProfile.objects.create(
            user=self.user,
            display_name="测试用户",
            email="test@example.com",
        )

    def test_get_profile_requires_auth(self):
        response = self.client.get("/api/v1/accounts/profile/")
        self.assertEqual(response.status_code, 401)

    def test_get_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/accounts/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["display_name"], "测试用户")

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.patch(
            "/api/v1/accounts/profile/",
            {"profile": {"display_name": "新名称"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["display_name"], "新名称")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class ChangePasswordAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.token = build_auth_token(self.user)
        self.profile = UserProfile.objects.create(
            user=self.user,
            must_change_password=True,
        )

    def test_change_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.post(
            "/api/v1/accounts/change-password/",
            {"old_password": "testpass123", "new_password": "newpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))
        
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.must_change_password)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class AdminUserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_staff=True,
        )
        self.admin_token = build_auth_token(self.admin)
        UserProfile.objects.create(user=self.admin, must_change_password=False)
        
        self.normal_user = User.objects.create_user(
            username="normaluser",
            password="normalpass123",
        )
        UserProfile.objects.create(user=self.normal_user)
        
        self.role = Role.objects.create(
            name="测试角色",
            code="test_role",
        )

    def test_admin_list_users(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/v1/accounts/admin/users/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["users"]), 2)

    def test_non_admin_cannot_list_users(self):
        normal_token = build_auth_token(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {normal_token}")
        response = self.client.get("/api/v1/accounts/admin/users/")
        self.assertEqual(response.status_code, 403)

    def test_admin_create_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(
            "/api/v1/accounts/admin/users/",
            {
                "username": "newuser",
                "password": "newpass123",
                "display_name": "新用户",
                "email": "new@example.com",
                "role_ids": [self.role.id],
                "must_change_password": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "newuser")
        self.assertTrue(response.data["profile"]["must_change_password"])

    def test_admin_disable_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(f"/api/v1/accounts/admin/users/{self.normal_user.id}/disable/")
        self.assertEqual(response.status_code, 200)
        
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.is_active)

    def test_admin_cannot_disable_self(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(f"/api/v1/accounts/admin/users/{self.admin.id}/disable/")
        self.assertEqual(response.status_code, 400)

    def test_admin_reset_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(
            f"/api/v1/accounts/admin/users/{self.normal_user.id}/reset-password/",
            {"new_password": "resetpass123", "must_change_password": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.check_password("resetpass123"))


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class RoleAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_staff=True,
        )
        self.admin_token = build_auth_token(self.admin)
        
        self.role = Role.objects.create(
            name="测试角色",
            code="test_role",
        )

    def test_admin_list_roles(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/v1/accounts/admin/roles/")
        self.assertEqual(response.status_code, 200)
        # 包含种子数据的5个角色 + 测试创建的1个角色
        self.assertGreaterEqual(len(response.data["roles"]), 1)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class AuditLogAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_staff=True,
        )
        self.admin_token = build_auth_token(self.admin)
        
        AuditLog.objects.create(
            action="create_account",
            operator=self.admin,
            detail={"username": "testuser"},
        )

    def test_admin_list_audit_logs(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/v1/accounts/admin/audit-logs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["logs"]), 1)
