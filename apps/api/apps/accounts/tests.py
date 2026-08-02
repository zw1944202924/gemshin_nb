from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
import os

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

    def test_admin_list_users_returns_roles(self):
        """验证管理员用户列表返回 roles 字段"""
        UserRole.objects.create(user=self.admin, role=self.role)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/v1/accounts/admin/users/")
        self.assertEqual(response.status_code, 200)
        
        # 查找 admin 用户并验证 roles 字段
        admin_data = next(u for u in response.data["users"] if u["username"] == "admin")
        self.assertIsNotNone(admin_data.get("roles"))
        self.assertEqual(len(admin_data["roles"]), 1)
        self.assertEqual(admin_data["roles"][0]["code"], "test_role")

    def test_admin_detail_user_returns_roles(self):
        """验证管理员用户详情返回 roles 字段"""
        UserRole.objects.create(user=self.normal_user, role=self.role)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(f"/api/v1/accounts/admin/users/{self.normal_user.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get("roles"))
        self.assertEqual(len(response.data["roles"]), 1)
        self.assertEqual(response.data["roles"][0]["code"], "test_role")

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

    def test_admin_create_user_returns_roles(self):
        """验证创建用户后返回的响应包含 roles 字段"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(
            "/api/v1/accounts/admin/users/",
            {
                "username": "newuser_with_roles",
                "password": "newpass123",
                "role_ids": [self.role.id],
                "must_change_password": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data.get("roles"))
        self.assertEqual(len(response.data["roles"]), 1)
        self.assertEqual(response.data["roles"][0]["code"], "test_role")

    def test_admin_update_user_roles(self):
        """验证更新用户角色后返回的响应包含更新后的 roles"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        
        # 先创建一个新角色
        new_role = Role.objects.create(name="新角色", code="new_role")
        
        # 更新用户角色
        response = self.client.patch(
            f"/api/v1/accounts/admin/users/{self.normal_user.id}/",
            {"role_ids": [self.role.id, new_role.id]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get("roles"))
        self.assertEqual(len(response.data["roles"]), 2)
        role_codes = [r["code"] for r in response.data["roles"]]
        self.assertIn("test_role", role_codes)
        self.assertIn("new_role", role_codes)

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


class SeedRolesCommandTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="zhangwei", password="oldpass123")
        self.comic = Module.objects.create(code="comic", name="漫剧", sort_order=1)
        self.stock = Module.objects.create(code="stock", name="股票", sort_order=2)
        self.blog = Module.objects.create(code="blog", name="内容库", sort_order=3)
        self.original_admin_password = os.environ.get("ADMIN_PASSWORD")
        os.environ["ADMIN_PASSWORD"] = "newpass123"
        self.addCleanup(self.restore_admin_password)

    def restore_admin_password(self):
        if self.original_admin_password is None:
            os.environ.pop("ADMIN_PASSWORD", None)
        else:
            os.environ["ADMIN_PASSWORD"] = self.original_admin_password

    def test_seed_roles_repairs_existing_admin_modules(self):
        admin_role = Role.objects.get(code="admin")
        admin_role.name = "管理员旧数据"
        admin_role.description = "旧管理员角色"
        admin_role.sort_order = 99
        admin_role.save()
        admin_role.modules.set([self.comic])

        call_command("seed_roles", admin_username="zhangwei")

        admin_role.refresh_from_db()
        self.assertTrue(self.admin.user_roles.filter(role=admin_role).exists())
        self.assertEqual(
            list(admin_role.modules.order_by("sort_order").values_list("code", flat=True)),
            ["comic", "stock", "blog"],
        )

    def test_seed_roles_supports_content_module_alias(self):
        self.blog.delete()
        content = Module.objects.create(code="content", name="内容库", sort_order=3)

        call_command("seed_roles", admin_username="zhangwei")

        admin_role = Role.objects.get(code="admin")
        content_role = Role.objects.get(code="content_creator")

        self.assertEqual(
            list(admin_role.modules.order_by("sort_order").values_list("code", flat=True)),
            ["comic", "stock", "content"],
        )
        self.assertEqual(
            list(content_role.modules.values_list("code", flat=True)),
            [content.code],
        )
