from django.urls import path

from apps.chat.views import (
    ConversationCollectionView,
    ConversationItemView,
    MessageItemView,
    MessageRegenerateView,
    MessageStopView,
    MessageStreamView,
)


urlpatterns = [
    path("conversations/", ConversationCollectionView.as_view(), name="chat-conversation-collection"),
    path("conversations/<int:conversation_id>/", ConversationItemView.as_view(), name="chat-conversation-item"),
    path(
        "conversations/<int:conversation_id>/messages/stream/",
        MessageStreamView.as_view(),
        name="chat-message-stream",
    ),
    path("messages/<int:message_id>/", MessageItemView.as_view(), name="chat-message-item"),
    path("messages/<int:message_id>/stop/", MessageStopView.as_view(), name="chat-message-stop"),
    path(
        "messages/<int:message_id>/regenerate/",
        MessageRegenerateView.as_view(),
        name="chat-message-regenerate",
    ),
]
