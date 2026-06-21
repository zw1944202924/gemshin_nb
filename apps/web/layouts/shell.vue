<script setup lang="ts">
const { isAuthenticated, user, logout } = useAuth()
const router = useRouter()

const handleLogout = async () => {
  await logout()
  await router.push("/")
}
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
          </template>
          <template v-else>
            <span class="guest-hint">请登录</span>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">
      <slot />
    </main>
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

.guest-hint {
  font-size: 13px;
  color: var(--ink-muted);
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

.main-content {
  flex: 1;
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
  .top-actions {
    display: none;
  }
}
</style>
