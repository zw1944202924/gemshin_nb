<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const newApiPath = "/assistant/new-api/"
</script>

<template>
  <section class="assistant-page">
    <div class="assistant-toolbar">
      <div>
        <p>AI 助手</p>
        <h1>New API 工作台</h1>
      </div>
      <a class="open-link" :href="newApiPath" target="_blank" rel="noreferrer">新窗口打开</a>
    </div>
    <iframe
      class="assistant-frame"
      :src="newApiPath"
      title="New API 工作台"
      referrerpolicy="same-origin"
    />
  </section>
</template>

<style scoped>
.assistant-page {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 96px);
  gap: 16px;
}

.assistant-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.assistant-toolbar p {
  margin: 0 0 4px;
  color: #64748b;
  font-size: 13px;
}

.assistant-toolbar h1 {
  margin: 0;
  color: #0f172a;
  font-size: 22px;
  font-weight: 700;
}

.open-link {
  flex: 0 0 auto;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 12px;
  text-decoration: none;
}

.assistant-frame {
  width: 100%;
  min-height: 720px;
  flex: 1;
  border: 1px solid #dbe3ef;
  border-radius: 8px;
  background: #fff;
}

@media (max-width: 720px) {
  .assistant-page {
    min-height: calc(100vh - 80px);
    gap: 12px;
  }

  .assistant-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .assistant-frame {
    min-height: 640px;
  }
}
</style>
