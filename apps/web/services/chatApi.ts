export type ChatMessageStatus = "completed" | "streaming" | "stopped" | "failed"

export type ChatConversationSummary = {
  id: number
  title: string
  title_source: "auto" | "manual"
  model_code: string
  last_message_preview?: string | null
  last_message_at?: string | null
  message_count?: number
  latest_assistant_status?: ChatMessageStatus | null
  created_at: string
  updated_at: string
}

export type ChatConversation = {
  id: number
  title: string
  title_source: "auto" | "manual"
  model_code: string
  created_at: string
  updated_at: string
}

export type ChatMessage = {
  id: number
  conversation_id?: number
  role: "user" | "assistant" | "system"
  content_markdown: string
  status: ChatMessageStatus
  sequence_no?: number | null
  reply_to_message_id?: number | null
  regen_from_message_id?: number | null
  is_current_version?: boolean
  superseded_by_message_id?: number | null
  error_code?: string | null
  error_message?: string | null
  created_at: string
  completed_at?: string | null
}

export type ChatConversationDetail = {
  conversation: ChatConversation
  messages: ChatMessage[]
}

export type ChatConversationsResponse = {
  items: ChatConversationSummary[]
  next_cursor: string | null
}

export type ChatMessageStatusResponse = ChatMessage

export type ChatStreamMetaEvent = {
  conversation_id: number
  user_message_id: number
  assistant_message_id: number
}

export type ChatStreamDeltaEvent = {
  assistant_message_id: number
  delta: string
}

export type ChatStreamTerminalEvent = {
  assistant_message_id: number
  status: ChatMessageStatus
  message?: string
  error_code?: string
}

export type ChatSnapshotEvent = {
  assistant_message_id: number
  content: string
  status: ChatMessageStatus
  reused: boolean
}

type StreamEventHandlers = {
  onMeta?: (payload: ChatStreamMetaEvent) => void
  onDelta?: (payload: ChatStreamDeltaEvent) => void
  onDone?: (payload: ChatStreamTerminalEvent) => void
  onStopped?: (payload: ChatStreamTerminalEvent) => void
  onErrorEvent?: (payload: ChatStreamTerminalEvent) => void
  onSnapshot?: (payload: ChatSnapshotEvent) => void
}

type JsonFetchOptions = {
  method?: string
  body?: unknown
}

type ApiContext = {
  apiBase: string
  token: string
}

export class ChatApiError extends Error {
  statusCode: number
  data: unknown

  constructor(message: string, statusCode: number, data: unknown) {
    super(message)
    this.name = "ChatApiError"
    this.statusCode = statusCode
    this.data = data
  }
}

const createJsonHeaders = (token: string) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
})

const parseResponseError = async (response: Response) => {
  const rawText = await response.text()
  const data = rawText ? tryParseJson(rawText) : null
  const detail =
    data &&
    typeof data === "object" &&
    "detail" in data &&
    typeof data.detail === "string"
      ? data.detail
      : `请求失败（${response.status}）`

  throw new ChatApiError(detail, response.status, data)
}

const tryParseJson = (payload: string) => {
  try {
    return JSON.parse(payload) as unknown
  } catch {
    return payload
  }
}

const requestJson = async <T>(context: ApiContext, path: string, options: JsonFetchOptions = {}) => {
  const response = await fetch(`${context.apiBase}${path}`, {
    method: options.method ?? "GET",
    headers: createJsonHeaders(context.token),
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  })

  if (!response.ok) {
    await parseResponseError(response)
  }

  if (response.status === 204) {
    return null as T
  }

  return (await response.json()) as T
}

