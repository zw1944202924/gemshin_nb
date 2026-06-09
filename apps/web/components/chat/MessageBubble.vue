<script setup lang="ts">
import MarkdownIt from "markdown-it"
import type { ChatMessage } from "~/services/chatApi"

const props = defineProps<{
  message: ChatMessage
}>()

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

const renderedHtml = computed(() =>
  props.message.role === "assistant"
    ? markdown.render(props.message.content_markdown || "")
    : ""
)

const statusLabel = computed(() => {
  switch (props.message.status) {
    case "streaming":
      return "生成中"
    case "stopped":
      return "已停止"
    case "failed":
      return props.message.error_message || "生成失败"
    default:
      return ""
  }
})
</script>

<template>
  <article class="bubble-row" :class="message.role">
    <div class="avatar">{{ message.role === "assistant" ? "AI" : "我" }}</div>
    <div class="bubble">
      <div class="bubble-head">
        <strong>{{ message.role === "assistant" ? "Gemshin AI" : "你" }}</strong>
        <small v-if="statusLabel">{{ statusLabel }}</small>
      </div>

      <div
        v-if="message.role === 'assistant'"
        class="markdown-body"
        v-html="renderedHtml"
      />
      <p v-else class="plain-text">{{ message.content_markdown }}</p>
    </div>
  </article>
</template>

<style scoped>
.bubble-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.9rem;
  align-items: start;
}

.bubble-row.user {
  grid-template-columns: minmax(0, 1fr) auto;
}

.bubble-row.user .avatar {
  order: 2;
  background: linear-gradient(135deg, #11253c, #24496c);
  color: #f4f8fc;
}

.bubble-row.user .bubble {
  order: 1;
  margin-left: auto;
  background: linear-gradient(135deg, #f6f7fa, #e7edf6);
}

.avatar {
  width: 2.5rem;
  height: 2.5rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
  background: linear-gradient(135deg, #ffebb7, #f0bf6c);
  color: #5d3a10;
  font-weight: 800;
}

.bubble {
  width: min(100%, 50rem);
  padding: 1rem 1.1rem;
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(21, 37, 28, 0.08);
  box-shadow: 0 14px 32px rgba(22, 32, 51, 0.08);
}

.bubble-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 0.75rem;
}

.bubble-head small {
  color: #8c5b15;
}

.plain-text {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.7;
}

.markdown-body :deep(*) {
  max-width: 100%;
}

.markdown-body :deep(p),
.markdown-body :deep(ul),
.markdown-body :deep(ol),
.markdown-body :deep(pre),
.markdown-body :deep(blockquote) {
  margin: 0 0 0.85rem;
  line-height: 1.75;
}

.markdown-body :deep(p:last-child),
.markdown-body :deep(ul:last-child),
.markdown-body :deep(ol:last-child),
.markdown-body :deep(pre:last-child),
.markdown-body :deep(blockquote:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(code) {
  border-radius: 0.45rem;
  padding: 0.12rem 0.35rem;
  background: rgba(15, 23, 39, 0.08);
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 0.92em;
}

.markdown-body :deep(pre) {
  overflow: auto;
  border-radius: 1rem;
  padding: 0.9rem 1rem;
  background: #152033;
  color: #f2f7fb;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
}

.markdown-body :deep(blockquote) {
  padding-left: 0.9rem;
  border-left: 3px solid rgba(121, 96, 48, 0.3);
  color: #55657d;
}

@media (max-width: 640px) {
  .bubble-row,
  .bubble-row.user {
    grid-template-columns: 1fr;
  }

  .bubble-row.user .avatar {
    order: 1;
  }

  .bubble-row.user .bubble {
    order: 2;
  }

  .avatar {
    width: 2.2rem;
    height: 2.2rem;
  }
}
</style>
