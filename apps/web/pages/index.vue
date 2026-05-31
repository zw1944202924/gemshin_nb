<script setup lang="ts">
const config = useRuntimeConfig()
const { token, user, logout } = useAuth()
</script>

<template>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Gemshin Base</p>
      <h1>Nuxt + Django 认证闭环基线</h1>
      <p class="intro">
        第一条真实端到端链路已经落到当前 monorepo：前端登录页、后端认证接口、
        登录态持有和受保护路由现在使用同一套最小口径。
      </p>
      <div class="panel">
        <p>API base: {{ config.public.apiBase }}</p>
        <ul>
          <li>登录接口：<code>/auth/login/</code></li>
          <li>会话校验：<code>/auth/me/</code></li>
          <li>受保护示例：<code>/protected/</code> 与前端 <code>/dashboard</code></li>
        </ul>
      </div>

      <div class="actions">
        <NuxtLink v-if="token && user" class="primary" to="/dashboard">进入受保护页面</NuxtLink>
        <NuxtLink v-else class="primary" to="/login">前往登录</NuxtLink>
        <button v-if="token && user" class="secondary" type="button" @click="logout()">退出登录</button>
      </div>
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

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.primary,
.secondary {
  border-radius: 999px;
  padding: 12px 18px;
  font: inherit;
  font-weight: 700;
}

.primary {
  background: #162033;
  color: #f5f7fb;
}

.secondary {
  border: 1px solid #c0cfdf;
  background: #fff;
  cursor: pointer;
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
