<script setup lang="ts">
definePageMeta({ requiresAuth: true })

const route = useRoute()
const projectId = Number(route.params.id)
const shotId = Number(route.params.shotId)

const {
  activeShot,
  jobs,
  loading,
  error,
  fetchShot,
  fetchJobs,
  createJob,
  retryJob,
} = useStory()

await fetchShot(shotId)
await fetchJobs(projectId, shotId)

const handleTriggerTask = async (jobType: string) => {
  await createJob(projectId, jobType, shotId)
  await fetchJobs(projectId, shotId)
}

const handleRetry = async (jobId: number) => {
  await retryJob(jobId)
  await fetchJobs(projectId, shotId)
}

const shotJobTypes = [
  { type: "image_generation", label: "图片生成" },
  { type: "video_generation", label: "视频生成" },
  { type: "voice_generation", label: "配音生成" },
]

const jobTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    story_outline: "剧情整理",
    storyboard: "分镜脚本",
    image_generation: "图片生成",
    video_generation: "视频生成",
    voice_generation: "配音生成",
  }
  return map[type] || type
}
</script>

<template>
  <div class="shot-page">
    <div class="page-header">
      <div>
        <NuxtLink :to="`/story/${projectId}`" class="back-link">
          &larr; 返回项目
        </NuxtLink>
        <h2 v-if="activeShot">镜头 {{ activeShot.order }}</h2>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- 镜头信息 -->
    <div v-if="activeShot" class="info-card">
      <div class="info-row">
        <span class="info-label">状态</span>
        <span class="status-tag" :class="activeShot.status">{{ activeShot.status_display }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">序号</span>
        <span>{{ activeShot.order }}</span>
      </div>
      <p class="info-desc">{{ activeShot.description || "暂无描述" }}</p>
    </div>

    <!-- 素材状态 -->
    <div v-if="activeShot && activeShot.assets.length" class="asset-section">
      <h3>素材</h3>
      <div class="asset-grid">
        <div
          v-for="asset in activeShot.assets"
          :key="asset.id"
          class="asset-card"
          :class="{ stale: asset.is_stale || asset.status === 'stale' }"
        >
          <div class="asset-type">{{ asset.asset_type_display }}</div>
          <span class="status-tag" :class="asset.status">{{ asset.status_display }}</span>
          <span v-if="asset.is_stale" class="stale-badge">待更新</span>
        </div>
      </div>
    </div>

    <!-- 任务触发 -->
    <div class="task-section">
      <h3>触发任务</h3>
      <div class="task-trigger-grid">
        <button
          v-for="jt in shotJobTypes"
          :key="jt.type"
          class="btn-task"
          @click="handleTriggerTask(jt.type)"
        >
          {{ jt.label }}
        </button>
      </div>
    </div>

    <!-- 任务历史 -->
    <div class="job-section">
      <h3>任务记录</h3>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="jobs.length === 0" class="empty">
        <p>暂无任务记录</p>
      </div>

      <div v-else class="job-list">
        <div
          v-for="job in jobs"
          :key="job.id"
          class="job-card"
        >
          <div class="job-header">
            <span class="job-type">{{ jobTypeLabel(job.job_type) }}</span>
            <span class="status-tag" :class="job.status">{{ job.status_display }}</span>
          </div>
          <div class="job-meta">
            <span>尝试 #{{ job.attempt }}</span>
            <span>{{ new Date(job.created_at).toLocaleString("zh-CN") }}</span>
          </div>
          <button
            v-if="job.status === 'failed'"
            class="btn-retry"
            @click="handleRetry(job.id)"
          >
            重试
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shot-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
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

.status-tag.pending { background: #eef2ff; color: #4b5e8a; }
.status-tag.processing { background: #fff3e0; color: #b8741e; }
.status-tag.completed { background: #e8f5e9; color: #2e7d32; }
.status-tag.failed { background: #fce4ec; color: #c62828; }
.status-tag.stale { background: #fff8e1; color: #f57f17; }
.status-tag.outdated { background: #f3e5f5; color: #7b1fa2; }

.asset-section h3,
.task-section h3,
.job-section h3 {
  margin: 0 0 10px;
  font-size: 1rem;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.asset-card {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.asset-card.stale {
  border-color: #ffc107;
  background: #fffde7;
}

.asset-type {
  font-weight: 700;
  font-size: 0.9rem;
}

.stale-badge {
  padding: 1px 8px;
  border-radius: 999px;
  background: #ffc107;
  color: #5d4037;
  font-size: 0.7rem;
  font-weight: 700;
  align-self: flex-start;
}

.task-trigger-grid {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-task {
  padding: 8px 18px;
  border: 1px solid rgba(21, 37, 28, 0.2);
  border-radius: 999px;
  background: #162033;
  color: #f5f7fb;
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-task:hover {
  background: #2a3d56;
}

.loading,
.empty {
  text-align: center;
  padding: 24px;
  color: rgba(21, 37, 28, 0.4);
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.job-card {
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.job-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.job-type {
  font-weight: 700;
  font-size: 0.9rem;
}

.job-meta {
  display: flex;
  gap: 16px;
  font-size: 0.78rem;
  color: rgba(21, 37, 28, 0.45);
}

.btn-retry {
  padding: 4px 14px;
  border: 1px solid #e53935;
  border-radius: 999px;
  background: #fff;
  color: #c62828;
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-retry:hover {
  background: #fce4ec;
}
</style>
