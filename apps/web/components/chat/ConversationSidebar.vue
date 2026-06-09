<script setup lang="ts">
import type { ChatConversationSummary } from "~/services/chatApi"

const props = defineProps<{
  conversations: ChatConversationSummary[]
  activeConversationId: number | null
  loading: boolean
  pendingRename: boolean
  pendingDelete: boolean
}>()

const emit = defineEmits<{
  create: []
  select: [conversationId: number]
  rename: [payload: { conversationId: number; title: string }]
  delete: [conversationId: number]
}>()

const renamingConversationId = ref<number | null>(null)
const renameDraft = ref("")

const startRename = (conversation: ChatConversationSummary) => {
  renamingConversationId.value = conversation.id
  renameDraft.value = conversation.title
}

const cancelRename = () => {
  renamingConversationId.value = null
  renameDraft.value = ""
}

const submitRename = () => {
  if (!renamingConversationId.value) {
    return
  }

  emit("rename", {
    conversationId: renamingConversationId.value,
    title: renameDraft.value
  })
  cancelRename()
}

const formatTitle = (conversation: ChatConversationSummary) => conversation.title.trim() || "新对话"
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div>
        <p class="eyebrow">AI Chat</p>
        <h2>会话列表</h2>
      </div>

      <button class="create-button" type="button" :disabled="loading" @click="emit('create')">
        新建
      </button>
    </div>

    <p v-if="!conversations.length && !loading" class="placeholder">
      还没有会话，先新建一个对话开始联调。
    </p>

    <div v-else class="conversation-list">
      <article
        v-for="conversation in props.conversations"
        :key="conversation.id"
        class="conversation-card"
        :class="{ active: conversation.id === props.activeConversationId }"
        @click="emit('select', conversation.id)"
      >
        <template v-if="renamingConversationId === conversation.id">
          <form class="rename-form" @submit.prevent.stop="submitRename">
            <input
              v-model="renameDraft"
              type="text"
              maxlength="80"
              placeholder="输入新标题"
              @click.stop
            />
            <div class="rename-actions">
              <button type="submit" :disabled="pendingRename">保存</button>
              <button type="button" class="ghost" @click.stop="cancelRename">取消</button>
            </div>
          </form>
        </template>

        <template v-else>
          <div class="conversation-main">
            <h3>{{ formatTitle(conversation) }}</h3>
            <p>{{ conversation.last_message_preview || "等待第一条消息" }}</p>
          </div>

          <footer class="conversation-footer">
            <small>{{ conversation.latest_assistant_status || "idle" }}</small>
            <div class="row-actions">
              <button type="button" class="ghost" @click.stop="startRename(conversation)">改名</button>
              <button
                type="button"
                class="danger"
                :disabled="pendingDelete"
                @click.stop="emit('delete', conversation.id)"
              >
                删除
              </button>
            </div>
          </footer>
        </template>
      </article>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  display: grid;
  gap: 18px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.eyebrow,
h2,
h3,
p {
  margin: 0;
}

.eyebrow {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255, 245, 225, 0.68);
}

h2 {
  margin-top: 0.45rem;
  font-size: 1.3rem;
}

.create-button,
.rename-actions button,
.row-actions button {
  border: 0;
  border-radius: 999px;
  padding: 0.6rem 0.9rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.create-button {
  background: linear-gradient(135deg, #f0c26b, #ffd78a);
  color: #3d2811;
}

.placeholder {
  padding: 1rem;
  border: 1px dashed rgba(255, 255, 255, 0.16);
  border-radius: 1rem;
  color: rgba(237, 244, 238, 0.72);
  line-height: 1.6;
}

.conversation-list {
  display: grid;
  gap: 0.85rem;
}

.conversation-card {
  display: grid;
  gap: 0.9rem;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.15rem;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    background 180ms ease;
}

.conversation-card:hover,
.conversation-card.active {
  transform: translateY(-1px);
  border-color: rgba(240, 194, 107, 0.34);
  background: rgba(240, 194, 107, 0.12);
}

.conversation-main {
  display: grid;
  gap: 0.45rem;
}

.conversation-main h3 {
  font-size: 0.98rem;
  color: #fff8ec;
}

.conversation-main p {
  color: rgba(237, 244, 238, 0.68);
  font-size: 0.88rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.conversation-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.conversation-footer small {
  color: rgba(237, 244, 238, 0.68);
  text-transform: capitalize;
}

.row-actions,
.rename-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ghost {
  background: rgba(255, 255, 255, 0.08);
  color: #eff6f0;
}

.danger {
  background: rgba(195, 62, 62, 0.18);
  color: #ffd7d4;
}

.rename-form {
  display: grid;
  gap: 0.75rem;
}

.rename-form input {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 0.9rem;
  padding: 0.8rem 0.9rem;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
</style>
