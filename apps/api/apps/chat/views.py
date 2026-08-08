from django.http import StreamingHttpResponse
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.services.chat import (
    build_version_map,
    create_conversation,
    get_conversation_for_user,
    get_message_for_user,
    list_conversation_items,
    mark_stop_requested,
    message_queryset_for_user,
    prepare_message_stream,
    prepare_regenerate_stream,
    rename_conversation,
    serialize_conversation,
    serialize_message,
    serialize_message_detail,
    soft_delete_conversation,
)
from apps.core.permissions import MustChangePasswordGuard


class ChatAPIView(APIView):
    permission_classes = [MustChangePasswordGuard]


class ConversationCollectionView(ChatAPIView):
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", "20"))
        except ValueError as exc:
            raise exceptions.ValidationError({"limit": "limit 必须是整数"}) from exc
        limit = max(1, min(limit, 100))
        return Response({"items": list_conversation_items(request.user, limit), "next_cursor": None})

    def post(self, request):
        payload = create_conversation(request.user, request.data.get("title", ""))
        return Response(payload, status=status.HTTP_201_CREATED)


class ConversationItemView(ChatAPIView):
    def get(self, request, conversation_id):
        conversation = get_conversation_for_user(request.user, conversation_id)
        messages = list(message_queryset_for_user(request.user).filter(conversation=conversation).order_by("sequence_no", "id"))
        version_map = build_version_map(messages)
        return Response(
            {
                "conversation": serialize_conversation(conversation),
                "messages": [serialize_message(message, version_map) for message in messages],
            }
        )

    def patch(self, request, conversation_id):
        conversation = get_conversation_for_user(request.user, conversation_id)
        return Response(rename_conversation(conversation, request.data.get("title", "")))

    def delete(self, request, conversation_id):
        conversation = get_conversation_for_user(request.user, conversation_id)
        soft_delete_conversation(conversation)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageStreamView(ChatAPIView):
    def perform_content_negotiation(self, request, force=False):
        return None, None

    def post(self, request, conversation_id):
        conversation = get_conversation_for_user(request.user, conversation_id)
        stream = prepare_message_stream(
            conversation,
            user=request.user,
            content=request.data.get("content", ""),
            client_message_id=request.data.get("client_message_id", ""),
        )
        return StreamingHttpResponse(stream, content_type="text/event-stream")


class MessageStopView(ChatAPIView):
    def post(self, request, message_id):
        message = get_message_for_user(request.user, message_id)
        return Response(mark_stop_requested(message))


class MessageRegenerateView(ChatAPIView):
    def perform_content_negotiation(self, request, force=False):
        return None, None

    def post(self, request, message_id):
        message = get_message_for_user(request.user, message_id)
        stream = prepare_regenerate_stream(
            message,
            user=request.user,
            client_request_id=request.data.get("client_request_id", ""),
        )
        return StreamingHttpResponse(stream, content_type="text/event-stream")


class MessageItemView(ChatAPIView):
    def get(self, request, message_id):
        message = get_message_for_user(request.user, message_id)
        return Response(serialize_message_detail(message))
