<script setup lang="ts">
const businessModules = [
  {
    id: "projects",
    title: "项目中心",
    description: "管理所有小说转漫剧项目，查看阶段进度、待处理项和最近活动。从这里开始一切创作。",
    icon: "📁",
    to: "/modules/projects"
  },
  {
    id: "workbench",
    title: "漫剧工作台",
    description: "进入具体项目的分镜、素材生成和配音环节。左侧阶段导航，中间主工作区，右侧状态面板。",
    icon: "🎬",
    to: "/modules/workbench"
  },
  {
    id: "validation",
    title: "结果校验与导出",
    description: "在正式导出前校验完整性，识别缺口、失败任务和依赖失效，确保交付质量。",
    icon: "✅",
    to: "/modules/validation"
  }
]

const supportingModules = [
  { title: "个人中心", description: "管理个人资料、偏好设置和工作记录。", icon: "👤", to: "/profile" },
  { title: "账户与权限", description: "配置账户安全、API 密钥和团队协作权限。", icon: "🔐", to: "/account" }
]
</script>

<template>
  <div class="modules-page">
    <!-- 深色头部 -->
    <section class="modules-hero">
      <div class="modules-hero-inner">
        <p class="kicker">模块中心</p>
        <h1>选一个方向，开始推进项目。</h1>
        <p class="hero-desc">
          所有业务能力都以模块方式组织。每个模块对应一套完整的生产链路，
          从入口到交付，结构清晰、状态可见。
        </p>
      </div>
    </section>

    <!-- 业务模块卡片 -->
    <section class="modules-list-section">
      <div class="section-label">业务方向</div>
      <div class="modules-grid">
        <NuxtLink
          v-for="mod in businessModules"
          :key="mod.id"
          :to="mod.to"
          class="module-card module-card-primary"
        >
          <span class="module-icon" aria-hidden="true">{{ mod.icon }}</span>
          <div class="module-copy">
            <span class="module-title">{{ mod.title }}</span>
            <p class="module-desc">{{ mod.description }}</p>
          </div>
          <span class="module-arrow" aria-hidden="true">→</span>
        </NuxtLink>
      </div>
    </section>

    <!-- 通用模块 -->
    <section class="modules-list-section">
      <div class="section-label">通用功能</div>
      <div class="modules-grid modules-grid-small">
        <NuxtLink
          v-for="mod in supportingModules"
          :key="mod.title"
          :to="mod.to"
          class="module-card"
        >
          <span class="module-icon" aria-hidden="true">{{ mod.icon }}</span>
          <div class="module-copy">
            <span class="module-title">{{ mod.title }}</span>
            <p class="module-desc">{{ mod.description }}</p>
          </div>
          <span class="module-arrow" aria-hidden="true">→</span>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.modules-page {
  min-height: 100vh;
}

.modules-hero {
  padding: 60px 24px 56px;
  position: relative;
}

.modules-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.modules-hero-inner {
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

.modules-hero-inner h1 {
  font-size: clamp(36px, 5vw, 56px);
  line-height: 1.06;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.hero-desc {
  max-width: 56ch;
  margin-top: 14px;
  color: var(--ink-copy);
  font-size: 16px;
  line-height: 1.8;
}

/* 模块列表 */
.modules-list-section {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding-bottom: 48px;
}

.section-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--surface-copy);
  margin-bottom: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(22, 35, 56, 0.08);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.modules-grid-small {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.module-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 18px;
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s, box-shadow 0.2s;
  color: inherit;
  text-decoration: none;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 40px rgba(12, 18, 29, 0.12);
}

.module-card-primary {
  border-left: 4px solid var(--accent);
}

.module-icon {
  font-size: 28px;
  line-height: 1;
}

.module-copy {
  min-width: 0;
}

.module-title {
  display: block;
  color: var(--surface-ink);
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 6px;
}

.module-desc {
  color: var(--surface-copy);
  font-size: 14px;
  line-height: 1.65;
}

.module-arrow {
  font-size: 20px;
  color: var(--ink-muted);
  transition: transform 0.2s;
}

.module-card:hover .module-arrow {
  transform: translateX(4px);
}

@media (max-width: 640px) {
  .modules-grid,
  .modules-grid-small {
    grid-template-columns: 1fr;
  }

  .module-card {
    grid-template-columns: auto 1fr;
  }

  .module-arrow {
    display: none;
  }
}
</style>
