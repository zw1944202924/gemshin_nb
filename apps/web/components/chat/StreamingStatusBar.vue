<script setup lang="ts">
const props = defineProps<{
  isStreaming: boolean
  streamError: string
  latestStatus: string
}>()

const statusCopy = computed(() => {
  if (props.streamError) {
    return props.streamError
  }

  if (props.isStreaming) {
    return "AI 正在流式生成回复，支持随时停止。"
  }

  if (props.latestStatus === "stopped") {
    return "本轮生成已停止，已保留当前内容。"
  }

  if (props.latestStatus === "failed") {
    return "本轮生成失败，可重新生成上一条回答。"
  }

  return "当前会话空闲，可以继续追问。"
})
</script>

<template>
  <div class="status-bar" :class="{ error: streamError, streaming: isStreaming }">
    <span class="indicator" />
    <p>{{ statusCopy }}</p>
  </div>
</template>

<style scoped>
.status-bar {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  padding: 0.9rem 1rem;
  border-radius: 999px;
  background: rgba(15, 23, 39, 0.06);
  color: #324153;
}

.status-bar.streaming {
  background: rgba(240, 194, 107, 0.16);
}

.status-bar.error {
  background: rgba(176, 41, 51, 0.12);
  color: #8d1022;
}

.indicator {
  width: 0.7rem;
  height: 0.7rem;
  flex: 0 0 auto;
  border-radius: 999px;
  background: currentColor;
}

p {
  margin: 0;
}
</style>
