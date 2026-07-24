<script setup lang="ts">
definePageMeta({
  layout: "shell"
})

const { isAuthenticated, user } = useAuth()

// 三个固定模块方向
const moduleDirections = [
  {
    name: "AI 漫剧制作一站式系统",
    description: "从内容导入、结构化整理到分镜生成与结果导出，提供完整的漫剧制作工作流。",
    icon: "🎬"
  },
  {
    name: "AI 股票分析系统",
    description: "基于数据驱动的智能分析工具，辅助投资决策与市场趋势洞察。",
    icon: "📈"
  },
  {
    name: "个人博客或个人内容库",
    description: "轻量级内容管理与发布平台，支持个人知识沉淀与对外分享。",
    icon: "📝"
  }
]
</script>

<template>
  <main class="homepage">
    <!-- Hero 区域 -->
    <section class="hero">
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="kicker">多模块集成平台</p>
          <h1>一个入口，三个方向，按需进入。</h1>
          <p class="hero-intro">
            gemshin_nb 将 AI 漫剧制作、股票分析与个人内容管理整合为统一平台。
            登录后先进入模块中心，再选择进入任一业务模块。
          </p>

          <!-- 已登录状态 -->
          <template v-if="isAuthenticated">
            <div class="welcome-banner">
              <span class="welcome-text">欢迎回来，{{ user?.display_name || user?.username }}</span>
            </div>

            <div class="hero-actions">
              <NuxtLink to="/modules" class="btn-primary btn-large">进入模块中心</NuxtLink>
              <NuxtLink to="/assistant" class="btn-secondary btn-large">AI 助手</NuxtLink>
            </div>
          </template>

          <!-- 未登录状态 -->
          <template v-else>
            <p class="hero-note">
              登录后可访问模块中心，选择进入任一业务方向。
            </p>
          </template>
        </div>

        <!-- 产品预览区域 -->
        <section class="product-preview" aria-label="平台概览">
          <div class="preview-card">
            <div class="preview-header">
              <div class="preview-dots" aria-hidden="true">
                <span /><span /><span />
              </div>
              <div class="preview-title">gemshin_nb 平台</div>
              <div class="preview-status">模块中心</div>
            </div>
            <div class="preview-body">
              <div class="preview-message">
                <p class="preview-big">登录后进入模块中心</p>
                <p class="preview-small">选择 AI 漫剧 · 股票分析 · 个人内容库</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </section>

    <!-- 模块方向展示 -->
    <section class="modules-section">
      <div class="section-container">
        <div class="section-header">
          <p class="section-label">当前三个固定方向</p>
          <h2>先进入模块中心，再进入模块内项目和工作台。</h2>
          <p class="section-desc">
            首页围绕这三个已确认方向来表达平台入口，登录后统一先进入模块中心，再选择进入某个固定模块的内部页面。
          </p>
        </div>

        <div class="modules-grid">
          <article v-for="module in moduleDirections" :key="module.name" class="module-card">
            <div class="module-icon" aria-hidden="true">{{ module.icon }}</div>
            <h3 class="module-name">{{ module.name }}</h3>
            <p class="module-desc">{{ module.description }}</p>
          </article>
        </div>

        <div class="modules-footer">
          <div class="footer-note">
            <strong>模块中心</strong>
            <p>登录后统一先到模块中心，再选择进入某个固定模块的内部项目页。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台特点 -->
    <section class="features-section">
      <div class="section-container">
        <div class="section-header">
          <p class="section-label">平台特点</p>
          <h2>简洁入口，明确方向，稳定结构。</h2>
        </div>

        <div class="features-grid">
          <div class="feature-item">
            <strong>多模块集成</strong>
            <p>三个独立业务方向统一在一个平台入口下，按需选择进入。</p>
          </div>
          <div class="feature-item">
            <strong>统一认证</strong>
            <p>一次登录即可访问所有模块，无需重复认证。</p>
          </div>
          <div class="feature-item">
            <strong>结构清晰</strong>
            <p>首页 → 模块中心 → 模块内部，层级分明，路径明确。</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.homepage {
  min-height: 100vh;
}

/* ── Hero 区域 ── */
.hero {
  position: relative;
  overflow: hidden;
  padding: 22px 20px 48px;
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(114, 162, 255, 0.1), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 22%);
  pointer-events: none;
}

.hero-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 560px);
  gap: 48px;
  align-items: start;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding-top: 72px;
}

.hero-copy {
  max-width: 620px;
}

