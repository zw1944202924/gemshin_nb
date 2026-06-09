<script setup lang="ts">
import type { ChatMessage } from "~/services/chatApi"

const props = defineProps<{
  messages: ChatMessage[]
  loading: boolean
}>()

const scrollContainer = ref<HTMLElement | null>(null)

watch(
  () => props.messages.map((message) => `${message.id}:${message.content_markdown.length}:${message.status}`).join("|"),
  async () => {
    await nextTick()
    scrollContainer.value?.scrollTo({
      top: scrollContainer.value.scrollHeight,
      behavior: "smooth"
    })
  }
)
</script>

<template>
  <section ref="scrollContainer" class="message-list">
    <div v-if="loading" class="panel-state">
      <p>正在加载会话历史...</p>
    </div>

    <div v-else-if="!messages.length" class="panel-state empty">
      <p class="eyebrow">Ready</p>
      <h3>先发一条消息，开始第一轮对话。</h3>
      <p>支持多行输入、流式展示、停止生成和重新生成上一条回答。</p>
    </div>

    <div v-else class="message-stack">
      <ChatMessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message"
      />
    </div>
  </section>
</template>

<style scoped>
.message-list {
  min-height: 24rem;
  max-height: calc(100vh - 20rem);
  overflow: auto;
  padding-right: 0.35rem;
}

.panel-state,
.message-stack {
  display: grid;
  gap: 1rem;
}

.panel-state {
  min-height: 22rem;
  place-items: center;
  align-content: center;
  padding: 2rem;
  border-radius: 1.6rem;
  background:
    radial-gradient(circle at top left, rgba(240, 194, 107, 0.2), transparent 35%),
    rgba(255, 255, 255, 0.6);
  border: 1px dashed rgba(21, 37, 28, 0.12);
  text-align: center;
}

.eyebrow,
h3,
p {
  margin: 0;
}

.eyebrow {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #8c6b2f;
}

.empty {
  gap: 0.75rem;
}

.message-stack {
  gap: 1rem;
}
</style>
