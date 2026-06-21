<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const { user } = useAuth()
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
          <h2>账户信息</h2>
          <p>当前登录账户的基本信息</p>
        </div>
        <div class="card-body">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">用户 ID</span>
              <span class="setting-value">{{ user?.id ?? "—" }}</span>
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">用户名</span>
              <span class="setting-value">@{{ user?.username || "—" }}</span>
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">显示名称</span>
              <span class="setting-value">{{ user?.display_name || user?.username || "—" }}</span>
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">认证方式</span>
              <span class="setting-value">Bearer Token（8 小时有效）</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 安全设置（占位） -->
      <div class="account-card">
        <div class="card-header">
          <h2>安全设置</h2>
          <p>密码修改、双因素认证等功能将在后续版本中提供</p>
        </div>
        <div class="card-body">
          <div class="placeholder-block">
            <p>密码修改、双因素认证、登录历史等功能正在开发中。当前版本通过 Bearer Token 进行认证，Token 有效期 8 小时。</p>
          </div>
        </div>
      </div>

      <!-- API 密钥（占位） -->
      <div class="account-card">
        <div class="card-header">
          <h2>API 密钥</h2>
          <p>程序化访问密钥将在后续版本中提供</p>
        </div>
        <div class="card-body">
          <div class="placeholder-block">
            <p>API 密钥管理功能正在开发中。完成后你可以在此生成和管理用于程序化访问的 API Key。</p>
          </div>
        </div>
      </div>

      <!-- 团队协作（占位） -->
      <div class="account-card">
        <div class="card-header">
          <h2>团队协作</h2>
          <p>成员管理和权限控制将在后续版本中提供</p>
        </div>
        <div class="card-body">
          <div class="placeholder-block">
            <p>团队协作功能正在开发中。完成后你可以在此邀请成员、分配角色和管理项目访问权限。</p>
          </div>
        </div>
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

.placeholder-block {
  padding: 16px 20px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.placeholder-block p {
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
}
</style>
