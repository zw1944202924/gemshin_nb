<script setup lang="ts">
const { isAuthenticated, user, login, logout } = useAuth()
const router = useRouter()
const route = useRoute()

// 登录弹窗状态
const showLoginModal = ref(false)
const loginForm = reactive({ username: "", password: "" })
const loginError = ref("")
const loginLoading = ref(false)
const loginModalRef = ref<HTMLDivElement>()
const usernameInputRef = ref<HTMLInputElement>()

// 登录成功后要跳转的目标
const redirectPath = ref("/")

const openLoginModal = (target?: string) => {
  if (target) {
    redirectPath.value = target
  }
  showLoginModal.value = true
  loginError.value = ""
  loginForm.username = ""
  loginForm.password = ""
  // 延迟聚焦到用户名输入框
  nextTick(() => {
    usernameInputRef.value?.focus()
  })
}

const closeLoginModal = () => {
  showLoginModal.value = false
  loginError.value = ""
  loginForm.username = ""
  loginForm.password = ""
  redirectPath.value = "/"
}

const handleLogin = async () => {
  loginError.value = ""
  loginLoading.value = true
  try {
    await login(loginForm)
    const target = redirectPath.value
    closeLoginModal()
    await router.push(target)
  } catch (error: any) {
    const detail =
      error?.data?.detail
        ? String(error.data.detail)
        : ""
    loginError.value = detail || "登录失败，请稍后重试"
  } finally {
    loginLoading.value = false
  }
}

const handleLogout = async () => {
  await logout()
  await router.push("/")
}

// Esc 键关闭弹窗
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === "Escape" && showLoginModal.value) {
    closeLoginModal()
  }
}

// 暴露方法给子组件使用
defineExpose({ openLoginModal })

// 检查 URL 中的 redirect 参数，如果有则自动打开登录弹窗
onMounted(() => {
  const redirect = route.query.redirect
  if (typeof redirect === "string" && redirect) {
    openLoginModal(redirect)
  }
})

// 监听路由变化，检查 redirect 参数
watch(
  () => route.query.redirect,
  (newRedirect) => {
    if (typeof newRedirect === "string" && newRedirect && !showLoginModal.value) {
      openLoginModal(newRedirect)
    }
  }
)
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-inner">
        <NuxtLink to="/" class="brand">
          <span class="brand-mark" aria-hidden="true" />
          <span>gemshin_nb</span>
        </NuxtLink>

        <nav class="topnav" aria-label="主导航">
          <NuxtLink to="/">首页</NuxtLink>
          <NuxtLink to="/modules">模块中心</NuxtLink>
          <NuxtLink to="/assistant">AI 助手</NuxtLink>
          <NuxtLink to="/profile">个人中心</NuxtLink>
          <NuxtLink to="/account">账户与权限</NuxtLink>
        </nav>

        <div class="top-actions">
          <template v-if="isAuthenticated">
            <span class="user-greeting">{{ user?.display_name || user?.username }}</span>
            <NuxtLink to="/modules" class="primary-link">模块中心</NuxtLink>
            <button class="logout-btn" type="button" @click="handleLogout">退出</button>
          </template>
          <template v-else>
            <button class="login-btn" type="button" @click="openLoginModal">登录</button>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">
      <slot />
    </main>

    <!-- 登录弹窗 -->
    <Teleport to="body">
      <div
        v-if="showLoginModal"
        ref="loginModalRef"
        class="login-modal-overlay"
        @click.self="closeLoginModal"
        @keydown="handleKeydown"
      >
        <div class="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-modal-title">
          <div class="login-modal-header">
            <div>
              <h3 id="login-modal-title">登录 gemshin_nb</h3>
              <p class="login-modal-desc">登录后即可访问模块中心，进入各业务方向。</p>
            </div>
            <button class="login-modal-close" type="button" @click="closeLoginModal" aria-label="关闭登录弹窗">&times;</button>
          </div>
          <form class="login-modal-form" @submit.prevent="handleLogin">
            <div class="login-modal-fields">
              <label class="login-modal-field">
                <span class="login-modal-label">用户名</span>
                <input
                  ref="usernameInputRef"
                  v-model="loginForm.username"
                  type="text"
                  autocomplete="username"
                  placeholder="请输入用户名"
                  :disabled="loginLoading"
                />
              </label>
              <label class="login-modal-field">
                <span class="login-modal-label">密码</span>
                <input
                  v-model="loginForm.password"
                  type="password"
                  autocomplete="current-password"
                  placeholder="请输入密码"
                  :disabled="loginLoading"
                />
              </label>
            </div>

            <p v-if="loginError" class="login-modal-error" role="alert">{{ loginError }}</p>

            <button class="login-modal-submit" type="submit" :disabled="loginLoading">
              {{ loginLoading ? "登录中..." : "登录" }}
            </button>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at top, rgba(106, 154, 255, 0.18), transparent 26%),
    linear-gradient(180deg, #05070b 0%, #0b1321 38%, #edf2f8 38%, #f8fafc 100%);
  color: var(--ink-primary);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 20px;
  background: rgba(6, 8, 13, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-light);
}

