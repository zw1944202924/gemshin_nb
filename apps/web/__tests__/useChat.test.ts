import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, computed } from 'vue'

// Mock Vue auto-imports
vi.stubGlobal('computed', computed)
vi.stubGlobal('ref', ref)

// Mock dependencies
const mockGetMessage = vi.fn()
vi.mock('~/services/chatApi', () => ({
  createChatApi: vi.fn(() => ({
    getMessage: mockGetMessage,
  })),
  ChatApiError: class extends Error {},
}))

const mockStreamingMessageId = ref(null)
const mockStreamError = ref('')
const mockMessages = ref([])
vi.mock('~/composables/chatState', () => ({
  useChatStreamingMessageIdState: vi.fn(() => mockStreamingMessageId),
  useChatStreamErrorState: vi.fn(() => mockStreamError),
  useChatActiveConversationState: vi.fn(() => ref(null)),
  useChatMessagesState: vi.fn(() => mockMessages),
  useChatInitializedState: vi.fn(() => ref(false)),
  useChatSidebarLoadingState: vi.fn(() => ref(false)),
  useChatConversationLoadingState: vi.fn(() => ref(false)),
  useChatPendingSendState: vi.fn(() => ref(false)),
  useChatPendingRenameState: vi.fn(() => ref(false)),
  useChatPendingDeleteState: vi.fn(() => ref(false)),
  useChatStreamStoppingState: vi.fn(() => ref(false)),
  useChatInterfaceErrorState: vi.fn(() => ref('')),
  useChatConversationListState: vi.fn(() => ref([])),
  abortActiveChatStreamController: vi.fn(),
  setActiveChatStreamController: vi.fn(),
}))

// Mock Nuxt composables
vi.stubGlobal('useRuntimeConfig', () => ({
  public: { apiBase: 'http://localhost:3000/api' },
}))
vi.stubGlobal('useRoute', () => ({
  query: {},
  path: '/chat',
}))
vi.stubGlobal('useRouter', () => ({
  replace: vi.fn(),
}))
vi.stubGlobal('useAuth', () => ({
  token: ref('test-token'),
}))
vi.stubGlobal('onUnmounted', vi.fn())

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockStreamingMessageId.value = null
    mockStreamError.value = ''
    mockMessages.value = []
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should start polling when recoverMessageStatus detects streaming status', async () => {
    const { useChat } = await import('~/composables/useChat')
    const chat = useChat()

    const mockMessage = {
      id: 123,
      status: 'streaming',
      content_markdown: 'test content',
      role: 'assistant',
    }

    const completedMessage = {
      id: 123,
      status: 'completed',
      content_markdown: 'final content',
      role: 'assistant',
    }

    // Add message to messages array
    mockMessages.value = [mockMessage]

    // Mock the API to return a streaming message, then completed
    mockGetMessage
      .mockResolvedValueOnce(mockMessage)
      .mockResolvedValueOnce(completedMessage)

    // Call recoverMessageStatus
    await chat.recoverMessageStatus(123)

    // Should have set streaming message ID
    expect(mockStreamingMessageId.value).toBe(123)

    // Fast-forward time to trigger polling (async timer for async setInterval callback)
    await vi.advanceTimersToNextTimerAsync()

    // Should have called getMessage again
    expect(mockGetMessage).toHaveBeenCalledTimes(2)

    // Should have cleared streaming message ID
    expect(mockStreamingMessageId.value).toBeNull()
  })

  it('should stop polling when message status is no longer streaming', async () => {
    const { useChat } = await import('~/composables/useChat')
    const chat = useChat()

    const mockMessage = {
      id: 456,
      status: 'streaming',
      content_markdown: 'test content',
      role: 'assistant',
    }

    const completedMessage = {
      id: 456,
      status: 'completed',
      content_markdown: 'final content',
      role: 'assistant',
    }

    // Add message to messages array
    mockMessages.value = [mockMessage]

    // Mock the API
    mockGetMessage
      .mockResolvedValueOnce(mockMessage)
      .mockResolvedValueOnce(completedMessage)

    // Call recoverMessageStatus
    await chat.recoverMessageStatus(456)

    // Should have set streaming message ID
    expect(mockStreamingMessageId.value).toBe(456)

    // Fast-forward time to trigger polling (async timer for async setInterval callback)
    await vi.advanceTimersToNextTimerAsync()

    // Should have called getMessage again
    expect(mockGetMessage).toHaveBeenCalledTimes(2)

    // Should have cleared streaming message ID
    expect(mockStreamingMessageId.value).toBeNull()
  })

  it('should handle polling errors gracefully', async () => {
    const { useChat } = await import('~/composables/useChat')
    const chat = useChat()

    const mockMessage = {
      id: 789,
      status: 'streaming',
      content_markdown: 'test content',
      role: 'assistant',
    }

    // Add message to messages array
    mockMessages.value = [mockMessage]

    // Mock the API to throw an error
    mockGetMessage
      .mockResolvedValueOnce(mockMessage)
      .mockRejectedValueOnce(new Error('Network error'))

    // Call recoverMessageStatus
    await chat.recoverMessageStatus(789)

    // Should have set streaming message ID
    expect(mockStreamingMessageId.value).toBe(789)

    // Fast-forward time to trigger polling (async timer for async setInterval callback)
    await vi.advanceTimersToNextTimerAsync()

    // Should have called getMessage again
    expect(mockGetMessage).toHaveBeenCalledTimes(2)

    // Should have set error message
    expect(mockStreamError.value).toBe('Network error')
  })
})