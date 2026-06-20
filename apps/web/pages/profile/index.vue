<script setup lang="ts">
definePageMeta({
  layout: "shell"
})

const profileItems = [
  { label: "显示名称", value: "张炜", editable: true },
  { label: "用户名", value: "zhangwei", editable: false },
  { label: "邮箱", value: "zhangwei@example.com", editable: true },
  { label: "角色", value: "管理员", editable: false },
  { label: "注册时间", value: "2025-01-15", editable: false },
  { label: "最近活跃项目", value: "漫剧项目 021", editable: false }
]
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
          <div class="avatar-placeholder" aria-label="用户头像占位">
            <span>张</span>
          </div>
          <div class="avatar-info">
            <strong>张炜</strong>
            <span>管理员</span>
          </div>
        </div>

        <div class="profile-fields">
          <div v-for="item in profileItems" :key="item.label" class="field-row">
            <span class="field-label">{{ item.label }}</span>
            <div class="field-value">
              <span>{{ item.value }}</span>
              <button v-if="item.editable" class="field-edit-btn" type="button" disabled>编辑</button>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-sidebar">
        <div class="sidebar-card">
          <strong>快捷操作</strong>
          <NuxtLink to="/account" class="sidebar-link">账户与权限设置 →</NuxtLink>
          <NuxtLink to="/modules/projects" class="sidebar-link">我的项目 →</NuxtLink>
        </div>

        <div class="sidebar-card">
          <strong>最近活动</strong>
          <p class="muted-text">暂无最近活动记录。开始处理项目后，这里会显示你的操作历史。</p>
        </div>

        <div class="sidebar-card">
          <strong>使用统计</strong>
          <div class="stat-row">
            <span>处理中项目</span>
            <strong>3</strong>
          </div>
          <div class="stat-row">
            <span>已完成项目</span>
            <strong>12</strong>
          </div>
          <div class="stat-row">
            <span>本月活跃天数</span>
            <strong>18</strong>
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

/* 内容区 */
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

.field-edit-btn {
  padding: 4px 12px;
  border: 1px solid rgba(22, 35, 56, 0.12);
  border-radius: 6px;
  background: transparent;
  color: var(--surface-copy);
  font-size: 12px;
  cursor: pointer;
  opacity: 0.5;
}

.field-edit-btn:hover {
  background: rgba(22, 35, 56, 0.04);
}

/* 侧边栏 */
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
  color: var(--accent);
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
