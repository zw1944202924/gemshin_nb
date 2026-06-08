from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class Conversation(TimestampedModel):
    TITLE_SOURCE_AUTO = "auto"
    TITLE_SOURCE_MANUAL = "manual"
    TITLE_SOURCE_CHOICES = [
        (TITLE_SOURCE_AUTO, "Auto"),
        (TITLE_SOURCE_MANUAL, "Manual"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_conversations",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    title_source = models.CharField(
        max_length=20,
        choices=TITLE_SOURCE_CHOICES,
        default=TITLE_SOURCE_AUTO,
    )
    model_code = models.CharField(max_length=50, default="deepseek-chat")
    system_prompt = models.TextField(blank=True, default="")
    last_message_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_conversations"
        ordering = ["-last_message_at", "-updated_at", "-id"]
        indexes = [
            models.Index(fields=["user", "-last_message_at"], name="chat_conv_user_last_msg_idx"),
            models.Index(fields=["user", "deleted_at"], name="chat_conv_user_deleted_idx"),
        ]


class Message(TimestampedModel):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    STATUS_COMPLETED = "completed"
    STATUS_STREAMING = "streaming"
    STATUS_STOPPED = "stopped"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_COMPLETED, "Completed"),
        (STATUS_STREAMING, "Streaming"),
        (STATUS_STOPPED, "Stopped"),
        (STATUS_FAILED, "Failed"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content_markdown = models.TextField(blank=True, default="")
    content_text = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COMPLETED)
    sequence_no = models.IntegerField()
    reply_to_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assistant_replies",
    )
    provider_message_id = models.CharField(max_length=100, blank=True, default="")
    regen_from_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="regen_children",
    )
    error_code = models.CharField(max_length=50, blank=True, default="")
    error_message = models.CharField(max_length=255, blank=True, default="")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["sequence_no", "id"]
        indexes = [
            models.Index(fields=["conversation", "sequence_no"], name="chat_msg_conv_seq_idx"),
            models.Index(fields=["conversation", "created_at"], name="chat_msg_conv_created_idx"),
            models.Index(fields=["user", "conversation"], name="chat_msg_user_conv_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "sequence_no"],
                name="chat_msg_unique_sequence",
            )
        ]
