<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const { user } = useAuth()
const { projects, fetchProjects } = useStory()

const displayNameInitial = computed(() => {
  const name = user.value?.display_name || user.value?.username || "?"
  return name.charAt(0).toUpperCase()
})

// 从真实后端获取项目统计
const projectStats = ref({ total: 0, processing: 0, completed: 0 })
const statsLoading = ref(true)

const loadStats = async () => {
  try {
    // 并行获取各状态的项目数量
    const all = await fetchProjects()
    projectStats.value.total = all?.length ?? 0
    const processing = await fetchProjects("processing")
    projectStats.value.processing = processing?.length ?? 0
    const completed = await fetchProjects("completed")
    projectStats.value.completed = completed?.length ?? 0
  } catch {
    // 统计加载失败不阻塞页面
  } finally {
    statsLoading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="profile-page">
    <section class="profile-hero">
      <div class="profile-hero-inner">
        <p class="kicker">个人中心</p>
        <h1>你的工作空间，你的节奏。</h1>
        <p class="hero-desc">管理个人资料、查看工作记录和偏好设置。</p>
      </div>
    </section>

    <section class="profile-content">
      <div class="profile-card">
        <div class="avatar-area">
          <div class="avatar-placeholder" aria-label="用户头像">
            <span>{{ displayNameInitial }}</span>
          </div>
          <div class="avatar-info">
            <strong>{{ user?.display_name || user?.username || "—" }}</strong>
            <span>@{{ user?.username || "—" }}</span>
          </div>
        </div>

        <div class="profile-fields">
          <div class="field-row">
            <span class="field-label">用户 ID</span>
            <div class="field-value">
              <span>{{ user?.id ?? "—" }}</span>
            </div>
          </div>
          <div class="field-row">
            <span class="field-label">显示名称</span>
            <div class="field-value">
              <span>{{ user?.display_name || user?.username || "—" }}</span>
            </div>
          </div>
          <div class="field-row">
            <span class="field-label">用户名</span>
            <div class="field-value">
              <span>@{{ user?.username || "—" }}</span>
            </div>
          </div>
          <div class="field-row">
            <span class="field-label">认证方式</span>
            <div class="field-value">
              <span>Token 登录</span>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-sidebar">
        <div class="sidebar-card">
          <strong>快捷操作</strong>
          <NuxtLink to="/account" class="sidebar-link">账户与权限设置 →</NuxtLink>
          <NuxtLink to="/story" class="sidebar-link">我的项目 →</NuxtLink>
        </div>

        <div class="sidebar-card">
          <strong>最近活动</strong>
          <p v-if="projects.length === 0 && !statsLoading" class="muted-text">
            还没有项目。去项目中心创建你的第一个项目。
          </p>
          <div v-else-if="projects.length > 0" class="recent-projects">
            <div v-for="p in projects.slice(0, 3)" :key="p.id" class="recent-item">
              <span class="recent-name">{{ p.title }}</span>
              <span class="recent-status">{{ p.status }}</span>
            </div>
          </div>
          <p v-else class="muted-text">加载中…</p>
        </div>

        <div class="sidebar-card">
          <strong>项目统计</strong>
          <div class="stat-row">
            <span>全部项目</span>
            <strong>{{ projectStats.total }}</strong>
          </div>
          <div class="stat-row">
            <span>处理中</span>
            <strong>{{ projectStats.processing }}</strong>
          </div>
          <div class="stat-row">
            <span>已完成</span>
            <strong>{{ projectStats.completed }}</strong>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
}

.profile-hero {
  padding: 60px 24px 40px;
  position: relative;
}

.profile-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.profile-hero-inner {
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

.profile-hero-inner h1 {
  font-size: clamp(32px, 4vw, 48px);
  line-height: 1.08;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.hero-desc {
  max-width: 50ch;
  margin-top: 12px;
  color: var(--ink-copy);
  font-size: 16px;
  line-height: 1.7;
}

.profile-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding-bottom: 64px;
}

.profile-card {
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  border-radius: 18px;
  padding: 28px;
  box-shadow: var(--shadow-card);
}

.avatar-area {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(22, 35, 56, 0.06);
  margin-bottom: 24px;
}

.avatar-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #081120;
}

.avatar-info strong {
  display: block;
  color: var(--surface-ink);
  font-size: 18px;
  font-weight: 700;
}

.avatar-info span {
  display: block;
  margin-top: 4px;
  color: var(--surface-copy);
  font-size: 14px;
}

.profile-fields {
  display: grid;
  gap: 0;
}

.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid rgba(22, 35, 56, 0.04);
}

.field-row:last-child {
  border-bottom: none;
}

.field-label {
  color: var(--surface-copy);
  font-size: 14px;
  flex-shrink: 0;
}

.field-value {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-value span {
  color: var(--surface-ink);
  font-size: 14px;
  font-weight: 500;
}

.profile-sidebar {
  display: grid;
  gap: 16px;
  align-content: start;
}

.sidebar-card {
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-card);
}

.sidebar-card strong {
  display: block;
  color: var(--surface-ink);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
}

.sidebar-link {
  display: block;
  padding: 8px 0;
  color: #3b82f6;
  font-size: 14px;
  font-weight: 500;
}

.sidebar-link:hover {
  text-decoration: underline;
}

.muted-text {
  color: var(--surface-copy);
  font-size: 14px;
  line-height: 1.7;
}

.recent-projects {
  display: grid;
  gap: 8px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(22, 35, 56, 0.04);
}

.recent-name {
  color: var(--surface-ink);
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  flex-shrink: 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(22, 35, 56, 0.04);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row span {
  color: var(--surface-copy);
  font-size: 14px;
}

.stat-row strong {
  margin-bottom: 0;
  color: var(--surface-ink);
  font-size: 16px;
}

@media (max-width: 920px) {
  .profile-content {
    grid-template-columns: 1fr;
  }

  .profile-sidebar {
    order: -1;
  }
}

@media (max-width: 640px) {
  .field-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