const dispatchStreamEvent = (eventName: string, dataPayload: string, handlers: StreamEventHandlers) => {
  const payload = tryParseJson(dataPayload)

  switch (eventName) {
    case "conversation.meta":
      handlers.onMeta?.(payload as ChatStreamMetaEvent)
      return
    case "message.delta":
      handlers.onDelta?.(payload as ChatStreamDeltaEvent)
      return
    case "message.done":
      handlers.onDone?.(payload as ChatStreamTerminalEvent)
      return
    case "message.stopped":
      handlers.onStopped?.(payload as ChatStreamTerminalEvent)
      return
    case "message.error":
      handlers.onErrorEvent?.(payload as ChatStreamTerminalEvent)
      return
    case "message.snapshot":
      handlers.onSnapshot?.(payload as ChatSnapshotEvent)
      return
    default:
  }
}

const consumeSseStream = async (
  response: Response,
  handlers: StreamEventHandlers,
  signal?: AbortSignal
) => {
  if (!response.body) {
    throw new Error("流式响应体为空")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  const flush = () => {
    const normalized = buffer.replace(/\r\n/g, "\n")
    const chunks = normalized.split("\n\n")
    buffer = chunks.pop() ?? ""

    for (const chunk of chunks) {
      const trimmed = chunk.trim()
      if (!trimmed) {
        continue
      }

      let eventName = "message"
      const dataLines: string[] = []

      for (const line of trimmed.split("\n")) {
        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim()
          continue
        }

        if (line.startsWith("data:")) {
          dataLines.push(line.slice(5).trim())
        }
      }

      dispatchStreamEvent(eventName, dataLines.join("\n"), handlers)
    }
  }

  while (true) {
    if (signal?.aborted) {
      break
    }

    const { done, value } = await reader.read()
    if (done) {
      buffer += decoder.decode()
      flush()
      break
    }

    buffer += decoder.decode(value, { stream: true })
    flush()
  }
}

const requestStream = async (
  context: ApiContext,
  path: string,
  body: unknown,
  handlers: StreamEventHandlers,
  signal?: AbortSignal
) => {
  const response = await fetch(`${context.apiBase}${path}`, {
    method: "POST",
    headers: {
      Accept: "text/event-stream",
      ...createJsonHeaders(context.token)
    },
    body: JSON.stringify(body),
    signal
  })

  if (!response.ok) {
    await parseResponseError(response)
  }

  await consumeSseStream(response, handlers, signal)
}

export const createChatApi = (context: ApiContext) => ({
  listConversations(limit = 20) {
    return requestJson<ChatConversationsResponse>(
      context,
      `/chat/conversations/?limit=${limit}`
    )
  },

  createConversation(title = "") {
    return requestJson<ChatConversationSummary>(context, "/chat/conversations/", {
      method: "POST",
      body: { title }
    })
  },

  getConversation(conversationId: number) {
    return requestJson<ChatConversationDetail>(context, `/chat/conversations/${conversationId}/`)
  },

  renameConversation(conversationId: number, title: string) {
    return requestJson<ChatConversationSummary>(context, `/chat/conversations/${conversationId}/`, {
      method: "PATCH",
      body: { title }
    })
  },

  deleteConversation(conversationId: number) {
    return requestJson<null>(context, `/chat/conversations/${conversationId}/`, {
      method: "DELETE"
    })
  },

  sendMessageStream(
    conversationId: number,
    body: { content: string; client_message_id: string },
    handlers: StreamEventHandlers,
    signal?: AbortSignal
  ) {
    return requestStream(
      context,
      `/chat/conversations/${conversationId}/messages/stream/`,
      body,
      handlers,
      signal
    )
  },

  stopMessage(assistantMessageId: number) {
    return requestJson<{ assistant_message_id: number; status: string }>(
      context,
      `/chat/messages/${assistantMessageId}/stop/`,
      {
        method: "POST",
        body: {}
      }
    )
  },

  regenerateMessage(
    assistantMessageId: number,
    body: { client_request_id: string },
    handlers: StreamEventHandlers,
    signal?: AbortSignal
  ) {
    return requestStream(
      context,
      `/chat/messages/${assistantMessageId}/regenerate/`,
      body,
      handlers,
      signal
    )
  },

  getMessage(messageId: number) {
    return requestJson<ChatMessageStatusResponse>(context, `/chat/messages/${messageId}/`)
  }
})
