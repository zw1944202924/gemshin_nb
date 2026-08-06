from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Role, UserProfile, UserRole
from apps.core.authentication import build_auth_token
from apps.modules.models import Module


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class ModuleModelTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(
            code="comic",
            name="AI 漫剧制作一站式系统",
            description="测试模块",
            icon="🎬",
            sort_order=1,
        )

    def test_module_creation(self):
        self.assertEqual(str(self.module), "AI 漫剧制作一站式系统")
        self.assertEqual(self.module.code, "comic")

    def test_module_unique_code(self):
        with self.assertRaises(Exception):
            Module.objects.create(
                code="comic",
                name="重复模块",
            )


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class RoleModelTests(TestCase):
    def setUp(self):
        self.module_comic = Module.objects.create(
            code="comic",
            name="AI 漫剧制作一站式系统",
            icon="🎬",
        )
        self.module_stock = Module.objects.create(
            code="stock",
            name="AI 股票分析系统",
            icon="📊",
        )
        self.role = Role.objects.create(
            name="测试角色",
            code="test_role",
            description="测试角色描述",
        )
        self.role.modules.add(self.module_comic, self.module_stock)

    def test_role_creation(self):
        self.assertEqual(str(self.role), "测试角色")
        self.assertEqual(self.role.modules.count(), 2)

    def test_role_unique_code(self):
        with self.assertRaises(Exception):
            Role.objects.create(
                name="重复角色",
                code="test_role",
            )


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class UserRoleModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.role = Role.objects.create(
            name="测试角色",
            code="test_role",
        )

    def test_user_role_creation(self):
        user_role = UserRole.objects.create(user=self.user, role=self.role)
        self.assertEqual(str(user_role), f"{self.user} → {self.role}")

    def test_unique_constraint(self):
        UserRole.objects.create(user=self.user, role=self.role)
        with self.assertRaises(Exception):
            UserRole.objects.create(user=self.user, role=self.role)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class ModuleAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.token = build_auth_token(self.user)

        self.module_comic = Module.objects.create(
            code="comic",
            name="AI 漫剧制作一站式系统",
            icon="🎬",
            sort_order=1,
        )
        self.module_stock = Module.objects.create(
            code="stock",
            name="AI 股票分析系统",
            icon="📊",
            sort_order=2,
        )
        self.module_blog = Module.objects.create(
            code="blog",
            name="个人博客 / 个人内容库",
            icon="📝",
            sort_order=3,
        )

        # 创建角色
        self.role_comic = Role.objects.create(
            name="漫剧角色",
            code="comic_role",
        )
        self.role_comic.modules.add(self.module_comic)

        self.role_stock = Role.objects.create(
            name="股票角色",
            code="stock_role",
        )
        self.role_stock.modules.add(self.module_stock)

    def test_list_requires_authentication(self):
        response = self.client.get("/api/v1/modules/")
        self.assertEqual(response.status_code, 401)

    def test_empty_list_when_no_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["modules"], [])

    def test_list_blocked_when_user_must_change_password(self):
        UserProfile.objects.create(user=self.user, must_change_password=True)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "请先完成密码修改")

    def test_list_returns_only_authorized_modules(self):
        UserRole.objects.create(user=self.user, role=self.role_comic)
        UserRole.objects.create(user=self.user, role=self.role_stock)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["modules"]), 2)

        codes = [m["code"] for m in response.data["modules"]]
        self.assertIn("comic", codes)
        self.assertIn("stock", codes)
        self.assertNotIn("blog", codes)

    def test_detail_requires_authentication(self):
        response = self.client.get("/api/v1/modules/comic/")
        self.assertEqual(response.status_code, 401)

    def test_detail_returns_404_for_nonexistent_module(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/nonexistent/")
        self.assertEqual(response.status_code, 404)

    def test_detail_returns_403_for_unauthorized_module(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/comic/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "无权访问该模块")

    def test_detail_blocked_when_user_must_change_password(self):
        UserProfile.objects.create(user=self.user, must_change_password=True)
        UserRole.objects.create(user=self.user, role=self.role_comic)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/comic/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "请先完成密码修改")

    def test_detail_returns_module_when_authorized(self):
        UserRole.objects.create(user=self.user, role=self.role_comic)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/comic/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], "comic")
        self.assertEqual(response.data["name"], "AI 漫剧制作一站式系统")
