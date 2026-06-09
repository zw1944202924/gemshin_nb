<script setup lang="ts">
const navItems = [
  { label: "Overview", hint: "当前基线与全局入口", to: "/" },
  { label: "Auth", hint: "登录、权限、会话", to: "/dashboard" },
  { label: "Chat", hint: "AI 对话模块入口", to: "/chat" },
  { label: "Login", hint: "切回登录页", to: "/login" }
]

const route = useRoute()
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <p class="brand-mark">G</p>
        <div>
          <p class="brand-name">Gemshin</p>
          <p class="brand-subtitle">apps/web dashboard shell</p>
        </div>
      </div>

      <nav class="nav-list" aria-label="Dashboard sections">
        <NuxtLink
          v-for="item in navItems"
          :key="item.label"
          :to="item.to"
          class="nav-item"
          :class="{ active: route.path === item.to }"
        >
          <span>{{ item.label }}</span>
          <small>{{ item.hint }}</small>
        </NuxtLink>
      </nav>
    </aside>

    <div class="main-panel">
      <header class="topbar">
        <div>
          <p class="topbar-eyebrow">Main baseline</p>
          <h1>Dashboard workspace</h1>
        </div>
        <UBadge color="primary" variant="soft" label="Nuxt UI enabled" />
      </header>

      <main class="content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(240px, 280px) minmax(0, 1fr);
  padding: 18px;
  gap: 18px;
}

.sidebar,
.main-panel {
  border: 1px solid rgba(21, 37, 28, 0.08);
  backdrop-filter: blur(18px);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 28px;
  padding: 24px;
  border-radius: 28px;
  background: rgba(20, 31, 24, 0.9);
  color: #edf4ee;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  width: 2.75rem;
  height: 2.75rem;
  display: grid;
  place-items: center;
  margin: 0;
  border-radius: 1rem;
  background: linear-gradient(135deg, #9bf0a5, #57c987);
  color: #10311c;
  font-size: 1.3rem;
  font-weight: 800;
}

.brand-name,
.brand-subtitle,
.topbar-eyebrow,
.topbar h1,
.nav-item small {
  margin: 0;
}

.brand-name {
  font-size: 1.05rem;
  font-weight: 700;
}

.brand-subtitle,
.nav-item small,
.topbar-eyebrow {
  color: rgba(237, 244, 238, 0.68);
}

.nav-list {
  display: grid;
  gap: 10px;
}

.nav-item {
  display: grid;
  gap: 2px;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    background 180ms ease;
}

.nav-item:hover {
  transform: translateX(4px);
  border-color: rgba(155, 240, 165, 0.35);
  background: rgba(155, 240, 165, 0.08);
}

.nav-item.active {
  border-color: rgba(240, 194, 107, 0.45);
  background: rgba(240, 194, 107, 0.14);
}

.main-panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.7);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 28px 0;
}

.topbar-eyebrow {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(21, 37, 28, 0.55);
}

.topbar h1 {
  margin-top: 6px;
  font-size: clamp(1.6rem, 3vw, 2.2rem);
}

.content {
  min-width: 0;
  padding: 24px 28px 28px;
}

@media (max-width: 960px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    gap: 18px;
  }
}

@media (max-width: 640px) {
  .shell {
    padding: 12px;
    gap: 12px;
  }

  .sidebar,
  .main-panel {
    border-radius: 22px;
  }

  .topbar,
  .content {
    padding-left: 18px;
    padding-right: 18px;
  }
}
</style>
