import {
  ChatApiError,
  type ChatConversation,
  type ChatConversationSummary,
  type ChatMessage,
  type ChatMessageStatus,
  createChatApi
} from "~/services/chatApi"

let activeStreamController: AbortController | null = null

const createClientRequestId = () => {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID()
  }

  return `client-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const buildNowIso = () => new Date().toISOString()

const createTempMessage = (
  role: ChatMessage["role"],
  content: string,
  status: ChatMessageStatus,
  overrides: Partial<ChatMessage> = {}
): ChatMessage => ({
  id: -Date.now() - Math.floor(Math.random() * 1000),
  role,
  content_markdown: content,
  status,
  created_at: buildNowIso(),
  completed_at: status === "streaming" ? null : buildNowIso(),
  is_current_version: role === "assistant" ? true : undefined,
  ...overrides
})

const normalizeConversationTitle = (conversation?: Pick<ChatConversationSummary, "title"> | null) =>
  conversation?.title?.trim() || "新对话"

const sortConversationList = (list: ChatConversationSummary[]) =>
  [...list].sort((left, right) => {
    const leftTime = left.last_message_at || left.updated_at
    const rightTime = right.last_message_at || right.updated_at
    return new Date(rightTime).getTime() - new Date(leftTime).getTime()
  })

const findLastCurrentAssistant = (items: ChatMessage[]) =>
  [...items]
    .reverse()
    .find((message) => message.role === "assistant" && message.is_current_version !== false)

const buildVisibleMessages = (items: ChatMessage[]) =>
  items.filter((message) => message.role !== "assistant" || message.is_current_version !== false)

const isRouteConversationId = (value: unknown): value is string =>
  typeof value === "string" && /^\d+$/.test(value)

export const useChat = () => {
  const config = useRuntimeConfig()
  const route = useRoute()
  const router = useRouter()
  const { token } = useAuth()

  const conversationList = useState<ChatConversationSummary[]>("chat-conversation-list", () => [])
  const activeConversation = useState<ChatConversation | null>("chat-active-conversation", () => null)
  const messages = useState<ChatMessage[]>("chat-messages", () => [])
  const initialized = useState<boolean>("chat-initialized", () => false)
  const sidebarLoading = useState<boolean>("chat-sidebar-loading", () => false)
  const conversationLoading = useState<boolean>("chat-conversation-loading", () => false)
  const pendingSend = useState<boolean>("chat-pending-send", () => false)
  const pendingRename = useState<boolean>("chat-pending-rename", () => false)
  const pendingDelete = useState<boolean>("chat-pending-delete", () => false)
  const streamStopping = useState<boolean>("chat-stream-stopping", () => false)
  const streamError = useState<string>("chat-stream-error", () => "")
  const interfaceError = useState<string>("chat-interface-error", () => "")
  const streamingMessageId = useState<number | null>("chat-streaming-message-id", () => null)

  const ensureToken = () => {
    if (!token.value) {
      throw new Error("当前未登录，无法访问聊天接口")
    }

    return token.value
  }

  const api = () =>
    createChatApi({
      apiBase: config.public.apiBase,
      token: ensureToken()
    })

  const activeConversationId = computed(() => activeConversation.value?.id ?? null)
  const visibleMessages = computed(() => buildVisibleMessages(messages.value))
  const lastCurrentAssistant = computed(() => findLastCurrentAssistant(messages.value) ?? null)
  const isStreaming = computed(() => streamingMessageId.value !== null)
  const canRegenerate = computed(() => Boolean(lastCurrentAssistant.value && !isStreaming.value))

  const updateConversationListItem = (conversation: ChatConversationSummary) => {
    const next = [...conversationList.value]
    const index = next.findIndex((item) => item.id === conversation.id)

    if (index >= 0) {
      next[index] = {
        ...next[index],
        ...conversation
      }
    } else {
      next.unshift(conversation)
    }

    conversationList.value = sortConversationList(next)
  }

  const removeConversationListItem = (conversationId: number) => {
    conversationList.value = conversationList.value.filter((item) => item.id !== conversationId)
  }

  const syncActiveConversationSummary = () => {
    if (!activeConversation.value) {
      return
    }

    const lastVisible = [...visibleMessages.value].reverse()[0]
    updateConversationListItem({
      id: activeConversation.value.id,
      title: activeConversation.value.title,
      title_source: activeConversation.value.title_source,
      model_code: activeConversation.value.model_code,
      created_at: activeConversation.value.created_at,
      updated_at: activeConversation.value.updated_at,
      last_message_preview: lastVisible?.content_markdown.slice(0, 120) || "",
      last_message_at: lastVisible?.completed_at || lastVisible?.created_at || activeConversation.value.updated_at,
      latest_assistant_status: lastCurrentAssistant.value?.status ?? null,
      message_count: visibleMessages.value.length
    })
  }

  const setActiveConversationByDetail = (detail: { conversation: ChatConversation; messages: ChatMessage[] }) => {
    activeConversation.value = detail.conversation
    messages.value = detail.messages
    syncActiveConversationSummary()
  }

  const pushConversationRoute = async (conversationId: number | null) => {
    const nextQuery = { ...route.query }

    if (conversationId === null) {
      delete nextQuery.conversation
    } else {
      nextQuery.conversation = String(conversationId)
    }

    await router.replace({ path: "/chat", query: nextQuery })
  }

  const refreshConversationList = async () => {
    sidebarLoading.value = true
    interfaceError.value = ""

    try {
      const response = await api().listConversations()
      conversationList.value = sortConversationList(response.items)
    } catch (error) {
      interfaceError.value = error instanceof Error ? error.message : "会话列表加载失败"
      throw error
    } finally {
      sidebarLoading.value = false
    }
  }

  const selectConversation = async (conversationId: number, options: { syncRoute?: boolean } = {}) => {
    if (conversationLoading.value && activeConversationId.value === conversationId) {
      return
    }

    conversationLoading.value = true
    interfaceError.value = ""

    try {
      const detail = await api().getConversation(conversationId)
      setActiveConversationByDetail(detail)

      if (options.syncRoute !== false) {
        await pushConversationRoute(conversationId)
      }

      const currentStreaming = findLastCurrentAssistant(detail.messages)
      if (currentStreaming?.status === "streaming") {
        streamingMessageId.value = currentStreaming.id
        await recoverMessageStatus(currentStreaming.id)
      } else {
        streamingMessageId.value = null
      }
    } catch (error) {
      interfaceError.value = error instanceof Error ? error.message : "会话详情加载失败"
      throw error
    } finally {
      conversationLoading.value = false
    }
  }

  const createConversation = async (options: { title?: string; select?: boolean } = {}) => {
    sidebarLoading.value = true
    interfaceError.value = ""

    try {
      const created = await api().createConversation(options.title ?? "")
      updateConversationListItem(created)

      if (options.select !== false) {
        activeConversation.value = {
          id: created.id,
          title: created.title,
          title_source: created.title_source,
          model_code: created.model_code,
          created_at: created.created_at,
          updated_at: created.updated_at
        }
        messages.value = []
        await pushConversationRoute(created.id)
      }

      return created
    } catch (error) {
      interfaceError.value = error instanceof Error ? error.message : "创建会话失败"
      throw error
    } finally {
      sidebarLoading.value = false
    }
  }

  const renameConversation = async (conversationId: number, title: string) => {
    pendingRename.value = true
    interfaceError.value = ""

    try {
      const updated = await api().renameConversation(conversationId, title.trim())
      updateConversationListItem(updated)

      if (activeConversation.value?.id === updated.id) {
        activeConversation.value = {
          ...activeConversation.value,
          title: updated.title,
          title_source: updated.title_source,
          updated_at: updated.updated_at
        }
      }
    } catch (error) {
      interfaceError.value = error instanceof Error ? error.message : "重命名失败"
      throw error
    } finally {
      pendingRename.value = false
    }
  }

  const deleteConversation = async (conversationId: number) => {
    pendingDelete.value = true
    interfaceError.value = ""

    try {
      await api().deleteConversation(conversationId)
      removeConversationListItem(conversationId)

      if (activeConversation.value?.id === conversationId) {
        const fallback = conversationList.value[0] ?? null
        activeConversation.value = null
        messages.value = []
        streamingMessageId.value = null

        if (fallback) {
          await selectConversation(fallback.id)
        } else {
          await pushConversationRoute(null)
        }
      }
    } catch (error) {
      interfaceError.value = error instanceof Error ? error.message : "删除会话失败"
      throw error
    } finally {
      pendingDelete.value = false
    }
  }

  const ensureConversationForSend = async () => {
    if (activeConversationId.value) {
      return activeConversationId.value
    }

    const created = await createConversation()
    return created.id
  }

  const replaceMessage = (messageId: number, updater: (message: ChatMessage) => ChatMessage) => {
    messages.value = messages.value.map((message) =>
      message.id === messageId ? updater(message) : message
    )
  }

  const finalizeAssistantStatus = (assistantMessageId: number, status: ChatMessageStatus, error?: string) => {
    replaceMessage(assistantMessageId, (message) => ({
      ...message,
      status,
      completed_at: buildNowIso(),
      error_message: error || message.error_message || null
    }))
    streamingMessageId.value = null
    streamStopping.value = false
    syncActiveConversationSummary()
  }

  const handleStreamFailure = (assistantMessageId: number | null, error: unknown) => {
    const message =
      error instanceof ChatApiError
        ? error.message
        : error instanceof Error
          ? error.message
          : "消息发送失败"

    streamError.value = message

    if (assistantMessageId !== null) {
      finalizeAssistantStatus(assistantMessageId, "failed", message)
    }
  }

  const runStream = async (
    request: (handlers: Parameters<ReturnType<typeof createChatApi>["sendMessageStream"]>[2], signal: AbortSignal) => Promise<void>,
    options: {
      onMeta: (payload: { user_message_id: number; assistant_message_id: number; conversation_id: number }) => void
      optimisticAssistantId: number
    }
  ) => {
    activeStreamController?.abort()
    activeStreamController = new AbortController()
    streamingMessageId.value = options.optimisticAssistantId
    streamError.value = ""

    try {
      await request(
        {
          onMeta: (payload) => {
            options.onMeta(payload)
          },
          onDelta: ({ assistant_message_id, delta }) => {
            replaceMessage(assistant_message_id, (message) => ({
              ...message,
              content_markdown: `${message.content_markdown}${delta}`,
              status: "streaming"
            }))
          },
          onSnapshot: ({ assistant_message_id, content, status }) => {
            replaceMessage(assistant_message_id, (message) => ({
              ...message,
              content_markdown: content,
              status
            }))
          },
          onDone: ({ assistant_message_id, status }) => {
            finalizeAssistantStatus(assistant_message_id, status)
          },
          onStopped: ({ assistant_message_id, status }) => {
            finalizeAssistantStatus(assistant_message_id, status)
          },
          onErrorEvent: ({ assistant_message_id, message }) => {
            finalizeAssistantStatus(assistant_message_id, "failed", message)
          }
        },
        activeStreamController.signal
      )
    } finally {
      activeStreamController = null
    }
  }

  const sendMessage = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed || pendingSend.value || isStreaming.value) {
      return
    }

    const conversationId = await ensureConversationForSend()
    pendingSend.value = true
    interfaceError.value = ""
    streamError.value = ""

    const optimisticUser = createTempMessage("user", trimmed, "completed")
    const optimisticAssistant = createTempMessage("assistant", "", "streaming", {
      is_current_version: true,
      reply_to_message_id: optimisticUser.id
    })

    messages.value = [...messages.value, optimisticUser, optimisticAssistant]
    syncActiveConversationSummary()

    try {
      await runStream(
        (handlers, signal) =>
          api().sendMessageStream(
            conversationId,
            { content: trimmed, client_message_id: createClientRequestId() },
            handlers,
            signal
          ),
        {
          optimisticAssistantId: optimisticAssistant.id,
          onMeta: ({ user_message_id, assistant_message_id, conversation_id }) => {
            replaceMessage(optimisticUser.id, (message) => ({
              ...message,
              id: user_message_id,
              conversation_id: conversation_id
            }))
            replaceMessage(optimisticAssistant.id, (message) => ({
              ...message,
              id: assistant_message_id,
              conversation_id: conversation_id,
              reply_to_message_id: user_message_id
            }))
            streamingMessageId.value = assistant_message_id
          }
        }
      )

      await refreshConversationList()

      if (activeConversationId.value === conversationId) {
        const summary = conversationList.value.find((item) => item.id === conversationId)
        if (summary && activeConversation.value) {
          activeConversation.value = {
            ...activeConversation.value,
            title: summary.title,
            title_source: summary.title_source,
            updated_at: summary.updated_at
          }
        }
      }
    } catch (error) {
      handleStreamFailure(streamingMessageId.value ?? optimisticAssistant.id, error)
    } finally {
      pendingSend.value = false
    }
  }

  const stopStreaming = async () => {
    if (!streamingMessageId.value || streamStopping.value) {
      return
    }

    streamStopping.value = true
    streamError.value = ""

    try {
      await api().stopMessage(streamingMessageId.value)
    } catch (error) {
      streamStopping.value = false
      streamError.value = error instanceof Error ? error.message : "停止生成失败"
      throw error
    }
  }

  const regenerateLastAnswer = async () => {
    const target = lastCurrentAssistant.value
    if (!target || isStreaming.value) {
      return
    }

    pendingSend.value = true
    interfaceError.value = ""
    streamError.value = ""

    const optimisticAssistant = createTempMessage("assistant", "", "streaming", {
      is_current_version: true,
      reply_to_message_id: target.reply_to_message_id ?? null,
      regen_from_message_id: target.id
    })

    messages.value = messages.value.map((message) =>
      message.id === target.id ? { ...message, is_current_version: false } : message
    )
    messages.value = [...messages.value, optimisticAssistant]
    syncActiveConversationSummary()

    try {
      await runStream(
        (handlers, signal) =>
          api().regenerateMessage(
            target.id,
            { client_request_id: createClientRequestId() },
            handlers,
            signal
          ),
        {
          optimisticAssistantId: optimisticAssistant.id,
          onMeta: ({ assistant_message_id, conversation_id }) => {
            replaceMessage(optimisticAssistant.id, (message) => ({
              ...message,
              id: assistant_message_id,
              conversation_id
            }))
            streamingMessageId.value = assistant_message_id
          }
        }
      )

      await refreshConversationList()
    } catch (error) {
      messages.value = messages.value.map((message) =>
        message.id === target.id ? { ...message, is_current_version: true } : message
      )
      handleStreamFailure(streamingMessageId.value ?? optimisticAssistant.id, error)
    } finally {
      pendingSend.value = false
    }
  }

  const recoverMessageStatus = async (messageId: number) => {
    try {
      const latest = await api().getMessage(messageId)
      replaceMessage(messageId, () => latest)
      if (latest.status !== "streaming") {
        streamingMessageId.value = null
      }
      syncActiveConversationSummary()
      return latest
    } catch (error) {
      streamError.value = error instanceof Error ? error.message : "消息状态恢复失败"
      throw error
    }
  }

  const initialize = async () => {
    if (initialized.value) {
      return
    }

    await refreshConversationList()

    if (isRouteConversationId(route.query.conversation)) {
      await selectConversation(Number(route.query.conversation), { syncRoute: false })
    } else if (conversationList.value[0]) {
      await selectConversation(conversationList.value[0].id)
    } else {
      activeConversation.value = null
      messages.value = []
    }

    initialized.value = true
  }

  const handleRouteConversationChange = async () => {
    const routeConversation = isRouteConversationId(route.query.conversation)
      ? Number(route.query.conversation)
      : null

    if (routeConversation === null) {
      if (activeConversation.value && route.path === "/chat") {
        activeConversation.value = null
        messages.value = []
      }
      return
    }

    if (routeConversation !== activeConversationId.value) {
      await selectConversation(routeConversation, { syncRoute: false })
    }
  }

  return {
    conversationList,
    activeConversation,
    activeConversationId,
    messages,
    visibleMessages,
    initialized,
    sidebarLoading,
    conversationLoading,
    pendingSend,
    pendingRename,
    pendingDelete,
    streamStopping,
    streamError,
    interfaceError,
    streamingMessageId,
    isStreaming,
    canRegenerate,
    lastCurrentAssistant,
    normalizeConversationTitle,
    initialize,
    handleRouteConversationChange,
    refreshConversationList,
    createConversation,
    selectConversation,
    renameConversation,
    deleteConversation,
    sendMessage,
    stopStreaming,
    regenerateLastAnswer,
    recoverMessageStatus
  }
}
