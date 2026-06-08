<script setup lang="ts">
const props = defineProps<{
  pendingSend: boolean
  isStreaming: boolean
  canRegenerate: boolean
  streamStopping: boolean
}>()

const emit = defineEmits<{
  send: [content: string]
  stop: []
  regenerate: []
}>()

const draft = ref("")

const submit = () => {
  const content = draft.value.trim()
  if (!content || props.pendingSend || props.isStreaming) {
    return
  }

  emit("send", content)
  draft.value = ""
}

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault()
    submit()
  }
}
</script>

<template>
  <section class="composer">
    <textarea
      v-model="draft"
      rows="5"
      maxlength="6000"
      placeholder="输入消息。支持 Markdown，按 Ctrl+Enter 发送。"
      :disabled="pendingSend && !isStreaming"
      @keydown="onKeydown"
    />

    <div class="composer-footer">
      <p>Enter 换行，Ctrl+Enter 发送。</p>
      <div class="actions">
        <button
          v-if="canRegenerate"
          type="button"
          class="ghost"
          :disabled="pendingSend || isStreaming"
          @click="emit('regenerate')"
        >
          重新生成上一条回答
        </button>

        <button
          v-if="isStreaming"
          type="button"
          class="danger"
          :disabled="streamStopping"
          @click="emit('stop')"
        >
          {{ streamStopping ? "停止中..." : "停止生成" }}
        </button>

        <button type="button" class="primary" :disabled="pendingSend || isStreaming || !draft.trim()" @click="submit">
          {{ pendingSend && !isStreaming ? "发送中..." : "发送" }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.composer {
  display: grid;
  gap: 0.8rem;
}

textarea {
  width: 100%;
  min-height: 9rem;
  resize: vertical;
  border: 1px solid rgba(21, 37, 28, 0.12);
  border-radius: 1.3rem;
  padding: 1rem 1.1rem;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

textarea:focus {
  outline: 2px solid rgba(240, 194, 107, 0.45);
  outline-offset: 2px;
}

.composer-footer {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.composer-footer p {
  margin: 0;
  color: #5c6c83;
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

button {
  border: 0;
  border-radius: 999px;
  padding: 0.8rem 1rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.primary {
  background: linear-gradient(135deg, #10253a, #264a6b);
  color: #f3f8fc;
}

.ghost {
  background: rgba(15, 23, 39, 0.08);
  color: #152033;
}

.danger {
  background: rgba(176, 41, 51, 0.12);
  color: #8d1022;
}
</style>
