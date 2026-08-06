from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
from apps.core.authentication import build_auth_token


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class StoryPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="story-user",
            password="storypass123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            must_change_password=True,
        )
        self.token = build_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_must_change_password_blocks_story_endpoints(self):
        response = self.client.get("/api/v1/story/projects/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "请先完成密码修改")

    def test_story_endpoints_recover_after_change_password(self):
        blocked_response = self.client.get("/api/v1/story/projects/")
        self.assertEqual(blocked_response.status_code, 403)

        change_response = self.client.post(
            "/api/v1/accounts/change-password/",
            {"old_password": "storypass123", "new_password": "storypass456"},
            format="json",
        )
        self.assertEqual(change_response.status_code, 200)

        create_response = self.client.post(
            "/api/v1/story/projects/",
            {"title": "改密后项目", "description": "恢复访问"},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.data["title"], "改密后项目")

        list_response = self.client.get("/api/v1/story/projects/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["title"], "改密后项目")
