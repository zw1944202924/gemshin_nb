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
        <h1>结果校验与导出</h1>
        <p class="hero-desc">在正式导出前校验完整性，识别缺口、失败任务和依赖失效，确保交付质量。</p>
      </div>
    </section>

    <section class="placeholder-content">
      <div class="placeholder-card">
        <div class="placeholder-icon">✅</div>
        <h2>结果校验与导出正在建设中</h2>
        <p>这里将提供项目结果的完整性校验面板，先判断是否可导出，再决定补缺口还是直接输出。</p>
        <p>预计支持：完整性扫描、缺口定位、一键导出产物包、导出历史记录。</p>

        <div class="coming-features">
          <div class="feature-item">
            <strong>完整性扫描</strong>
            <span>自动检测分镜、素材、配音等各环节的完整性</span>
          </div>
          <div class="feature-item">
            <strong>缺口定位</strong>
            <span>精确定位缺失项和失败的生成任务</span>
          </div>
          <div class="feature-item">
            <strong>产物导出</strong>
            <span>将完整项目打包导出为结构化产物</span>
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
