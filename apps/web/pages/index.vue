<script setup lang="ts">
const config = useRuntimeConfig()

const metrics = [
  {
    label: "Runtime",
    value: "Nuxt 3 + UI",
    tone: "Foundation aligned with dashboard baseline"
  },
  {
    label: "API target",
    value: config.public.apiBase,
    tone: "Ready for auth and module integration"
  },
  {
    label: "Work mode",
    value: "Local-first",
    tone: "Buildable and extensible in apps/web"
  }
]

const navigationGroups = [
  {
    title: "Core surfaces",
    items: ["Overview", "Identity & access", "Operations", "Release notes"]
  },
  {
    title: "Extension points",
    items: ["layouts/", "components/dashboard/", "server/api/", "composables/"]
  }
]

const deliveryTracks = [
  {
    title: "Dashboard shell",
    summary: "Sidebar, header and content regions are separated so feature modules can land without reworking the app frame."
  },
  {
    title: "Shared visual tokens",
    summary: "Global CSS variables and Nuxt UI wiring provide a stable base for future pages and authentication states."
  },
  {
    title: "Developer handoff",
    summary: "Startup notes now point to apps/web and describe the local commands needed for build and dev verification."
  }
]
</script>

<template>
  <div class="dashboard-page">
    <section class="hero-panel">
      <div class="hero-copy">
        <UBadge color="primary" variant="soft" label="Gemshin Dashboard Baseline" />
        <h1>apps/web 已切到可持续扩展的 Dashboard 起点</h1>
        <p>
          当前前端基线基于 <code>main</code> 分支的 Nuxt 工程补齐了布局骨架、UI
          入口和本地开发说明，后续认证、业务模块和接口联调可以直接在这里继续展开。
        </p>
      </div>
      <div class="hero-actions">
        <UButton
          label="查看 API 目标"
          color="neutral"
          variant="outline"
          to="#api-target"
        />
        <UButton
          label="继续扩展布局"
          color="primary"
          to="#delivery-tracks"
        />
      </div>
    </section>

    <section class="metrics-grid">
      <UCard
        v-for="metric in metrics"
        :key="metric.label"
        class="metric-card"
      >
        <template #header>
          <p class="metric-label">{{ metric.label }}</p>
        </template>

        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-tone">{{ metric.tone }}</p>
      </UCard>
    </section>

    <section class="content-grid">
      <UCard id="api-target" class="content-card">
        <template #header>
          <div class="section-heading">
            <div>
              <p class="section-eyebrow">Current target</p>
              <h2>联调入口</h2>
            </div>
            <UBadge color="neutral" variant="subtle" label="runtimeConfig" />
          </div>
        </template>

        <p class="content-text">
          当前公开 API 基址是 <code>{{ config.public.apiBase }}</code>。后续登录态、
          租户上下文和业务查询可以从这个入口继续封装。
        </p>
      </UCard>

      <UCard class="content-card">
        <template #header>
          <div class="section-heading">
            <div>
              <p class="section-eyebrow">Structure</p>
              <h2>目录分层</h2>
            </div>
            <UBadge color="primary" variant="subtle" label="ready" />
          </div>
        </template>

        <div class="nav-groups">
          <div
            v-for="group in navigationGroups"
            :key="group.title"
            class="nav-group"
          >
            <p class="nav-title">{{ group.title }}</p>
            <ul>
              <li v-for="item in group.items" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </UCard>
    </section>

    <section id="delivery-tracks" class="delivery-list">
      <UCard
        v-for="track in deliveryTracks"
        :key="track.title"
        class="delivery-card"
      >
        <template #header>
          <h3>{{ track.title }}</h3>
        </template>

        <p>{{ track.summary }}</p>
      </UCard>
    </section>
  </div>
</template>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 24px;
}

.hero-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-between;
  padding: 28px;
  border: 1px solid rgba(21, 37, 28, 0.08);
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(241, 248, 240, 0.92)),
    rgba(255, 255, 255, 0.85);
  box-shadow: 0 20px 70px rgba(28, 46, 35, 0.08);
}

.hero-copy {
  max-width: 52rem;
}

.hero-copy h1 {
  margin: 14px 0 12px;
  font-size: clamp(2.2rem, 5vw, 4.25rem);
  line-height: 0.98;
}

.hero-copy p {
  margin: 0;
  max-width: 42rem;
  line-height: 1.75;
  color: rgba(21, 37, 28, 0.72);
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: flex-end;
}

.metrics-grid,
.delivery-list {
  display: grid;
  gap: 16px;
}

.metrics-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.metric-card,
.content-card,
.delivery-card {
  border-radius: 24px;
}

.metric-label,
.section-eyebrow,
.nav-title {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-value {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.metric-tone,
.content-text,
.delivery-card p,
.nav-group li {
  color: rgba(21, 37, 28, 0.7);
  line-height: 1.65;
}

.metric-tone {
  margin: 10px 0 0;
}

.content-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-heading h2,
.delivery-card h3 {
  margin: 4px 0 0;
  font-size: 1.3rem;
}

.nav-groups {
  display: grid;
  gap: 18px;
}

.nav-group ul {
  margin: 10px 0 0;
  padding-left: 18px;
}

.delivery-list {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

code {
  font-family: "SFMono-Regular", Consolas, monospace;
}

@media (max-width: 768px) {
  .hero-panel {
    padding: 22px;
  }

  .hero-actions {
    width: 100%;
  }
}
</style>
