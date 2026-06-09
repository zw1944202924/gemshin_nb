import type { ChatConversation, ChatConversationSummary, ChatMessage } from "~/services/chatApi"

let activeStreamController: AbortController | null = null

export const useChatConversationListState = () =>
  useState<ChatConversationSummary[]>("chat-conversation-list", () => [])

export const useChatActiveConversationState = () =>
  useState<ChatConversation | null>("chat-active-conversation", () => null)

export const useChatMessagesState = () =>
  useState<ChatMessage[]>("chat-messages", () => [])

export const useChatInitializedState = () =>
  useState<boolean>("chat-initialized", () => false)

export const useChatSidebarLoadingState = () =>
  useState<boolean>("chat-sidebar-loading", () => false)

export const useChatConversationLoadingState = () =>
  useState<boolean>("chat-conversation-loading", () => false)

export const useChatPendingSendState = () =>
  useState<boolean>("chat-pending-send", () => false)

export const useChatPendingRenameState = () =>
  useState<boolean>("chat-pending-rename", () => false)

export const useChatPendingDeleteState = () =>
  useState<boolean>("chat-pending-delete", () => false)

export const useChatStreamStoppingState = () =>
  useState<boolean>("chat-stream-stopping", () => false)

export const useChatStreamErrorState = () =>
  useState<string>("chat-stream-error", () => "")

export const useChatInterfaceErrorState = () =>
  useState<string>("chat-interface-error", () => "")

export const useChatStreamingMessageIdState = () =>
  useState<number | null>("chat-streaming-message-id", () => null)

export const abortActiveChatStreamController = () => {
  activeStreamController?.abort()
  activeStreamController = null
}

export const setActiveChatStreamController = (controller: AbortController | null) => {
  activeStreamController = controller
}

export const resetChatState = () => {
  abortActiveChatStreamController()

  useChatConversationListState().value = []
  useChatActiveConversationState().value = null
  useChatMessagesState().value = []
  useChatInitializedState().value = false
  useChatSidebarLoadingState().value = false
  useChatConversationLoadingState().value = false
  useChatPendingSendState().value = false
  useChatPendingRenameState().value = false
  useChatPendingDeleteState().value = false
  useChatStreamStoppingState().value = false
  useChatStreamErrorState().value = ""
  useChatInterfaceErrorState().value = ""
  useChatStreamingMessageIdState().value = null
}
