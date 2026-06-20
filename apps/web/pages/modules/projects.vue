<script setup lang="ts">
definePageMeta({
  layout: "shell"
})
</script>

<template>
  <div class="placeholder-page">
    <section class="placeholder-hero">
      <div class="placeholder-hero-inner">
        <p class="kicker">业务模块</p>
        <h1>项目中心</h1>
        <p class="hero-desc">管理所有小说转漫剧项目，查看阶段进度、待处理项和最近活动。项目管理的真实功能已上线，请通过下方入口进入。</p>
      </div>
    </section>

    <section class="placeholder-content">
      <div class="placeholder-card">
        <div class="placeholder-icon">📁</div>
        <h2>项目中心已上线</h2>
        <p>项目创建、列表管理、状态追踪等核心功能已在 /story 路由下可用。</p>

        <div class="action-area">
          <NuxtLink to="/story" class="primary-action">进入项目中心 →</NuxtLink>
        </div>

        <div class="coming-features">
          <div class="feature-item">
            <strong>项目列表</strong>
            <span>创建和管理你的小说转漫剧项目</span>
          </div>
          <div class="feature-item">
            <strong>分镜管理</strong>
            <span>为项目添加和管理分镜</span>
          </div>
          <div class="feature-item">
            <strong>导出下载</strong>
            <span>校验完整性并导出结构化产物包</span>
          </div>
        </div>

        <NuxtLink to="/modules" class="back-link">← 返回模块中心</NuxtLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.placeholder-page {
  min-height: 100vh;
}

.placeholder-hero {
  padding: 60px 24px 32px;
  position: relative;
}

.placeholder-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.placeholder-hero-inner {
  position: relative;
  z-index: 1;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
}

.kicker {
  margin: 0 0 12px;
  color: var(--ink-accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.placeholder-hero-inner h1 {
  font-size: clamp(32px, 4vw, 48px);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.hero-desc {
  max-width: 56ch;
  margin-top: 12px;
  color: var(--ink-copy);
  font-size: 16px;
  line-height: 1.7;
}

.placeholder-content {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding-bottom: 64px;
}

.placeholder-card {
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  border-radius: 18px;
  padding: 40px;
  box-shadow: var(--shadow-card);
  text-align: center;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.placeholder-card h2 {
  color: var(--surface-ink);
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
}

.placeholder-card p {
  color: var(--surface-copy);
  font-size: 15px;
  line-height: 1.8;
  max-width: 480px;
  margin: 0 auto 8px;
}

.action-area {
  margin: 24px 0;
}

.primary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  border-radius: 12px;
  background: var(--accent-gradient);
  color: #081120;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.15s;
}

.primary-action:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.coming-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 32px auto 28px;
  max-width: 720px;
  text-align: left;
}

.feature-item {
  padding: 16px;
  border-radius: 14px;
  background: rgba(247, 250, 255, 0.04);
  border: 1px solid rgba(194, 214, 255, 0.06);
}

.feature-item strong {
  display: block;
  color: var(--surface-ink);
  font-size: 15px;
  margin-bottom: 4px;
}

.feature-item span {
  color: var(--surface-copy);
  font-size: 13px;
  line-height: 1.6;
}

.back-link {
  display: inline-block;
  color: var(--accent);
  font-size: 15px;
  font-weight: 600;
}

.back-link:hover {
  text-decoration: underline;
}
</style>
