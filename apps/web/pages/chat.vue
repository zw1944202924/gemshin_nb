<script setup lang="ts">
definePageMeta({
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

const { user, logout } = useAuth()
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
  if (!activeConversationId.value) {
    return
  }

  await renameConversation(activeConversationId.value, title)
}

const deleteCurrentConversation = async () => {
  if (!activeConversationId.value) {
    return
  }

  await deleteConversation(activeConversationId.value)
}

const signOut = async () => {
  await logout()
  await router.push("/login")
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
  <main class="chat-page">
    <section class="chat-shell">
      <div class="sidebar-panel">
        <div class="sidebar-top">
          <div>
            <p class="workspace-label">Gemshin AI Workspace</p>
            <h1>对话模块 V1</h1>
            <p class="workspace-user">
              当前用户：<strong>{{ user?.display_name || user?.username }}</strong>
            </p>
          </div>

          <button class="logout-button" type="button" @click="signOut">退出登录</button>
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
      </div>

      <section class="content-panel">
        <div class="content-top">
          <div>
            <p class="eyebrow">Streaming Chat</p>
            <h2>左侧管理会话，右侧完成真实对话链路</h2>
          </div>
          <div class="quick-links">
            <NuxtLink to="/">返回概览</NuxtLink>
            <NuxtLink to="/dashboard">鉴权页</NuxtLink>
          </div>
        </div>

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
          <p class="eyebrow">No Conversation</p>
          <h3>先创建一个会话，再开始联调聊天页。</h3>
          <p>
            页面已经接好会话 CRUD、流式展示、停止生成和重生成入口；
            选中或新建会话后即可进入完整链路。
          </p>
          <button class="primary" type="button" @click="createAndOpenConversation">立即新建会话</button>
        </section>
      </section>
    </section>
  </main>
</template>

<style scoped>
.chat-page {
  min-height: 100vh;
}

.chat-shell {
  min-height: calc(100vh - 3rem);
  display: grid;
  grid-template-columns: minmax(18rem, 24rem) minmax(0, 1fr);
  gap: 1.25rem;
}

.sidebar-panel {
  display: grid;
  gap: 1.25rem;
  padding: 1.25rem;
  border-radius: 2rem;
  background:
    radial-gradient(circle at top, rgba(255, 226, 168, 0.16), transparent 36%),
    linear-gradient(180deg, #172113, #101814);
  color: #edf4ee;
}

.sidebar-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.workspace-label,
.workspace-user,
.eyebrow,
h1,
h2,
h3,
p {
  margin: 0;
}

.workspace-label,
.eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.workspace-label {
  color: rgba(255, 248, 236, 0.72);
}

h1 {
  margin-top: 0.45rem;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.workspace-user {
  margin-top: 0.7rem;
  color: rgba(237, 244, 238, 0.76);
}

.logout-button,
.primary,
.quick-links a {
  border: 0;
  border-radius: 999px;
  font: inherit;
  font-weight: 700;
}

.logout-button {
  padding: 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.08);
  color: #edf4ee;
  cursor: pointer;
}

.content-panel {
  display: grid;
  gap: 1.2rem;
  padding: 1.6rem;
  border-radius: 2rem;
  background:
    radial-gradient(circle at top right, rgba(240, 194, 107, 0.16), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(245, 247, 251, 0.92));
}

.content-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.eyebrow {
  color: #8c6b2f;
}

h2 {
  margin-top: 0.35rem;
  font-size: clamp(1.6rem, 3vw, 2.4rem);
}

.quick-links {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.quick-links a {
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 39, 0.06);
  color: #152033;
}

.error-banner {
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  background: rgba(176, 41, 51, 0.12);
  color: #8d1022;
}

.empty-panel {
  min-height: 28rem;
  display: grid;
  place-content: center;
  gap: 0.8rem;
  text-align: center;
  padding: 2rem;
  border: 1px dashed rgba(21, 37, 28, 0.12);
  border-radius: 1.8rem;
  background: rgba(255, 255, 255, 0.52);
}

.primary {
  justify-self: center;
  padding: 0.9rem 1.2rem;
  background: linear-gradient(135deg, #10253a, #264a6b);
  color: #f3f8fc;
  cursor: pointer;
}

@media (max-width: 1100px) {
  .chat-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .sidebar-top,
  .content-top {
    flex-direction: column;
  }

  .content-panel,
  .sidebar-panel {
    padding: 1.1rem;
  }
}
</style>
