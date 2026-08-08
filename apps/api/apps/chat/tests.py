import json
import threading
from unittest import mock, skipUnless

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
from apps.chat.models import Conversation, Message
from apps.chat.services import chat as chat_service
from apps.core.authentication import build_auth_token


class FakeProvider:
    chunks = ["第一段", "第二段"]
    fail_message = ""

    def stream_messages(self, messages, *, model_code, system_prompt=""):
        if self.fail_message:
            from apps.chat.services.providers.base import ProviderError

            raise ProviderError(self.fail_message)

        from apps.chat.services.providers.base import ProviderChunk

        for chunk in self.chunks:
            yield ProviderChunk(delta_text=chunk, provider_message_id="provider-msg-1")


class EmojiFakeProvider:
    chunks = ["Hello 😊", " World 🌍"]
    fail_message = ""

    def stream_messages(self, messages, *, model_code, system_prompt=""):
        if self.fail_message:
            from apps.chat.services.providers.base import ProviderError

            raise ProviderError(self.fail_message)

        from apps.chat.services.providers.base import ProviderChunk

        for chunk in self.chunks:
            yield ProviderChunk(delta_text=chunk, provider_message_id="provider-msg-emoji")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    CHAT_PROVIDER_CLASS="apps.chat.tests.FakeProvider",
)
class ChatFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="demo", password="pass123456")
        self.other_user = get_user_model().objects.create_user(username="other", password="pass123456")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {build_auth_token(self.user)}")

    def _parse_sse(self, response):
        body = b"".join(response.streaming_content).decode("utf-8")
        events = []
        for block in body.strip().split("\n\n"):
            lines = block.splitlines()
            event_name = lines[0].split(": ", 1)[1]
            payload = json.loads(lines[1].split(": ", 1)[1])
            events.append((event_name, payload))
        return events

    def test_conversation_crud_and_history(self):
        created = self.client.post("/api/v1/chat/conversations/", {"title": ""}, format="json")
        self.assertEqual(created.status_code, 201)
        conversation_id = created.data["id"]

        renamed = self.client.patch(
            f"/api/v1/chat/conversations/{conversation_id}/",
            {"title": "周会待办"},
            format="json",
        )
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.data["title_source"], "manual")

        detail = self.client.get(f"/api/v1/chat/conversations/{conversation_id}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["conversation"]["title"], "周会待办")
        self.assertEqual(detail.data["messages"], [])

        deleted = self.client.delete(f"/api/v1/chat/conversations/{conversation_id}/")
        self.assertEqual(deleted.status_code, 204)

        listing = self.client.get("/api/v1/chat/conversations/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data["items"], [])

    def test_create_conversation_rejects_overlong_title(self):
        response = self.client.post(
            "/api/v1/chat/conversations/",
            {"title": "x" * 81},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["title"], "标题长度不能超过 80 个字符")

    def test_stream_message_creates_user_and_assistant_messages(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")

        response = self.client.post(
            f"/api/v1/chat/conversations/{conversation.id}/messages/stream/",
            {"content": "帮我整理本周计划", "client_message_id": "msg-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        events = self._parse_sse(response)
        self.assertEqual(
            [event[0] for event in events],
            ["conversation.meta", "message.delta", "message.delta", "message.done"],
        )

        conversation.refresh_from_db()
        messages = list(Message.objects.filter(conversation=conversation).order_by("sequence_no"))
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].status, "completed")
        self.assertEqual(messages[1].content_markdown, "第一段第二段")
        self.assertEqual(conversation.title, "帮我整理本周计划")

    def test_duplicate_message_request_returns_reused_snapshot(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        first = self.client.post(
            f"/api/v1/chat/conversations/{conversation.id}/messages/stream/",
            {"content": "第一次提问", "client_message_id": "dup-1"},
            format="json",
        )
        self.assertEqual(first.status_code, 200)
        self._parse_sse(first)

        second = self.client.post(
            f"/api/v1/chat/conversations/{conversation.id}/messages/stream/",
            {"content": "第一次提问", "client_message_id": "dup-1"},
            format="json",
        )
        self.assertEqual(second.status_code, 200)
        events = self._parse_sse(second)
        self.assertEqual(events[0][0], "message.snapshot")
        self.assertTrue(events[0][1]["reused"])

    def test_stop_generation_requires_streaming_message(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        user_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="user",
            content_markdown="hi",
            content_text="hi",
            status="completed",
            sequence_no=1,
        )
        assistant_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="assistant",
            status="streaming",
            sequence_no=2,
            reply_to_message=user_message,
        )

        response = self.client.post(f"/api/v1/chat/messages/{assistant_message.id}/stop/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "stopping")

    def test_regenerate_creates_new_assistant_version(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        user_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="user",
            content_markdown="原问题",
            content_text="原问题",
            status="completed",
            sequence_no=1,
        )
        assistant_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="assistant",
            content_markdown="旧回答",
            content_text="旧回答",
            status="completed",
            sequence_no=2,
            reply_to_message=user_message,
        )

        response = self.client.post(
            f"/api/v1/chat/messages/{assistant_message.id}/regenerate/",
            {"client_request_id": "regen-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self._parse_sse(response)

        regenerated = Message.objects.filter(regen_from_message=assistant_message).get()
        self.assertEqual(regenerated.status, "completed")
        self.assertEqual(regenerated.content_markdown, "第一段第二段")

        detail = self.client.get(f"/api/v1/chat/conversations/{conversation.id}/")
        assistant_versions = [item for item in detail.data["messages"] if item["role"] == "assistant"]
        self.assertEqual(len(assistant_versions), 2)
        self.assertFalse(assistant_versions[0]["is_current_version"])
        self.assertTrue(assistant_versions[1]["is_current_version"])

    def test_regenerate_failed_keeps_old_version_current(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        user_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="user",
            content_markdown="原问题",
            content_text="原问题",
            status="completed",
            sequence_no=1,
        )
        assistant_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="assistant",
            content_markdown="旧回答",
            content_text="旧回答",
            status="completed",
            sequence_no=2,
            reply_to_message=user_message,
        )

        with mock.patch("apps.chat.tests.FakeProvider.fail_message", "模拟失败"):
            response = self.client.post(
                f"/api/v1/chat/messages/{assistant_message.id}/regenerate/",
                {"client_request_id": "regen-fail-1"},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            self._parse_sse(response)

        regenerated = Message.objects.filter(regen_from_message=assistant_message).get()
        self.assertEqual(regenerated.status, "failed")

        detail = self.client.get(f"/api/v1/chat/conversations/{conversation.id}/")
        assistant_versions = [item for item in detail.data["messages"] if item["role"] == "assistant"]
        self.assertEqual(len(assistant_versions), 2)
        self.assertTrue(assistant_versions[0]["is_current_version"])
        self.assertTrue(assistant_versions[1]["is_current_version"])

    def test_regenerate_completed_replaces_old_version(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        user_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="user",
            content_markdown="原问题",
            content_text="原问题",
            status="completed",
            sequence_no=1,
        )
        assistant_message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="assistant",
            content_markdown="旧回答",
            content_text="旧回答",
            status="completed",
            sequence_no=2,
            reply_to_message=user_message,
        )

        response = self.client.post(
            f"/api/v1/chat/messages/{assistant_message.id}/regenerate/",
            {"client_request_id": "regen-stop-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self._parse_sse(response)

        regenerated = Message.objects.filter(regen_from_message=assistant_message).get()
        self.assertEqual(regenerated.status, "completed")

        detail = self.client.get(f"/api/v1/chat/conversations/{conversation.id}/")
        assistant_versions = [item for item in detail.data["messages"] if item["role"] == "assistant"]
        self.assertEqual(len(assistant_versions), 2)
        self.assertFalse(assistant_versions[0]["is_current_version"])
        self.assertTrue(assistant_versions[1]["is_current_version"])

    def test_message_detail_and_user_isolation(self):
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="assistant",
            content_markdown="可见消息",
            content_text="可见消息",
            status="completed",
            sequence_no=1,
        )

        detail = self.client.get(f"/api/v1/chat/messages/{message.id}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["content_markdown"], "可见消息")

        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {build_auth_token(self.other_user)}")
        denied = other_client.get(f"/api/v1/chat/messages/{message.id}/")
        self.assertEqual(denied.status_code, 404)

    def test_must_change_password_blocks_chat_endpoints(self):
        UserProfile.objects.create(user=self.user, must_change_password=True)

        response = self.client.get("/api/v1/chat/conversations/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "请先完成密码修改")

    @override_settings(
        CHAT_PROVIDER_CLASS="apps.chat.tests.EmojiFakeProvider",
    )
    def test_emoji_characters_persist_successfully(self):
        """Test that emoji and other 4-byte Unicode characters can be stored and retrieved."""
        conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        
        # Test with various emoji characters
        emoji_content = "Hello 😊 World 🌍 Test 🎉 Emoji 🚀"
        message = Message.objects.create(
            conversation=conversation,
            user=self.user,
            role="assistant",
            content_markdown=emoji_content,
            content_text=emoji_content,
            status="completed",
            sequence_no=1,
        )
        
        # Refresh from database
        message.refresh_from_db()
        self.assertEqual(message.content_markdown, emoji_content)
        self.assertEqual(message.content_text, emoji_content)
        
        # Test via API
        detail = self.client.get(f"/api/v1/chat/messages/{message.id}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["content_markdown"], emoji_content)
        
        # Test streaming with emoji content
        conversation2 = Conversation.objects.create(user=self.user, model_code="deepseek-chat")
        response = self.client.post(
            f"/api/v1/chat/conversations/{conversation2.id}/messages/stream/",
            {"content": "帮我写一个包含emoji的回复 😊", "client_message_id": "emoji-test-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        events = self._parse_sse(response)
        self.assertEqual(
            [event[0] for event in events],
            ["conversation.meta", "message.delta", "message.delta", "message.done"],
        )
        
        # Verify the assistant message was saved with emoji content
        assistant_message = Message.objects.filter(
            conversation=conversation2, 
            role="assistant"
        ).first()
        self.assertIsNotNone(assistant_message)
        self.assertEqual(assistant_message.status, "completed")
        self.assertIn("😊", assistant_message.content_markdown)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
class ChatConcurrencyTests(TransactionTestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(username="concurrent", password="pass123456")
        self.conversation = Conversation.objects.create(user=self.user, model_code="deepseek-chat")

    def test_same_conversation_only_allows_one_streaming_message(self):
        start_event = threading.Event()
        release_event = threading.Event()
        original_next_sequence_no = chat_service._next_sequence_no
        results = []
        errors = []

        def slow_next_sequence_no(conversation):
            if threading.current_thread().name == "worker-1" and not start_event.is_set():
                start_event.set()
                release_event.wait(timeout=2)
            return original_next_sequence_no(conversation)

        def worker(name, content):
            close_old_connections()
            try:
                _, user_message, assistant_message = chat_service.create_message_pair_for_stream(
                    conversation=self.conversation,
                    user=self.user,
                    content=content,
                )
                results.append((name, user_message.id, assistant_message.id))
            except Exception as exc:  # noqa: BLE001
                errors.append((name, exc))
            finally:
                close_old_connections()

        with mock.patch("apps.chat.services.chat._next_sequence_no", side_effect=slow_next_sequence_no):
            first_thread = threading.Thread(
                target=worker,
                name="worker-1",
                args=("worker-1", "第一个请求"),
            )
            second_thread = threading.Thread(
                target=worker,
                name="worker-2",
                args=("worker-2", "第二个请求"),
            )
            first_thread.start()
            self.assertTrue(start_event.wait(timeout=2))
            second_thread.start()
            release_event.set()
            first_thread.join(timeout=5)
            second_thread.join(timeout=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            Message.objects.filter(
                conversation=self.conversation,
                role=Message.ROLE_ASSISTANT,
                status=Message.STATUS_STREAMING,
            ).count(),
            1,
        )
        self.assertIn("当前会话仍有消息在生成中", str(errors[0][1]))


class MySQLCharsetValidationTests(TestCase):
    """MySQL 字符集回归验证：仅在 MySQL 环境下执行，保证 utf8mb4 路径真实生效。

    注意：当前测试配置默认走 SQLite（config.settings.test），因此本类用例会被自动跳过。
    部署到 MySQL 环境后，这些用例将在 CI 中真实通过，才能证明本次修复已覆盖生产路径。
    """

    @skipUnless(connection.vendor == 'mysql', 'MySQL charset test requires MySQL backend')
    def test_charset_is_utf8mb4(self):
        with connection.cursor() as cursor:
            cursor.execute("SHOW VARIABLES LIKE 'character_set_connection'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[1], 'utf8mb4', '连接字符集必须为 utf8mb4，否则 emoji 写库会失败')

            cursor.execute("SHOW VARIABLES LIKE 'collation_connection'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertTrue(
                row[1].startswith('utf8mb4'),
                f'连接排序规则必须为 utf8mb4 系列，当前为 {row[1]}',
            )

    @skipUnless(connection.vendor == 'mysql', 'MySQL charset test requires MySQL backend')
    def test_chat_message_columns_are_utf8mb4(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COLUMN_NAME, CHARACTER_SET_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'chat_messages' "
                "AND COLUMN_NAME IN ('content_markdown', 'content_text')"
            )
            columns = {row[0]: row[1] for row in cursor.fetchall()}
            self.assertEqual(columns.get('content_markdown'), 'utf8mb4')
            self.assertEqual(columns.get('content_text'), 'utf8mb4')