.kicker {
  margin: 0 0 14px;
  color: var(--ink-accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-copy h1 {
  max-width: 14ch;
  font-size: clamp(48px, 7vw, 80px);
  line-height: 0.94;
  letter-spacing: -0.04em;
  text-wrap: balance;
  color: var(--ink-primary);
}

.hero-intro {
  max-width: 58ch;
  margin-top: 20px;
  color: var(--ink-copy);
  font-size: 17px;
  line-height: 1.85;
}

.hero-note {
  margin-top: 24px;
  color: var(--ink-muted);
  font-size: 16px;
  line-height: 1.6;
}

/* ── 已登录欢迎 ── */
.welcome-banner {
  margin-top: 24px;
  padding: 14px 20px;
  border-radius: 14px;
  background: rgba(114, 162, 255, 0.1);
  border: 1px solid rgba(194, 214, 255, 0.12);
}

.welcome-text {
  color: var(--ink-primary);
  font-size: 15px;
  font-weight: 500;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
  text-decoration: none;
}
.btn-primary:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: wait;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  background: rgba(9, 18, 31, 0.4);
  color: rgba(244, 248, 255, 0.92);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
}
.btn-secondary:hover {
  background: rgba(247, 250, 255, 0.08);
}

.btn-large {
  min-height: 56px;
  padding: 0 28px;
  font-size: 16px;
  border-radius: 14px;
}

/* ── 产品预览 ── */
.product-preview {
  display: flex;
  flex-direction: column;
}

.preview-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: linear-gradient(180deg, rgba(19, 31, 51, 0.98), rgba(12, 21, 35, 0.98));
  box-shadow: var(--shadow-float);
}

.preview-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(188, 209, 248, 0.12);
}

.preview-dots {
  display: flex;
  gap: 6px;
}

.preview-dots span {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  background: rgba(214, 226, 246, 0.32);
}

.preview-title,
.preview-status {
  font-size: 13px;
  color: rgba(234, 241, 255, 0.8);
}

.preview-status {
  color: rgba(191, 214, 255, 0.78);
}

.preview-body {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-message {
  text-align: center;
  padding: 40px 20px;
}

.preview-big {
  color: var(--ink-primary);
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.preview-small {
  color: var(--ink-muted);
  font-size: 14px;
  line-height: 1.6;
}

/* ── 通用区域样式 ── */
.section-container {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 100px 0 80px;
}

.section-header {
  margin-bottom: 48px;
}

.section-label {
  margin: 0 0 14px;
  color: #315f8f;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.section-header h2 {
  max-width: 18ch;
  font-size: clamp(30px, 4vw, 48px);
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: var(--surface-ink);
  text-wrap: balance;
}

.section-desc {
  max-width: 60ch;
  margin-top: 14px;
  color: var(--surface-copy);
  line-height: 1.8;
  font-size: 16px;
}

/* ── 模块方向展示 ── */
.modules-section {
  background: rgba(247, 250, 255, 0.02);
  border-top: 1px solid var(--border-light);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.module-card {
  padding: 28px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  transition: transform 0.2s, box-shadow 0.2s;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 48px rgba(12, 18, 29, 0.14);
}

.module-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.module-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--surface-ink);
  margin-bottom: 12px;
}

.module-desc {
  color: var(--surface-copy);
  line-height: 1.7;
  font-size: 14px;
}

.modules-footer {
  margin-top: 48px;
}

.footer-note {
  padding: 24px;
  border-radius: var(--radius-md);
  background: rgba(114, 162, 255, 0.08);
  border: 1px solid rgba(194, 214, 255, 0.12);
}

.footer-note strong {
  display: block;
  color: var(--surface-ink);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

.footer-note p {
  color: var(--surface-copy);
  line-height: 1.7;
  font-size: 14px;
}

/* ── 平台特点 ── */
.features-section {
  border-top: 1px solid var(--border-light);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.feature-item {
  padding: 24px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-card);
}

.feature-item strong {
  display: block;
  color: var(--surface-ink);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}

.feature-item p {
  color: var(--surface-copy);
  line-height: 1.7;
  font-size: 14px;
}

/* ── 响应式 ── */
@media (max-width: 1140px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 36px;
  }

  .hero-copy {
    max-width: none;
  }
}

@media (max-width: 820px) {
  .hero-copy h1 {
    max-width: none;
    font-size: clamp(38px, 10vw, 60px);
  }

  .modules-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .section-container {
    padding: 60px 0;
  }
}
</style>