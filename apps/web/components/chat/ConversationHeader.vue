<script setup lang="ts">
const props = defineProps<{
  title: string
  modelCode: string
  pendingRename: boolean
  pendingDelete: boolean
}>()

const emit = defineEmits<{
  rename: [title: string]
  delete: []
}>()

const editing = ref(false)
const draftTitle = ref(props.title)

watch(
  () => props.title,
  (value) => {
    draftTitle.value = value
  }
)

const submitRename = () => {
  emit("rename", draftTitle.value)
  editing.value = false
}
</script>

<template>
  <header class="header">
    <div class="header-main">
      <p class="eyebrow">Conversation</p>
      <template v-if="editing">
        <form class="rename-form" @submit.prevent="submitRename">
          <input v-model="draftTitle" maxlength="80" type="text" />
          <button type="submit" :disabled="pendingRename">保存</button>
          <button type="button" class="ghost" @click="editing = false">取消</button>
        </form>
      </template>
      <template v-else>
        <h2>{{ title }}</h2>
        <p class="model">模型：{{ modelCode }}</p>
      </template>
    </div>

    <div class="header-actions">
      <button class="ghost" type="button" @click="editing = true">改名</button>
      <button class="danger" type="button" :disabled="pendingDelete" @click="emit('delete')">
        删除会话
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.eyebrow,
h2,
.model {
  margin: 0;
}

.eyebrow {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #796030;
}

h2 {
  margin-top: 0.35rem;
  font-size: clamp(1.5rem, 3vw, 2rem);
}

.model {
  margin-top: 0.5rem;
  color: #55657d;
}

.header-actions,
.rename-form {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.rename-form input {
  min-width: min(100%, 18rem);
  border: 1px solid #cfdae7;
  border-radius: 999px;
  padding: 0.8rem 1rem;
  background: #fff;
}

button {
  border: 0;
  border-radius: 999px;
  padding: 0.75rem 1rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.ghost {
  background: rgba(15, 23, 39, 0.08);
  color: #152033;
}

.danger {
  background: rgba(176, 41, 51, 0.12);
  color: #8d1022;
}

@media (max-width: 720px) {
  .header {
    flex-direction: column;
  }
}
</style>
