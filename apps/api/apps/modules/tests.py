from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.core.authentication import build_auth_token
from apps.modules.models import Module, UserModuleAuthorization


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
class AuthorizationModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.module = Module.objects.create(
            code="comic",
            name="AI 漫剧制作一站式系统",
            icon="🎬",
        )

    def test_authorization_creation(self):
        auth = UserModuleAuthorization.objects.create(
            user=self.user,
            module=self.module,
        )
        self.assertEqual(str(auth), f"{self.user} → {self.module}")

    def test_unique_constraint(self):
        UserModuleAuthorization.objects.create(
            user=self.user,
            module=self.module,
        )
        with self.assertRaises(Exception):
            UserModuleAuthorization.objects.create(
                user=self.user,
                module=self.module,
            )


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

    def test_list_requires_authentication(self):
        response = self.client.get("/api/v1/modules/")
        self.assertEqual(response.status_code, 401)

    def test_empty_list_when_no_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["modules"], [])

    def test_list_returns_only_authorized_modules(self):
        UserModuleAuthorization.objects.create(
            user=self.user,
            module=self.module_comic,
        )
        UserModuleAuthorization.objects.create(
            user=self.user,
            module=self.module_stock,
        )

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

    def test_detail_returns_module_when_authorized(self):
        UserModuleAuthorization.objects.create(
            user=self.user,
            module=self.module_comic,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/v1/modules/comic/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], "comic")
        self.assertEqual(response.data["name"], "AI 漫剧制作一站式系统")
