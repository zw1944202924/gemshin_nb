<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true,
})

const { modules, loading, error, fetchModules } = useModules()

onMounted(() => {
  fetchModules()
})

const handleModuleClick = (code: string) => {
  navigateTo(`/modules/${code}`)
}
</script>

<template>
  <div class="module-center">
    <section class="page-header">
      <div class="page-header-inner">
        <div class="page-label">模块中心</div>
        <h1 class="page-title">选择你有权限使用的业务模块</h1>
        <p class="page-desc">
          登录后统一先到模块中心，再选择进入某个固定模块。当前页面只展示你已获得授权的业务模块，未授权模块不会显示。
        </p>
      </div>
    </section>

    <section class="module-section">
      <div class="module-section-inner">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button class="retry-btn" @click="fetchModules">重试</button>
        </div>

        <!-- 空状态：无任何授权模块 -->
        <div v-else-if="modules.length === 0" class="empty-state">
          <div class="empty-icon">🔒</div>
          <h2 class="empty-title">暂无可用模块</h2>
          <p class="empty-desc">
            你尚未获得任何业务模块的访问权限。请联系管理员获取授权后，即可在此处看到对应的模块入口。
          </p>
          <NuxtLink to="/" class="back-link">返回首页</NuxtLink>
        </div>

        <!-- 模块卡片网格 -->
        <div v-else class="module-grid">
          <article
            v-for="mod in modules"
            :key="mod.id"
            class="module-card"
            @click="handleModuleClick(mod.code)"
          >
            <div class="module-icon">{{ mod.icon || '📦' }}</div>
            <h3>{{ mod.name }}</h3>
            <p>{{ mod.description }}</p>
            <div class="module-meta">
              <span class="meta-tag status-ready">已就绪</span>
            </div>
            <button class="module-action">进入模块</button>
          </article>
        </div>

        <div class="footer-notes">
          <span>模块中心只负责"选模块"，不提前展开模块内部阶段链路。</span>
          <span>当前页面只展示已获得授权的业务模块，未授权模块不显示。</span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.module-center {
  min-height: 100vh;
}

.page-header {
  padding: 40px 24px 0;
  position: relative;
}

.page-header::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.page-header-inner {
  position: relative;
  z-index: 1;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
}

.page-label {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-muted);
  margin-bottom: 12px;
}

.page-title {
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: var(--ink-primary);
  max-width: 18ch;
}

.page-desc {
  max-width: 64ch;
  margin-top: 16px;
  color: var(--ink-copy);
  line-height: 1.72;
  font-size: 15px;
}

.module-section {
  padding: 24px 24px 60px;
}

.module-section-inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--ink-muted);
  font-size: 15px;
}

/* 错误状态 */
.error-state {
  text-align: center;
  padding: 80px 24px;
  color: #f87171;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 24px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s, transform 0.15s;
}

.retry-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 24px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 24px;
}

.empty-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--ink-primary);
  margin-bottom: 12px;
}

.empty-desc {
  max-width: 48ch;
  margin: 0 auto;
  color: var(--ink-copy);
  line-height: 1.7;
  font-size: 15px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  margin-top: 32px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.15s;
}

.back-link:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

/* 模块网格 */
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.module-card {
  background: var(--surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 28px 24px;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.module-card:hover {
  border-color: var(--ink-accent);
  box-shadow: 0 8px 32px rgba(49, 95, 143, 0.12);
  transform: translateY(-2px);
}

.module-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(49, 95, 143, 0.12), rgba(49, 95, 143, 0.04));
  display: grid;
  place-items: center;
  margin-bottom: 18px;
  font-size: 22px;
}

.module-card h3 {
  font-size: 18px;
  line-height: 1.3;
  color: var(--ink-primary);
  margin-bottom: 10px;
}

.module-card p {
  color: var(--ink-copy);
  line-height: 1.65;
  font-size: 14px;
  flex: 1;
}

.module-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ink-muted);
  padding: 4px 10px;
  background: var(--surface-soft);
  border-radius: 100px;
}

.meta-tag.status-ready {
  color: #0f766e;
  background: rgba(15, 118, 110, 0.08);
}

.module-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  margin-top: 18px;
  padding: 0 20px;
  border-radius: var(--radius-sm);
  background: #17202c;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.15s, transform 0.15s;
  text-decoration: none;
  width: fit-content;
  border: none;
  cursor: pointer;
}

.module-action:hover {
  background: #2a3a4e;
  transform: translateY(-1px);
}

.footer-notes {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-top: 36px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
  color: #435163;
  font-size: 13px;
  line-height: 1.65;
}

@media (max-width: 920px) {
  .module-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: 26px;
  }

  .module-card {
    padding: 22px 18px;
  }
}
</style>
