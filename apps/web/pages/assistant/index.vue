<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const {
  activeConversation,
  activeConversationId,
  conversationList,
  conversationLoading,
  sidebarLoading,
  pendingSend,
  pendingRename,
  pendingDelete,
  streamStopping,
  interfaceError,
  streamError,
  isStreaming,
  canRegenerate,
  lastCurrentAssistant,
  visibleMessages,
  normalizeConversationTitle,
  initialize,
  handleRouteConversationChange,
  createConversation,
  selectConversation,
  renameConversation,
  deleteConversation,
  sendMessage,
  stopStreaming,
  regenerateLastAnswer
} = useChat()

const { user } = useAuth()
const router = useRouter()

const pageReady = ref(false)

const loadPage = async () => {
  try {
    await initialize()
  } finally {
    pageReady.value = true
  }
}

const createAndOpenConversation = async () => {
  await createConversation()
}

const renameConversationFromSidebar = async (payload: { conversationId: number; title: string }) => {
  await renameConversation(payload.conversationId, payload.title)
}

const renameCurrentConversation = async (title: string) => {
  if (!activeConversationId.value) return
  await renameConversation(activeConversationId.value, title)
}

const deleteCurrentConversation = async () => {
  if (!activeConversationId.value) return
  await deleteConversation(activeConversationId.value)
}

watch(
  () => useRoute().query.conversation,
  async () => {
    if (pageReady.value) {
      await handleRouteConversationChange()
    }
  }
)

onMounted(async () => {
  await loadPage()
})
</script>

<template>
  <div class="assistant-page">
    <section class="assistant-hero">
      <div class="assistant-hero-inner">
        <p class="kicker">AI 助手</p>
        <h1>你的项目智能助手</h1>
        <p class="hero-desc">
          当前登录：<strong>{{ user?.display_name || user?.username }}</strong>。
          你可以向 AI 助手询问项目进度、业务方向建议或任何创作相关问题。
          AI 助手了解你的用户信息、项目上下文以及三个业务方向（项目中心、漫剧工作台、结果校验与导出）。
        </p>
      </div>
    </section>

    <section class="assistant-shell">
      <!-- 侧边栏 -->
      <aside class="sidebar-panel">
        <div class="sidebar-header">
          <p class="sidebar-title">会话历史</p>
        </div>

        <ChatConversationSidebar
          :conversations="conversationList"
          :active-conversation-id="activeConversationId"
          :loading="sidebarLoading"
          :pending-rename="pendingRename"
          :pending-delete="pendingDelete"
          @create="createAndOpenConversation"
          @select="selectConversation"
          @rename="renameConversationFromSidebar"
          @delete="deleteConversation"
        />
      </aside>

      <!-- 主内容区 -->
      <section class="content-panel">
        <p v-if="interfaceError" class="error-banner">{{ interfaceError }}</p>

        <template v-if="activeConversation">
          <ChatConversationHeader
            :title="normalizeConversationTitle(activeConversation)"
            :model-code="activeConversation.model_code"
            :pending-rename="pendingRename"
            :pending-delete="pendingDelete"
            @rename="renameCurrentConversation"
            @delete="deleteCurrentConversation"
          />

          <ChatStreamingStatusBar
            :is-streaming="isStreaming"
            :stream-error="streamError"
            :latest-status="lastCurrentAssistant?.status || ''"
          />

          <ChatMessageList
            :messages="visibleMessages"
            :loading="conversationLoading || !pageReady"
          />

          <ChatComposerBox
            :pending-send="pendingSend"
            :is-streaming="isStreaming"
            :can-regenerate="canRegenerate"
            :stream-stopping="streamStopping"
            @send="sendMessage"
            @stop="stopStreaming"
            @regenerate="regenerateLastAnswer"
          />
        </template>

        <section v-else class="empty-panel">
          <p class="eyebrow">AI 助手就绪</p>
          <h3>新建一个会话，开始与 AI 助手对话。</h3>
          <p>
            AI 助手可以回答项目相关问题、提供创作建议，
            并了解你当前的项目状态和三个业务方向的工作流程。
          </p>
          <button class="btn-primary" type="button" @click="createAndOpenConversation">
            立即新建会话
          </button>
        </section>
      </section>
    </section>
  </div>
</template>

<style scoped>
.assistant-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.assistant-hero {
  padding: 40px 24px 20px;
  position: relative;
}

.assistant-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.assistant-hero-inner {
  position: relative;
  z-index: 1;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
}

.kicker {
  margin: 0 0 8px;
  color: var(--ink-accent);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.assistant-hero-inner h1 {
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.hero-desc {
  max-width: 64ch;
  margin-top: 10px;
  color: var(--ink-copy);
  font-size: 14px;
  line-height: 1.7;
}

.hero-desc strong {
  color: var(--ink-primary);
}

/* Shell */
.assistant-shell {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(240px, 280px) minmax(0, 1fr);
  gap: 0;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto 0;
  border-top: 1px solid var(--border-light);
}

.sidebar-panel {
  padding: 16px;
  border-right: 1px solid var(--border-light);
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding-bottom: 12px;
}

.sidebar-title {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(205, 220, 247, 0.66);
}

.content-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.error-banner {
  margin: 0;
  padding: 10px 16px;
  background: rgba(248, 113, 113, 0.12);
  color: #f87171;
  font-size: 13px;
}

/* Empty */
.empty-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-panel .eyebrow {
  color: var(--ink-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.empty-panel h3 {
  color: var(--ink-primary);
  font-size: 22px;
  margin-bottom: 10px;
}

.empty-panel p {
  color: var(--ink-copy);
  font-size: 14px;
  line-height: 1.7;
  max-width: 480px;
  margin-bottom: 24px;
}

.empty-panel .btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  border: none;
  border-radius: 12px;
  background: var(--accent-gradient);
  color: #081120;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 920px) {
  .assistant-shell {
    grid-template-columns: 1fr;
  }

  .sidebar-panel {
    border-right: 0;
    border-bottom: 1px solid var(--border-light);
    max-height: 300px;
  }
}
</style>
