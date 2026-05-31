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
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
}

.hero {
  max-width: 760px;
  background: linear-gradient(135deg, #ffffff, #eef4ff);
  border: 1px solid #d7e2f2;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(22, 32, 51, 0.08);
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #4b6381;
}

h1 {
  margin: 0;
  font-size: clamp(32px, 6vw, 56px);
}

.intro {
  margin: 16px 0 0;
  line-height: 1.6;
}

.panel {
  margin-top: 24px;
  padding: 20px;
  border-radius: 16px;
  background: #162033;
  color: #f5f7fb;
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

ul {
  margin: 12px 0 0;
  padding-left: 20px;
}
</style>
