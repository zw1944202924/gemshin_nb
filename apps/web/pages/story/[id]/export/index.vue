<script setup lang="ts">
definePageMeta({ requiresAuth: true })

const route = useRoute()
const projectId = Number(route.params.id)

const {
  activeProject,
  exportSummary,
  exportValidation,
  loading,
  error,
  fetchProject,
  fetchExportSummary,
  fetchExportValidation,
} = useStory()

const tab = ref<"summary" | "validate">("summary")

await fetchProject(projectId)
await fetchExportSummary(projectId).catch(() => {})
await fetchExportValidation(projectId).catch(() => {})

const assetLabelMap: Record<string, string> = {
  image: "图片",
  video: "视频",
  audio: "音频",
  subtitle: "字幕",
}

const statusLabelMap: Record<string, string> = {
  missing: "缺失",
  stale: "待更新",
  complete: "已完成",
  pending: "待生成",
  processing: "生成中",
  failed: "失败",
  outdated: "已过期",
}
</script>

<template>
  <div class="export-page">
    <div class="page-header">
      <div>
        <NuxtLink :to="`/story/${projectId}`" class="back-link">&larr; 返回项目</NuxtLink>
        <h2 v-if="activeProject">{{ activeProject.title }} · 导出管理</h2>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- 汇总概览 -->
    <div v-if="exportSummary" class="summary-bar">
      <div class="summary-stat">
        <span class="stat-value">{{ exportSummary.complete_shots }} / {{ exportSummary.shot_count }}</span>
        <span class="stat-label">镜头就绪</span>
      </div>
      <div class="summary-stat">
        <span
          class="stat-value status-badge"
          :class="exportValidation?.valid ? 'valid' : 'invalid'"
        >
          {{ exportValidation?.valid ? "可导出" : "有缺口" }}
        </span>
        <span class="stat-label">标准校验</span>
      </div>
    </div>

    <!-- 校验错误列表 -->
    <div v-if="exportValidation && !exportValidation.valid" class="validation-errors">
      <h4>校验未通过</h4>
      <ul>
        <li v-for="(err, i) in exportValidation.errors" :key="i">{{ err }}</li>
      </ul>
    </div>

    <!-- Tab 切换 -->
    <div class="tabs">
      <button
        class="tab-btn"
        :class="{ active: tab === 'summary' }"
        @click="tab = 'summary'"
      >
        素材明细
      </button>
      <button
        class="tab-btn"
        :class="{ active: tab === 'validate' }"
        @click="tab = 'validate'"
      >
        导出校验
      </button>
    </div>

    <!-- 素材明细 -->
    <div v-if="tab === 'summary' && exportSummary" class="shot-table-wrap">
      <table class="shot-table">
        <thead>
          <tr>
            <th>镜头</th>
            <th>图片</th>
            <th>视频</th>
            <th>音频</th>
            <th>字幕</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in exportSummary.shots" :key="s.shot_id">
            <td class="col-order">镜头 {{ s.shot_order }}</td>
            <td
              v-for="at in ['image', 'video', 'audio', 'subtitle']"
              :key="at"
              class="col-asset"
              :class="s.assets[at]"
            >
              {{ statusLabelMap[s.assets[at]] || s.assets[at] }}
            </td>
            <td>
              <span v-if="s.is_complete" class="tag-ok">就绪</span>
              <span v-else class="tag-warn">待处理</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 校验详细 -->
    <div v-if="tab === 'validate' && exportValidation" class="validate-section">
      <div class="validate-card" :class="{ valid: exportValidation.valid, invalid: !exportValidation.valid }">
        <h4>{{ exportValidation.valid ? "校验通过" : "校验失败" }}</h4>
        <p v-if="exportValidation.valid">所有镜头必备素材齐全，可以进行标准导出。</p>
        <p v-else>存在 {{ exportValidation.errors.length }} 个问题需要处理。</p>
      </div>

      <div v-if="!exportValidation.valid" class="missing-detail">
        <h4>问题详情</h4>
        <div
          v-for="s in exportSummary?.shots.filter(x => !x.is_complete)"
          :key="s.shot_id"
          class="missing-shot"
        >
          <strong>镜头 {{ s.shot_order }}</strong>
          <span v-if="s.missing.length">
            缺少: {{ s.missing.map(m => assetLabelMap[m]).join("、") }}
          </span>
          <span v-if="s.stale.length">
            待更新: {{ s.stale.map(m => assetLabelMap[m]).join("、") }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<style scoped>
.export-page {
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

.summary-bar {
  display: flex;
  gap: 24px;
  padding: 18px 24px;
  border-radius: 14px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  background: #fff;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
}

.stat-label {
  font-size: 0.78rem;
  color: rgba(21, 37, 28, 0.45);
}

.status-badge {
  padding: 2px 14px;
  border-radius: 999px;
  font-size: 0.85rem;
}

.status-badge.valid { background: #e8f5e9; color: #2e7d32; }
.status-badge.invalid { background: #fce4ec; color: #c62828; }

.validation-errors {
  padding: 14px 18px;
  border-radius: 10px;
  background: #fff3e0;
  border: 1px solid #ffcc80;
}

.validation-errors h4 {
  margin: 0 0 6px;
  font-size: 0.9rem;
  color: #e65100;
}

.validation-errors ul {
  margin: 0;
  padding-left: 20px;
  font-size: 0.85rem;
  color: #bf360c;
}

.tabs {
  display: flex;
  gap: 4px;
}

.tab-btn {
  padding: 8px 20px;
  border: 1px solid rgba(21, 37, 28, 0.12);
  border-radius: 10px 10px 0 0;
  background: #f5f7fb;
  font: inherit;
  cursor: pointer;
}

.tab-btn.active {
  background: #fff;
  border-bottom-color: #fff;
  font-weight: 700;
}

.shot-table-wrap {
  overflow-x: auto;
}

.shot-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.shot-table th,
.shot-table td {
  padding: 10px 14px;
  border: 1px solid rgba(21, 37, 28, 0.06);
  text-align: left;
}

.shot-table th {
  background: #fafbfd;
  font-weight: 700;
}

.col-order {
  font-weight: 700;
}

.col-asset.missing { color: #c62828; }
.col-asset.stale { color: #f57f17; }
.col-asset.complete { color: #2e7d32; }
.col-asset.pending { color: #999; }
.col-asset.processing { color: #ff9800; }
.col-asset.failed { color: #c62828; }
.col-asset.outdated { color: #9e9e9e; }

.tag-ok {
  padding: 2px 8px;
  border-radius: 999px;
  background: #e8f5e9;
  color: #2e7d32;
  font-size: 0.75rem;
  font-weight: 700;
}

.tag-warn {
  padding: 2px 8px;
  border-radius: 999px;
  background: #fff3e0;
  color: #e65100;
  font-size: 0.75rem;
  font-weight: 700;
}

.validate-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.validate-card {
  padding: 20px;
  border-radius: 12px;
  border-width: 2px;
  border-style: solid;
}

.validate-card.valid {
  border-color: #4caf50;
  background: #e8f5e9;
}

.validate-card.invalid {
  border-color: #ef5350;
  background: #fce4ec;
}

.validate-card h4 {
  margin: 0 0 6px;
}

.validate-card p {
  margin: 0;
  font-size: 0.88rem;
}

.missing-detail h4 {
  margin: 0 0 8px;
  font-size: 0.95rem;
}

.missing-shot {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(21, 37, 28, 0.06);
  background: #fff;
  display: flex;
  gap: 12px;
  font-size: 0.85rem;
  margin-bottom: 6px;
}

.loading {
  text-align: center;
  padding: 32px;
  color: rgba(21, 37, 28, 0.4);
}
</style>
