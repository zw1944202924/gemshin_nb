<script setup lang="ts">
definePageMeta({
  layout: "shell"
})

const securityItems = [
  { label: "登录密码", value: "••••••••", action: "修改" },
  { label: "双因素认证", value: "未启用", action: "启用" },
  { label: "最近登录", value: "2026-06-20 12:30 于 北京", action: "" }
]

const apiKeyItems = [
  { label: "API Key 1", value: "gsk-••••••••••••••••1234", action: "复制", created: "2026-03-12" },
  { label: "API Key 2", value: "gsk-••••••••••••••••5678", action: "复制", created: "2026-05-08" }
]

const teamMembers = [
  { name: "张炜", role: "所有者", avatar: "张" },
  { name: "李设计", role: "编辑者", avatar: "李" },
  { name: "王开发", role: "只读", avatar: "王" }
]
</script>

<template>
  <div class="account-page">
    <section class="account-hero">
      <div class="account-hero-inner">
        <p class="kicker">账户与权限</p>
        <h1>管理你的账户安全和协作权限。</h1>
        <p class="hero-desc">配置密码、API 密钥、团队协作和访问控制。</p>
      </div>
    </section>

    <section class="account-content">
      <!-- 账户安全 -->
      <div class="account-card">
        <div class="card-header">
          <h2>账户安全</h2>
          <p>管理登录密码和认证方式</p>
        </div>
        <div class="card-body">
          <div v-for="item in securityItems" :key="item.label" class="setting-row">
            <div class="setting-info">
              <span class="setting-label">{{ item.label }}</span>
              <span class="setting-value">{{ item.value }}</span>
            </div>
            <button
              v-if="item.action"
              class="setting-action-btn"
              type="button"
              disabled
            >{{ item.action }}</button>
          </div>
        </div>
      </div>

      <!-- API 密钥 -->
      <div class="account-card">
        <div class="card-header">
          <h2>API 密钥</h2>
          <p>用于程序化访问的密钥管理</p>
        </div>
        <div class="card-body">
          <div v-for="item in apiKeyItems" :key="item.label" class="setting-row">
            <div class="setting-info">
              <span class="setting-label">{{ item.label }}</span>
              <span class="setting-meta">创建于 {{ item.created }}</span>
              <code class="key-value">{{ item.value }}</code>
            </div>
            <div class="setting-actions">
              <button class="setting-action-btn" type="button" disabled>{{ item.action }}</button>
              <button class="setting-action-btn danger" type="button" disabled>删除</button>
            </div>
          </div>
          <div class="add-new-row">
            <button class="setting-action-btn" type="button" disabled>+ 生成新密钥</button>
          </div>
        </div>
      </div>

      <!-- 团队协作 -->
      <div class="account-card">
        <div class="card-header">
          <h2>团队协作</h2>
          <p>管理成员及其访问权限</p>
        </div>
        <div class="card-body">
          <div v-for="member in teamMembers" :key="member.name" class="member-row">
            <div class="member-avatar" aria-hidden="true">{{ member.avatar }}</div>
            <div class="member-info">
              <span class="member-name">{{ member.name }}</span>
              <span class="member-role">{{ member.role }}</span>
            </div>
            <button class="setting-action-btn" type="button" disabled>管理</button>
          </div>
          <div class="add-new-row">
            <button class="setting-action-btn" type="button" disabled>+ 邀请成员</button>
          </div>
        </div>
      </div>

      <!-- 占位提示 -->
      <div class="placeholder-notice">
        <p>以上功能为前端占位。完整的账户管理、权限控制和 API 密钥系统将在后续迭代中与后端联调实现。</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.account-page {
  min-height: 100vh;
}

.account-hero {
  padding: 60px 24px 40px;
  position: relative;
}

.account-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(114, 162, 255, 0.08), transparent 40%);
  pointer-events: none;
}

.account-hero-inner {
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

.account-hero-inner h1 {
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

/* 内容 */
.account-content {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding-bottom: 64px;
  display: grid;
  gap: 20px;
}

.account-card {
  background: var(--surface-card);
  border: 1px solid rgba(22, 35, 56, 0.08);
  border-radius: 18px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.card-header {
  padding: 24px 28px 0;
}

.card-header h2 {
  color: var(--surface-ink);
  font-size: 20px;
  font-weight: 700;
}

.card-header p {
  margin-top: 6px;
  color: var(--surface-copy);
  font-size: 14px;
}

.card-body {
  padding: 20px 28px 24px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid rgba(22, 35, 56, 0.04);
}

.setting-row:last-of-type {
  border-bottom: none;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-label {
  color: var(--surface-ink);
  font-size: 15px;
  font-weight: 600;
}

.setting-value {
  color: var(--surface-copy);
  font-size: 13px;
}

.setting-meta {
  color: var(--surface-copy);
  font-size: 12px;
}

.key-value {
  display: block;
  padding: 4px 10px;
  background: rgba(22, 35, 56, 0.04);
  border-radius: 6px;
  font-size: 12px;
  color: var(--surface-copy);
  margin-top: 4px;
  word-break: break-all;
}

.setting-actions {
  display: flex;
  gap: 8px;
}

.setting-action-btn {
  padding: 6px 16px;
  border: 1px solid rgba(22, 35, 56, 0.12);
  border-radius: 8px;
  background: transparent;
  color: var(--surface-copy);
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  opacity: 0.5;
}

.setting-action-btn:hover {
  background: rgba(22, 35, 56, 0.04);
}

.setting-action-btn.danger {
  border-color: rgba(220, 80, 80, 0.2);
  color: #c44;
}

/* 成员行 */
.member-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(22, 35, 56, 0.04);
}

.member-row:last-of-type {
  border-bottom: none;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #081120;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  color: var(--surface-ink);
  font-size: 15px;
  font-weight: 600;
}

.member-role {
  color: var(--surface-copy);
  font-size: 13px;
}

.add-new-row {
  padding-top: 16px;
}

.placeholder-notice {
  padding: 16px 20px;
  border-radius: 12px;
  background: rgba(114, 162, 255, 0.06);
  border: 1px solid rgba(194, 214, 255, 0.12);
}

.placeholder-notice p {
  color: var(--surface-copy);
  font-size: 14px;
  line-height: 1.7;
}

@media (max-width: 640px) {
  .setting-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .member-row {
    flex-wrap: wrap;
  }
}
</style>
