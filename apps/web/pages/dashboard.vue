<script setup lang="ts">
definePageMeta({
  requiresAuth: true
})

const router = useRouter()
const { user, logout, authorizedFetch } = useAuth()
const message = ref("正在加载受保护资源...")
const errorMessage = ref("")

const loadProtectedMessage = async () => {
  errorMessage.value = ""

  try {
    const response = await authorizedFetch<{ message: string; scope: string }>("/protected/")
    message.value = `${response.message}，当前访问范围：${response.scope}`
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "受保护资源加载失败"
  }
}

const signOut = async () => {
  await logout()
  await router.push("/login")
}

await loadProtectedMessage()
</script>

<template>
  <main class="dashboard-shell">
    <section class="dashboard-card">
      <div class="topbar">
        <div>
          <p class="eyebrow">Protected Route</p>
          <h1>最小认证闭环已接通</h1>
        </div>
        <button class="ghost" type="button" @click="signOut">退出登录</button>
      </div>

      <p class="intro">
        当前用户：<strong>{{ user?.display_name }}</strong>
        <span v-if="user">（{{ user.username }}）</span>
      </p>

      <div class="status-panel">
        <p>{{ message }}</p>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </div>

      <div class="actions">
        <button class="primary" type="button" @click="loadProtectedMessage">重新验证后端鉴权</button>
        <NuxtLink class="link" to="/">返回首页</NuxtLink>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard-shell {
  min-height: 100vh;
  padding: 28px;
  background:
    linear-gradient(120deg, rgba(255, 240, 204, 0.6), transparent 42%),
    linear-gradient(180deg, #0f1727, #162033 42%, #d9e6f2 42%, #edf3f9);
}

.dashboard-card {
  max-width: 960px;
  margin: 80px auto 0;
  padding: 36px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 28px 90px rgba(15, 23, 39, 0.18);
}

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #7f5b21;
}

h1 {
  margin: 0;
  font-size: clamp(30px, 6vw, 48px);
}

.intro {
  margin: 18px 0 0;
  color: #314357;
  line-height: 1.7;
}

.status-panel {
  margin-top: 28px;
  padding: 24px;
  border-radius: 22px;
  background: #162033;
  color: #f5f7fb;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

.primary,
.ghost,
.link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 12px 18px;
  font: inherit;
  font-weight: 700;
}

.primary {
  border: 0;
  color: #f5f7fb;
  background: linear-gradient(135deg, #0f4c81, #162033);
  cursor: pointer;
}

.ghost {
  border: 1px solid #cbd6e5;
  background: transparent;
  cursor: pointer;
}

.link {
  border: 1px solid #b8c6d9;
}

.error {
  color: #ffb4ab;
}

@media (max-width: 720px) {
  .topbar {
    flex-direction: column;
  }

  .dashboard-card {
    margin-top: 24px;
    padding: 24px;
  }
}
</style>
