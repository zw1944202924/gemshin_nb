import json
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework import exceptions

from apps.chat.models import Conversation, Message
from apps.chat.services.providers.base import ProviderError


STOP_KEY_PREFIX = "chat:stop"
IDEM_MESSAGE_KEY_PREFIX = "chat:idem:message"
IDEM_REGEN_KEY_PREFIX = "chat:idem:regen"


class ConflictError(exceptions.APIException):
    status_code = 409
    default_detail = "冲突"
    default_code = "conflict"


class StopGeneration(Exception):
    pass


@dataclass
class MessageVersionInfo:
    is_current_version: bool
    superseded_by_message_id: int | None


def trim_text(value, limit=None):
    collapsed = " ".join((value or "").split())
    if limit and len(collapsed) > limit:
        return f"{collapsed[: limit - 1].rstrip()}…"
    return collapsed


def conversation_queryset_for_user(user):
    return Conversation.objects.filter(user=user, deleted_at__isnull=True)


def message_queryset_for_user(user):
    return Message.objects.filter(user=user, conversation__deleted_at__isnull=True)


def get_conversation_for_user(user, conversation_id):
    try:
        return conversation_queryset_for_user(user).get(pk=conversation_id)
    except Conversation.DoesNotExist as exc:
        raise exceptions.NotFound("会话不存在") from exc


def get_message_for_user(user, message_id):
    try:
        return message_queryset_for_user(user).select_related("conversation", "reply_to_message").get(pk=message_id)
    except Message.DoesNotExist as exc:
        raise exceptions.NotFound("消息不存在") from exc


def build_version_map(messages):
    superseded_map = {}
    for message in messages:
        if message.regen_from_message_id:
            superseded_map[message.regen_from_message_id] = message.id

    version_map = {}
    for message in messages:
        if message.role != Message.ROLE_ASSISTANT:
            continue
        superseded_by = superseded_map.get(message.id)
        version_map[message.id] = MessageVersionInfo(
            is_current_version=superseded_by is None,
            superseded_by_message_id=superseded_by,
        )
    return version_map


