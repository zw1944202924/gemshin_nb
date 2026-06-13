<script setup lang="ts">
definePageMeta({ requiresAuth: true })

const { projects, loading, error, fetchProjects, createProject } = useStory()
const newTitle = ref("")
const showCreate = ref(false)

await fetchProjects()

const handleCreate = async () => {
  if (!newTitle.value.trim()) return
  await createProject(newTitle.value.trim())
  newTitle.value = ""
  showCreate.value = false
}
</script>

<template>
  <div class="story-page">
    <div class="page-header">
      <h2>漫剧项目</h2>
      <button class="btn-primary" @click="showCreate = !showCreate">
        {{ showCreate ? "取消" : "+ 新建项目" }}
      </button>
    </div>

    <div v-if="showCreate" class="create-panel">
      <input
        v-model="newTitle"
        type="text"
        placeholder="输入项目标题"
        class="input"
        @keyup.enter="handleCreate"
      />
      <button class="btn-primary" :disabled="!newTitle.trim()" @click="handleCreate">创建</button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="projects.length === 0" class="empty">
      <p>暂无项目，点击上方按钮创建第一个漫剧项目</p>
    </div>

    <div v-else class="project-grid">
      <NuxtLink
        v-for="project in projects"
        :key="project.id"
        :to="`/story/${project.id}`"
        class="project-card"
      >
        <div class="card-header">
          <h3>{{ project.title }}</h3>
          <span class="status-tag" :class="project.status">{{ project.status_display }}</span>
        </div>
        <p class="card-desc">{{ project.description || "暂无描述" }}</p>
        <div class="card-meta">
          <span>{{ project.shot_count }} 个分镜</span>
          <span>{{ new Date(project.updated_at).toLocaleDateString("zh-CN") }}</span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.story-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-header h2 {
  margin: 0;
  font-size: 1.4rem;
}

.create-panel {
  display: flex;
  gap: 10px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(155, 240, 165, 0.08);
  border: 1px solid rgba(155, 240, 165, 0.25);
}

.input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid rgba(21, 37, 28, 0.15);
  border-radius: 8px;
  font: inherit;
}

.btn-primary {
  padding: 8px 18px;
  border: none;
  border-radius: 999px;
  background: #162033;
  color: #f5f7fb;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #c22;
  font-size: 0.9rem;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: rgba(21, 37, 28, 0.5);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.project-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fff;
  transition: box-shadow 180ms ease, transform 180ms ease;
}

.project-card:hover {
  box-shadow: 0 8px 24px rgba(22, 32, 51, 0.08);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-tag {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-tag.draft { background: #eef2ff; color: #4b5e8a; }
.status-tag.processing { background: #fff3e0; color: #b8741e; }
.status-tag.completed { background: #e8f5e9; color: #2e7d32; }
.status-tag.failed { background: #fce4ec; color: #c62828; }

.card-desc {
  margin: 0;
  font-size: 0.88rem;
  color: rgba(21, 37, 28, 0.6);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: rgba(21, 37, 28, 0.4);
}
</style>