.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: min(1320px, calc(100% - 24px));
  margin: 0 auto;
  height: var(--shell-header-height);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.brand-mark {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(126, 177, 255, 0.72));
  box-shadow: 0 0 24px rgba(132, 182, 255, 0.38);
}

.topnav {
  display: flex;
  gap: 6px;
  align-items: center;
}

.topnav a {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--ink-copy);
  transition: background 0.15s, color 0.15s;
}

.topnav a:hover,
.topnav a.router-link-active {
  background: rgba(247, 250, 255, 0.08);
  color: var(--ink-primary);
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.user-greeting {
  font-size: 13px;
  color: var(--ink-copy);
  white-space: nowrap;
}

.login-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 18px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
}

.login-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.primary-link {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 18px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 14px;
  font-weight: 700;
  transition: opacity 0.15s, transform 0.15s;
  text-decoration: none;
}

.primary-link:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.logout-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.08);
  color: var(--ink-copy);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.main-content {
  flex: 1;
}

/* ── 登录弹窗 ── */
.login-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
}

.login-modal {
  width: 100%;
  max-width: 400px;
  margin: 20px;
  background: #1a2332;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.login-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-light);
}

.login-modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--ink-primary);
}

.login-modal-desc {
  margin: 6px 0 0;
  color: var(--ink-muted);
  font-size: 13px;
  line-height: 1.5;
}

.login-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--ink-copy);
  font-size: 20px;
  cursor: pointer;
  transition: background 0.15s;
}

.login-modal-close:hover {
  background: rgba(255, 255, 255, 0.12);
}

.login-modal-form {
  padding: 24px;
}

.login-modal-fields {
  display: grid;
  gap: 16px;
}

.login-modal-field {
  display: grid;
  gap: 8px;
}

.login-modal-label {
  color: var(--ink-copy);
  font-size: 13px;
  font-weight: 600;
}

.login-modal-field input {
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid rgba(194, 214, 255, 0.18);
  background: rgba(9, 18, 31, 0.5);
  color: rgba(247, 250, 255, 0.96);
  font: inherit;
  font-size: 15px;
  transition: border-color 0.15s;
}

.login-modal-field input::placeholder {
  color: rgba(186, 202, 227, 0.4);
}

.login-modal-field input:focus {
  outline: none;
  border-color: rgba(132, 182, 255, 0.6);
  background: rgba(9, 18, 31, 0.7);
}

.login-modal-error {
  margin: 12px 0 0;
  color: #f87171;
  font-size: 13px;
}

.login-modal-submit {
  margin-top: 20px;
  width: 100%;
  min-height: 48px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #081120;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
}

.login-modal-submit:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.login-modal-submit:disabled {
  opacity: 0.6;
  cursor: wait;
}

@media (max-width: 920px) {
  .topbar-inner {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 0;
    gap: 10px;
  }

  .topnav {
    order: 3;
    width: 100%;
    overflow-x: auto;
    white-space: nowrap;
    gap: 2px;
  }

  .top-actions {
    margin-left: auto;
  }
}

@media (max-width: 640px) {
  .topnav {
    display: none;
  }
}
</style>