def serialize_conversation(conversation):
    return {
        "id": conversation.id,
        "title": conversation.title,
        "title_source": conversation.title_source,
        "model_code": conversation.model_code,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


def serialize_message(message, version_map):
    payload = {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content_markdown": message.content_markdown,
        "status": message.status,
        "sequence_no": message.sequence_no,
        "reply_to_message_id": message.reply_to_message_id,
        "regen_from_message_id": message.regen_from_message_id,
        "error_code": message.error_code or None,
        "error_message": message.error_message or None,
        "created_at": message.created_at,
        "completed_at": message.completed_at,
    }
    if message.role == Message.ROLE_ASSISTANT:
        version_info = version_map.get(message.id, MessageVersionInfo(True, None))
        payload["is_current_version"] = version_info.is_current_version
        payload["superseded_by_message_id"] = version_info.superseded_by_message_id
    return payload


def serialize_message_detail(message):
    version_map = build_version_map(
        list(Message.objects.filter(conversation=message.conversation).order_by("sequence_no", "id"))
    )
    return serialize_message(message, version_map)


def list_conversation_items(user, limit):
    conversations = list(
        conversation_queryset_for_user(user)
        .prefetch_related("messages")
        .order_by("-last_message_at", "-updated_at", "-id")[:limit]
    )
    items = []
    for conversation in conversations:
        messages = list(conversation.messages.all().order_by("sequence_no", "id"))
        version_map = build_version_map(messages)
        effective_messages = [
            message
            for message in messages
            if message.role != Message.ROLE_ASSISTANT or version_map.get(message.id, MessageVersionInfo(True, None)).is_current_version
        ]
        latest_effective = effective_messages[-1] if effective_messages else None
        latest_assistant = next(
            (message for message in reversed(effective_messages) if message.role == Message.ROLE_ASSISTANT),
            None,
        )
        items.append(
            {
                "id": conversation.id,
                "title": conversation.title,
                "title_source": conversation.title_source,
                "model_code": conversation.model_code,
                "last_message_preview": trim_text(latest_effective.content_markdown if latest_effective else "", 80),
                "last_message_at": conversation.last_message_at,
                "message_count": len(messages),
                "latest_assistant_status": latest_assistant.status if latest_assistant else None,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
        )
    return items


def create_conversation(user, title):
    trimmed_title = (title or "").strip()
    conversation = Conversation.objects.create(
        user=user,
        title=trimmed_title,
        title_source=Conversation.TITLE_SOURCE_MANUAL if trimmed_title else Conversation.TITLE_SOURCE_AUTO,
        model_code=settings.CHAT_MODEL_CODE,
    )
    return serialize_conversation(conversation)


def rename_conversation(conversation, title):
    trimmed_title = (title or "").strip()
    if not trimmed_title:
        raise exceptions.ValidationError({"title": "标题不能为空"})
    if len(trimmed_title) > 80:
        raise exceptions.ValidationError({"title": "标题长度不能超过 80 个字符"})

    conversation.title = trimmed_title
    conversation.title_source = Conversation.TITLE_SOURCE_MANUAL
    conversation.save(update_fields=["title", "title_source", "updated_at"])
    return {
        "id": conversation.id,
        "title": conversation.title,
        "title_source": conversation.title_source,
        "updated_at": conversation.updated_at,
    }


def soft_delete_conversation(conversation):
    conversation.deleted_at = timezone.now()
    conversation.save(update_fields=["deleted_at", "updated_at"])


def ensure_no_active_stream(conversation):
    if Message.objects.filter(
        conversation=conversation,
        role=Message.ROLE_ASSISTANT,
        status=Message.STATUS_STREAMING,
    ).exists():
        raise exceptions.ValidationError({"detail": "当前会话仍有消息在生成中"})


def auto_title_for_content(content):
    return trim_text(content, settings.CHAT_AUTO_TITLE_LENGTH)


def _next_sequence_no(conversation):
    max_sequence = (
        Message.objects.filter(conversation=conversation).aggregate(max_sequence=Max("sequence_no")).get("max_sequence")
        or 0
    )
    return max_sequence + 1


def _stop_cache_key(message_id):
    return f"{STOP_KEY_PREFIX}:{message_id}"


def _message_idem_cache_key(user_id, conversation_id, client_message_id):
    return f"{IDEM_MESSAGE_KEY_PREFIX}:{user_id}:{conversation_id}:{client_message_id}"


def _regen_idem_cache_key(user_id, assistant_message_id, client_request_id):
    return f"{IDEM_REGEN_KEY_PREFIX}:{user_id}:{assistant_message_id}:{client_request_id}"


def _set_idempotency_record(cache_key, payload):
    cache.set(cache_key, payload, timeout=settings.CHAT_IDEMPOTENCY_TTL_SECONDS)


def _get_provider():
    provider_class = import_string(settings.CHAT_PROVIDER_CLASS)
    return provider_class()


def _build_context_messages(conversation, upto_sequence_no=None, exclude_message_ids=None):
    exclude_message_ids = set(exclude_message_ids or [])
    messages = list(Message.objects.filter(conversation=conversation).order_by("sequence_no", "id"))
    version_map = build_version_map(messages)
    filtered = []
    for message in messages:
        if message.id in exclude_message_ids:
            continue
        if message.role == Message.ROLE_ASSISTANT and not version_map.get(message.id, MessageVersionInfo(True, None)).is_current_version:
            continue
        if upto_sequence_no is not None and message.sequence_no > upto_sequence_no:
            continue
        filtered.append(message)

    return [
        {"role": message.role, "content": message.content_markdown}
        for message in filtered[-settings.CHAT_CONTEXT_MESSAGE_LIMIT :]
    ]


def _emit_event(event, payload):
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _build_reused_stream_response(assistant_message, *, reused=False):
    final_event = "message.done"
    if assistant_message.status == Message.STATUS_STOPPED:
        final_event = "message.stopped"
    elif assistant_message.status == Message.STATUS_FAILED:
        final_event = "message.error"

    yield _emit_event(
        "message.snapshot",
        {
            "assistant_message_id": assistant_message.id,
            "content": assistant_message.content_markdown,
            "status": assistant_message.status,
            "reused": reused,
        },
    )
    if final_event == "message.error":
        yield _emit_event(
            final_event,
            {
                "assistant_message_id": assistant_message.id,
                "status": assistant_message.status,
                "error_code": assistant_message.error_code or "provider_error",
                "message": assistant_message.error_message or "模型服务暂时不可用",
            },
        )
    else:
        yield _emit_event(
            final_event,
            {
                "assistant_message_id": assistant_message.id,
                "status": assistant_message.status,
            },
        )


def prepare_message_stream(conversation, *, user, content, client_message_id):
    content = (content or "").strip()
    if not content:
        raise exceptions.ValidationError({"content": "消息内容不能为空"})
    if not client_message_id:
        raise exceptions.ValidationError({"client_message_id": "client_message_id 不能为空"})

    cache_key = _message_idem_cache_key(user.id, conversation.id, client_message_id)
    existing = cache.get(cache_key)
    if existing:
        assistant_message = Message.objects.get(pk=existing["assistant_message_id"], user=user)
        if existing.get("status") == Message.STATUS_STREAMING:
            raise ConflictError(
                {
                    "detail": "duplicate client_message_id",
                    "conversation_id": conversation.id,
                    "user_message_id": existing["user_message_id"],
                    "assistant_message_id": existing["assistant_message_id"],
                    "status": existing["status"],
                }
            )
        return _build_reused_stream_response(assistant_message, reused=True)

    ensure_no_active_stream(conversation)

    with transaction.atomic():
        user_message = Message.objects.create(
            conversation=conversation,
            user=user,
            role=Message.ROLE_USER,
            content_markdown=content,
            content_text=content,
            status=Message.STATUS_COMPLETED,
            sequence_no=_next_sequence_no(conversation),
            completed_at=timezone.now(),
        )
        assistant_message = Message.objects.create(
            conversation=conversation,
            user=user,
            role=Message.ROLE_ASSISTANT,
            status=Message.STATUS_STREAMING,
            sequence_no=_next_sequence_no(conversation),
            reply_to_message=user_message,
            started_at=timezone.now(),
        )
        if not conversation.title or conversation.title_source == Conversation.TITLE_SOURCE_AUTO:
            conversation.title = auto_title_for_content(content)
            conversation.title_source = Conversation.TITLE_SOURCE_AUTO
        conversation.last_message_at = assistant_message.created_at
        conversation.model_code = settings.CHAT_MODEL_CODE
        conversation.save(update_fields=["title", "title_source", "last_message_at", "model_code", "updated_at"])

    idem_payload = {
        "conversation_id": conversation.id,
        "user_message_id": user_message.id,
        "assistant_message_id": assistant_message.id,
        "status": Message.STATUS_STREAMING,
    }
    _set_idempotency_record(cache_key, idem_payload)
    context_messages = _build_context_messages(conversation, exclude_message_ids={assistant_message.id})
    return _stream_new_generation(
        assistant_message=assistant_message,
        cache_key=cache_key,
        idempotency_payload=idem_payload,
        context_messages=context_messages,
    )


def prepare_regenerate_stream(message, *, user, client_request_id):
    if not client_request_id:
        raise exceptions.ValidationError({"client_request_id": "client_request_id 不能为空"})
    if message.role != Message.ROLE_ASSISTANT:
        raise exceptions.ValidationError({"detail": "只有 assistant 消息支持重新生成"})

    conversation = message.conversation
    ensure_no_active_stream(conversation)

    messages = list(Message.objects.filter(conversation=conversation).order_by("sequence_no", "id"))
    version_map = build_version_map(messages)
    current_info = version_map.get(message.id)
    if not current_info or not current_info.is_current_version:
        raise exceptions.ValidationError({"detail": "只能重新生成当前有效的最后一条回答"})

    latest_current_assistant = next(
        (
            item
            for item in reversed(messages)
            if item.role == Message.ROLE_ASSISTANT and version_map.get(item.id, MessageVersionInfo(True, None)).is_current_version
        ),
        None,
    )
    if latest_current_assistant is None or latest_current_assistant.id != message.id:
        raise exceptions.ValidationError({"detail": "只能重新生成当前有效的最后一条回答"})
    if message.reply_to_message_id is None:
        raise exceptions.ValidationError({"detail": "当前回答缺少对应的用户消息"})

    cache_key = _regen_idem_cache_key(user.id, message.id, client_request_id)
    existing = cache.get(cache_key)
    if existing:
        assistant_message = Message.objects.get(pk=existing["assistant_message_id"], user=user)
        if existing.get("status") == Message.STATUS_STREAMING:
            raise ConflictError(
                {
                    "detail": "duplicate client_request_id",
                    "conversation_id": conversation.id,
                    "assistant_message_id": existing["assistant_message_id"],
                    "regen_from_message_id": existing["regen_from_message_id"],
                    "status": existing["status"],
                }
            )
        return _build_reused_stream_response(assistant_message, reused=True)

    with transaction.atomic():
        assistant_message = Message.objects.create(
            conversation=conversation,
            user=user,
            role=Message.ROLE_ASSISTANT,
            status=Message.STATUS_STREAMING,
            sequence_no=_next_sequence_no(conversation),
            reply_to_message_id=message.reply_to_message_id,
            regen_from_message=message,
            started_at=timezone.now(),
        )
        conversation.last_message_at = assistant_message.created_at
        conversation.save(update_fields=["last_message_at", "updated_at"])

    idem_payload = {
        "conversation_id": conversation.id,
        "assistant_message_id": assistant_message.id,
        "regen_from_message_id": message.id,
        "status": Message.STATUS_STREAMING,
    }
    _set_idempotency_record(cache_key, idem_payload)
    context_messages = _build_context_messages(
        conversation,
        upto_sequence_no=message.reply_to_message.sequence_no,
        exclude_message_ids={message.id, assistant_message.id},
    )
    return _stream_new_generation(
        assistant_message=assistant_message,
        cache_key=cache_key,
        idempotency_payload=idem_payload,
        context_messages=context_messages,
    )


def _stream_new_generation(*, assistant_message, cache_key, idempotency_payload, context_messages):
    provider = _get_provider()
    accumulated_content = assistant_message.content_markdown
    provider_message_id = ""

    yield _emit_event(
        "conversation.meta",
        {
            "conversation_id": assistant_message.conversation_id,
            "user_message_id": assistant_message.reply_to_message_id,
            "assistant_message_id": assistant_message.id,
        },
    )

    try:
        for chunk in provider.stream_messages(
            context_messages,
            model_code=assistant_message.conversation.model_code,
            system_prompt=assistant_message.conversation.system_prompt,
        ):
            if cache.get(_stop_cache_key(assistant_message.id)):
                raise StopGeneration()

            if chunk.provider_message_id:
                provider_message_id = chunk.provider_message_id
            if chunk.delta_text:
                accumulated_content += chunk.delta_text
                Message.objects.filter(pk=assistant_message.id).update(
                    content_markdown=accumulated_content,
                    content_text=accumulated_content,
                    provider_message_id=provider_message_id,
                    updated_at=timezone.now(),
                )
                yield _emit_event(
                    "message.delta",
                    {
                        "assistant_message_id": assistant_message.id,
                        "delta": chunk.delta_text,
                    },
                )

        final_status = Message.STATUS_COMPLETED
        final_event = "message.done"
        error_code = ""
        error_message = ""
    except StopGeneration:
        final_status = Message.STATUS_STOPPED
        final_event = "message.stopped"
        error_code = ""
        error_message = ""
    except ProviderError as exc:
        final_status = Message.STATUS_FAILED
        final_event = "message.error"
        error_code = exc.error_code
        error_message = str(exc)
    except Exception as exc:
        final_status = Message.STATUS_FAILED
        final_event = "message.error"
        error_code = "provider_error"
        error_message = str(exc)

    now = timezone.now()
    update_kwargs = {
        "status": final_status,
        "content_markdown": accumulated_content,
        "content_text": accumulated_content,
        "provider_message_id": provider_message_id,
        "completed_at": now,
        "updated_at": now,
        "error_code": error_code,
        "error_message": error_message[:255],
    }
    Message.objects.filter(pk=assistant_message.id).update(**update_kwargs)
    Conversation.objects.filter(pk=assistant_message.conversation_id).update(last_message_at=now, updated_at=now)

    idempotency_payload["status"] = final_status
    _set_idempotency_record(cache_key, idempotency_payload)
    cache.delete(_stop_cache_key(assistant_message.id))

    if final_event == "message.error":
        yield _emit_event(
            final_event,
            {
                "assistant_message_id": assistant_message.id,
                "status": final_status,
                "error_code": error_code or "provider_error",
                "message": error_message[:255] or "模型服务暂时不可用",
            },
        )
    else:
        yield _emit_event(
            final_event,
            {
                "assistant_message_id": assistant_message.id,
                "status": final_status,
            },
        )


def mark_stop_requested(message):
    if message.role != Message.ROLE_ASSISTANT:
        raise exceptions.ValidationError({"detail": "只有 assistant 消息支持停止生成"})
    if message.status != Message.STATUS_STREAMING:
        raise exceptions.ValidationError({"detail": "当前消息不在生成中"})

    latest_message = Message.objects.filter(conversation=message.conversation).order_by("-sequence_no", "-id").first()
    if latest_message is None or latest_message.id != message.id:
        raise exceptions.ValidationError({"detail": "只能停止当前会话最后一条生成中的消息"})

    cache.set(_stop_cache_key(message.id), "1", timeout=300)
    return {"assistant_message_id": message.id, "status": "stopping"}
