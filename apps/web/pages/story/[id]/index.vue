<script setup lang="ts">
definePageMeta({ requiresAuth: true })

const route = useRoute()
const projectId = Number(route.params.id)

const {
  activeProject,
  shots,
  loading,
  error,
  fetchProject,
  fetchShots,
  createShot,
  createJob,
} = useStory()

const newOrder = ref(1)
const newDescription = ref("")
const showCreateShot = ref(false)

await fetchProject(projectId)
await fetchShots(projectId)

const handleCreateShot = async () => {
  if (newOrder.value < 1) return
  await createShot(projectId, newOrder.value, newDescription.value.trim())
  newOrder.value += 1
  newDescription.value = ""
  showCreateShot.value = false
}

const handleTriggerJob = async (jobType: string) => {
  await createJob(projectId, jobType)
}
</script>

<template>
  <div class="project-page">
    <div class="page-header">
      <div>
        <NuxtLink to="/story" class="back-link">&larr; 返回项目列表</NuxtLink>
        <h2 v-if="activeProject">{{ activeProject.title }}</h2>
      </div>
      <NuxtLink
        v-if="activeProject"
        :to="`/story/${projectId}/export`"
        class="btn-primary"
      >
        导出管理
      </NuxtLink>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- 项目信息 -->
    <div v-if="activeProject" class="info-card">
      <div class="info-row">
        <span class="info-label">状态</span>
        <span class="status-tag" :class="activeProject.status">{{ activeProject.status_display }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">分镜数</span>
        <span>{{ activeProject.shot_count }}</span>
      </div>
      <p class="info-desc">{{ activeProject.description || "暂无描述" }}</p>
    </div>

    <!-- 项目级任务 -->
    <div v-if="activeProject" class="task-bar">
      <h3>项目级任务</h3>
      <div class="task-btns">
        <button class="btn-task" @click="handleTriggerJob('story_outline')">剧情整理</button>
        <button class="btn-task" @click="handleTriggerJob('storyboard')">分镜脚本</button>
      </div>
    </div>

    <!-- 分镜列表 -->
    <div class="shot-section">
      <div class="section-header">
        <h3>分镜列表</h3>
        <button class="btn-outline" @click="showCreateShot = !showCreateShot">
          {{ showCreateShot ? "取消" : "+ 添加分镜" }}
        </button>
      </div>

      <div v-if="showCreateShot" class="create-panel">
        <label>
          序号
          <input v-model.number="newOrder" type="number" min="1" class="input-sm" />
        </label>
        <input
          v-model="newDescription"
          type="text"
          placeholder="分镜描述（可选）"
          class="input"
        />
        <button class="btn-primary" :disabled="newOrder < 1" @click="handleCreateShot">添加</button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="shots.length === 0" class="empty">
        <p>暂无分镜，请先添加</p>
      </div>

      <div v-else class="shot-grid">
        <NuxtLink
          v-for="shot in shots"
          :key="shot.id"
          :to="`/story/${projectId}/shots/${shot.id}`"
          class="shot-card"
        >
          <div class="shot-header">
            <span class="shot-order">镜头 {{ shot.order }}</span>
            <span class="status-tag" :class="shot.status">{{ shot.status_display }}</span>
          </div>
          <p class="shot-desc">{{ shot.description || "暂无描述" }}</p>
          <div class="shot-assets">
            <span
              v-for="asset in shot.assets"
              :key="asset.id"
              class="asset-dot"
              :class="asset.status"
              :title="`${asset.asset_type_display}: ${asset.status_display}`"
            />
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.page-header h2 {
  margin: 4px 0 0;
  font-size: 1.4rem;
}

.back-link {
  font-size: 0.85rem;
  color: rgba(21, 37, 28, 0.5);
}

.back-link:hover {
  color: #162033;
}

.btn-primary {
  padding: 8px 20px;
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

.btn-outline {
  padding: 6px 16px;
  border: 1px solid rgba(21, 37, 28, 0.2);
  border-radius: 999px;
  background: #fff;
  font: inherit;
  cursor: pointer;
}

.btn-task {
  padding: 6px 16px;
  border: 1px solid rgba(21, 37, 28, 0.15);
  border-radius: 999px;
  background: #f5f7fb;
  font: inherit;
  cursor: pointer;
}

.btn-task:hover {
  background: #e8ecf4;
}

.error {
  color: #c22;
  font-size: 0.9rem;
}

.info-card {
  padding: 16px 20px;
  border-radius: 12px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-label {
  width: 64px;
  font-size: 0.85rem;
  color: rgba(21, 37, 28, 0.5);
}

.info-desc {
  margin: 4px 0 0;
  font-size: 0.9rem;
  color: rgba(21, 37, 28, 0.6);
}

.status-tag {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-tag.draft, .status-tag.pending { background: #eef2ff; color: #4b5e8a; }
.status-tag.processing { background: #fff3e0; color: #b8741e; }
.status-tag.completed { background: #e8f5e9; color: #2e7d32; }
.status-tag.failed { background: #fce4ec; color: #c62828; }

.task-bar {
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fafbfd;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.task-bar h3 {
  margin: 0;
  font-size: 1rem;
}

.task-btns {
  display: flex;
  gap: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 1rem;
}

.create-panel {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 14px;
  margin-bottom: 12px;
  border-radius: 12px;
  background: rgba(155, 240, 165, 0.08);
  border: 1px solid rgba(155, 240, 165, 0.25);
}

.create-panel label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
}

.input,
.input-sm {
  padding: 8px 12px;
  border: 1px solid rgba(21, 37, 28, 0.15);
  border-radius: 8px;
  font: inherit;
}

.input {
  flex: 1;
}

.input-sm {
  width: 72px;
}

.loading,
.empty {
  text-align: center;
  padding: 32px;
  color: rgba(21, 37, 28, 0.4);
}

.shot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.shot-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fff;
  transition: box-shadow 180ms ease;
}

.shot-card:hover {
  box-shadow: 0 4px 16px rgba(22, 32, 51, 0.06);
}

.shot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.shot-order {
  font-weight: 700;
  font-size: 0.95rem;
}

.shot-desc {
  margin: 0;
  font-size: 0.82rem;
  color: rgba(21, 37, 28, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shot-assets {
  display: flex;
  gap: 4px;
  margin-top: auto;
}

.asset-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.asset-dot.completed { background: #4caf50; }
.asset-dot.processing { background: #ff9800; }
.asset-dot.pending { background: #bbb; }
.asset-dot.failed { background: #e53935; }
.asset-dot.stale { background: #ffc107; }
.asset-dot.outdated { background: #9e9e9e; }
</style>
