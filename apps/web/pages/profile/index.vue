<script setup lang="ts">
definePageMeta({
  layout: "shell",
  requiresAuth: true
})

const { user, logout, authorizedFetch } = useAuth()
const router = useRouter()

const profile = ref({
  display_name: "",
  email: "",
  notify_account_security: true,
  notify_permission_change: true,
  notify_module_activity: true,
  last_password_change: ""
})

const passwordForm = ref({
  old_password: "",
  new_password: "",
  confirm_password: ""
})

const loading = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const showPasswordModal = ref(false)
const showEditModal = ref(false)
const message = ref({ type: "", text: "" })

const mustChangePassword = computed(() => user.value?.must_change_password ?? false)
const isAdmin = computed(() => user.value?.is_admin ?? false)

const userInitials = computed(() => {
  const name = profile.value.display_name || user.value?.username || ""
  return name.slice(0, 2).toUpperCase()
})

function formatDate(dateStr: string | undefined) {
  if (!dateStr) return ""
  const date = new Date(dateStr)
  return date.toLocaleString("zh-CN")
}

function getModuleIcon(code: string) {
  const icons: Record<string, string> = {
    comic: "🎬",
    stock: "📊",
    blog: "📝"
  }
  return icons[code] || "📦"
}

function getModuleDesc(code: string) {
  const descs: Record<string, string> = {
    comic: "完整访问 · 项目中心、工作台、结果校验与导出",
    stock: "完整访问 · 策略分析、研究记录、数据跟踪",
    blog: "完整访问 · 内容整理、标签管理、发布准备"
  }
  return descs[code] || "完整访问"
}

onMounted(async () => {
  await fetchProfile()
  if (mustChangePassword.value) {
    showPasswordModal.value = true
  }
})

async function fetchProfile() {
  loading.value = true
  try {
    const data = await authorizedFetch("/accounts/profile/")
    profile.value = {
      display_name: data.profile?.display_name || "",
      email: data.profile?.email || "",
      notify_account_security: data.profile?.notify_account_security ?? true,
      notify_permission_change: data.profile?.notify_permission_change ?? true,
      notify_module_activity: data.profile?.notify_module_activity ?? true,
      last_password_change: data.profile?.last_password_change || ""
    }
  } catch (error) {
    message.value = { type: "error", text: "加载资料失败" }
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch("/accounts/profile/", {
      method: "PATCH",
      body: { profile: profile.value }
    })
    message.value = { type: "success", text: "资料已保存" }
    showEditModal.value = false
  } catch (error) {
    message.value = { type: "error", text: "保存失败" }
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    message.value = { type: "error", text: "两次密码不一致" }
    return
  }

  changingPassword.value = true
  message.value = { type: "", text: "" }
  try {
    await authorizedFetch("/accounts/change-password/", {
      method: "POST",
      body: {
        old_password: passwordForm.value.old_password,
        new_password: passwordForm.value.new_password
      }
    })
    message.value = { type: "success", text: "密码修改成功" }
    showPasswordModal.value = false
    passwordForm.value = { old_password: "", new_password: "", confirm_password: "" }
    
    if (user.value) {
      user.value.must_change_password = false
    }
  } catch (error: any) {
    const detail = error?.data?.detail || error?.data?.old_password?.[0] || "密码修改失败"
    message.value = { type: "error", text: detail }
  } finally {
    changingPassword.value = false
  }
}

async function handleLogout() {
  await logout()
  await navigateTo("/")
}
</script>

<template>
  <div class="profile-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <p class="page-label">个人中心</p>
      <h1 class="page-title">管理你的个人资料与账号</h1>
      <p class="page-desc">查看和编辑个人资料、修改密码、管理通知偏好、确认角色与模块访问范围。所有已登录用户均可访问此页面。</p>
    </div>

    <!-- 首次改密提示 -->
    <div v-if="mustChangePassword" class="alert-banner alert-warning">
      <div class="alert-icon">!</div>
      <div class="alert-content">
        <strong>需要修改密码</strong>
        你的账号首次登录或密码已被重置，请修改密码后继续使用。
      </div>
    </div>

    <div v-if="message.text" :class="['alert-banner', `alert-${message.type}`]">
      <div class="alert-icon">{{ message.type === "success" ? "✓" : "!" }}</div>
      <div class="alert-content">{{ message.text }}</div>
    </div>

    <!-- 个人资料 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>个人资料</h2>
          <p>与产品使用直接相关的基本信息，头像、姓名和邮箱用于全局身份展示。</p>
        </div>
        <button class="btn btn-secondary btn-sm" @click="showEditModal = true">编辑资料</button>
      </div>
      <div class="cards-grid">
        <div class="card">
          <div class="profile-card">
            <div class="profile-avatar">{{ userInitials }}</div>
            <div class="profile-info">
              <h3>{{ profile.display_name || user?.username }}</h3>
              <div class="profile-role">
                <span v-if="user?.roles?.length" class="role-tags">
                  <span v-for="role in user.roles" :key="role.id" class="role-tag">
                    {{ role.name }}
                  </span>
                </span>
                <span v-else class="text-muted">暂无角色</span>
              </div>
              <div class="data-rows">
                <div class="data-row">
                  <div class="data-label">登录邮箱</div>
                  <div class="data-value">{{ profile.email || "未设置" }}</div>
                </div>
                <div class="data-row">
                  <div class="data-label">所属工作区</div>
                  <div class="data-value">gemshin_nb 主工作区</div>
                </div>
                <div class="data-row">
                  <div class="data-label">注册时间</div>
                  <div class="data-value">{{ formatDate(user?.date_joined) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-label">账号状态</div>
          <h3>账号正常运行</h3>
          <p>当前账号可正常登录，会话有效，未被冻结或限制。</p>
          <div class="data-rows">
            <div class="data-row">
              <div class="data-label">登录状态</div>
              <div class="data-value"><span class="status-badge active">已登录</span></div>
            </div>
            <div class="data-row">
              <div class="data-label">安全状态</div>
              <div class="data-value"><span class="status-badge active">正常</span></div>
            </div>
            <div class="data-row">
              <div class="data-label">最近登录</div>
              <div class="data-value">{{ formatDate(user?.last_login) || '首次登录' }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 登录与安全 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>登录与安全</h2>
          <p>管理登录密码和安全设置。修改密码后需要重新登录。</p>
        </div>
      </div>
      <div class="cards-grid">
        <div class="card">
          <div class="card-label">登录密码</div>
          <h3>修改密码</h3>
          <p>建议定期更换密码，使用包含大小写字母、数字和特殊字符的强密码。</p>
          <div class="data-rows">
            <div class="data-row">
              <div class="data-label">上次修改</div>
              <div class="data-value">{{ formatDate(profile.last_password_change) || '从未修改' }}</div>
            </div>
            <div class="data-row">
              <div class="data-label">密码强度</div>
              <div class="data-value"><span class="status-badge active">强</span></div>
            </div>
          </div>
          <div class="actions-row">
            <button class="btn btn-primary btn-sm" @click="showPasswordModal = true">修改密码</button>
          </div>
        </div>
        <div class="card">
          <div class="card-label">安全验证</div>
          <h3>登录验证</h3>
          <p>当前未启用二次验证。开启后每次新设备登录需要额外验证。</p>
          <div class="data-rows">
            <div class="data-row">
              <div class="data-label">二次验证</div>
              <div class="data-value"><span class="status-badge warning">未开启</span></div>
            </div>
            <div class="data-row">
              <div class="data-label">信任设备</div>
              <div class="data-value">1 台设备</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 通知偏好 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>通知偏好</h2>
          <p>控制你接收哪些系统通知，以及通过什么渠道接收。</p>
        </div>
      </div>
      <div class="card">
        <div class="data-rows">
          <div class="data-row">
            <div class="data-label">账号与安全通知</div>
            <div class="data-value">
              <label class="toggle-item">
                <input
                  v-model="profile.notify_account_security"
                  type="checkbox"
                  class="toggle-input"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          <div class="data-row">
            <div class="data-label">权限变更通知</div>
            <div class="data-value">
              <label class="toggle-item">
                <input
                  v-model="profile.notify_permission_change"
                  type="checkbox"
                  class="toggle-input"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          <div class="data-row">
            <div class="data-label">模块动态通知</div>
            <div class="data-value">
              <label class="toggle-item">
                <input
                  v-model="profile.notify_module_activity"
                  type="checkbox"
                  class="toggle-input"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
        <div class="actions-row">
          <button class="btn btn-secondary btn-sm" :disabled="saving" @click="saveProfile">
            {{ saving ? "保存中..." : "保存偏好" }}
          </button>
        </div>
      </div>
    </section>

    <!-- 角色与模块访问 -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>角色与模块访问</h2>
          <p>你的角色决定可访问的业务模块。拥有多个角色时，最终可见模块取并集。</p>
        </div>
      </div>

      <div class="card" style="margin-top: 20px;">
        <div class="card-label">当前角色</div>
        <div class="data-rows">
          <div class="data-row">
            <div class="data-label">角色</div>
            <div class="data-value">
              <span v-if="user?.roles?.length" class="role-tags">
                <span v-for="role in user.roles" :key="role.id" class="role-tag">
                  {{ role.name }}
                </span>
              </span>
              <span v-else class="text-muted">暂无角色</span>
            </div>
          </div>
          <div class="data-row">
            <div class="data-label">角色说明</div>
            <div class="data-value">
              <span v-if="user?.roles?.length">
                {{ user.roles.map(r => r.name).join('、') }}，可访问对应业务模块。
              </span>
              <span v-else class="text-muted">无角色时无法访问任何业务模块。</span>
            </div>
          </div>
        </div>
      </div>

      <div class="module-access-list">
        <div v-if="user?.roles?.length" v-for="role in user.roles" :key="role.id">
          <div v-for="mod in role.modules" :key="mod.code" class="module-access-item">
            <div class="module-access-left">
              <div class="module-access-icon">{{ mod.icon || getModuleIcon(mod.code) }}</div>
              <div>
                <div class="module-access-name">{{ mod.name }}</div>
                <div class="module-access-desc">{{ getModuleDesc(mod.code) }}</div>
              </div>
            </div>
            <div class="module-access-right">
              <span class="status-badge active">可访问</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无模块权限，请联系管理员分配角色。</p>
        </div>
      </div>

      <div class="footer-notes">
        <span>角色是模块访问的唯一来源。如需调整模块权限，请联系管理员。</span>
        <span v-if="isAdmin">管理员可在"账户与权限"页面管理所有用户的账号和角色。</span>
      </div>
    </section>

    <!-- 管理员专属入口 -->
    <section v-if="isAdmin" class="section">
      <div class="section-header">
        <div>
          <h2>管理员功能</h2>
          <p>你是管理员，可以管理其他用户的账号、角色和权限。</p>
        </div>
      </div>
      <div class="card">
        <div class="card-label">账户与权限管理</div>
        <h3>管理平台用户</h3>
        <p>创建账号、分配角色、重置密码、启用或停用账号、查看操作审计。此功能仅管理员可见。</p>
        <div class="actions-row">
          <NuxtLink to="/account" class="btn btn-primary">进入账户与权限</NuxtLink>
        </div>
      </div>
    </section>

    <!-- 退出登录 -->
    <section class="section">
      <div class="actions-row">
        <button class="btn btn-danger" @click="handleLogout">退出登录</button>
      </div>
    </section>

    <!-- 编辑资料弹窗 -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal">
        <h2 class="modal-title">编辑资料</h2>
        <p class="modal-desc">修改你的显示名称和邮箱。</p>

        <div class="form-group">
          <label class="form-label">显示名称</label>
          <input
            v-model="profile.display_name"
            type="text"
            class="form-input"
            placeholder="输入显示名称"
          />
        </div>

        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="profile.email"
            type="email"
            class="form-input"
            placeholder="输入邮箱地址"
          />
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showEditModal = false">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveProfile">
            {{ saving ? "保存中..." : "保存" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordModal" class="modal-overlay">
      <div class="modal">
        <h2 class="modal-title">修改密码</h2>
        <p class="modal-desc">你的账号需要修改密码后才能继续使用。</p>

        <div class="form-group">
          <label class="form-label">旧密码</label>
          <input
            v-model="passwordForm.old_password"
            type="password"
            class="form-input"
            placeholder="输入当前密码"
          />
        </div>

        <div class="form-group">
          <label class="form-label">新密码</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            class="form-input"
            placeholder="输入新密码（至少8位）"
          />
        </div>

        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <input
            v-model="passwordForm.confirm_password"
            type="password"
            class="form-input"
            placeholder="再次输入新密码"
          />
        </div>

        <div class="modal-actions">
          <button
            class="btn btn-primary"
            :disabled="changingPassword"
            @click="changePassword"
          >
            {{ changingPassword ? "修改中..." : "确认修改" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 账号页共享设计令牌：浅色内容画布 */
.profile-page {
  --canvas: #eef2f6;
  --surface: #f7f9fb;
  --surface-soft: #f1f4f7;
  --line: #dbe2ea;
  --line-soft: #e7edf2;
  --ink: #17202c;
  --copy: #556173;
  --muted: #7a8594;
  --accent: #315f8f;
  --danger: #b54242;
  --danger-bg: rgba(181, 66, 66, 0.08);
  --warning: #8c6841;
  --warning-bg: rgba(140, 104, 65, 0.08);
  --success: #0f766e;
  --success-bg: rgba(15, 118, 110, 0.08);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  max-width: 960px;
  margin: 0 auto;
  padding: 40px 20px;
  background: var(--canvas);
  color: var(--ink);
  line-height: 1.6;
}

/* Page Header */
.page-header {
  margin-bottom: 36px;
}

.page-label {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px;
}

.page-title {
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: var(--ink);
  max-width: 20ch;
}

.page-desc {
  max-width: 64ch;
  margin-top: 16px;
  color: var(--copy);
  line-height: 1.72;
  font-size: 15px;
}

/* Section styles */
.section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}

.section-header p {
  font-size: 14px;
  color: var(--muted);
}

/* Cards grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.card-label {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}

.card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 8px;
}

.card p {
  font-size: 14px;
  color: var(--copy);
  margin-bottom: 16px;
}

/* Profile card */
.profile-card {
  display: flex;
  gap: 20px;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #4a7ab5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
  flex-shrink: 0;
}

.profile-info h3 {
  margin-bottom: 4px;
}

.profile-role {
  margin-bottom: 16px;
}

/* Data rows */
.data-rows {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--line-soft);
}

.data-row:last-child {
  border-bottom: none;
}

.data-label {
  font-size: 14px;
  color: var(--muted);
}

.data-value {
  font-size: 14px;
  color: var(--ink);
  text-align: right;
}

/* Status badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: var(--success-bg);
  color: var(--success);
}

.status-badge.warning {
  background: var(--warning-bg);
  color: var(--warning);
}

.status-badge.disabled {
  background: var(--danger-bg);
  color: var(--danger);
}

/* Role tags */
.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.role-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: rgba(49, 95, 143, 0.1);
  color: var(--accent);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* Module access list */
.module-access-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.module-access-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-md);
}

.module-access-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.module-access-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: var(--surface-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.module-access-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
}

.module-access-desc {
  font-size: 12px;
  color: var(--muted);
}

/* Footer notes */
.footer-notes {
  margin-top: 20px;
  padding: 16px;
  background: var(--surface-soft);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
}

/* Actions row */
.actions-row {
  margin-top: 16px;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 20px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
  border: none;
  text-decoration: none;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-sm {
  min-height: 32px;
  padding: 0 14px;
  font-size: 13px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent), #4a7ab5);
  color: white;
}

.btn-secondary {
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--line);
}

.btn-danger {
  background: var(--danger);
  color: white;
}

/* Alert banner */
.alert-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  font-size: 14px;
  line-height: 1.5;
}

.alert-warning {
  background: var(--warning-bg);
  border: 1px solid rgba(140, 104, 65, 0.2);
  color: var(--warning);
}

.alert-success {
  background: var(--success-bg);
  border: 1px solid rgba(15, 118, 110, 0.2);
  color: var(--success);
}

.alert-error {
  background: var(--danger-bg);
  border: 1px solid rgba(181, 66, 66, 0.2);
  color: var(--danger);
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 700;
}

.alert-warning .alert-icon {
  background: rgba(140, 104, 65, 0.15);
}

.alert-success .alert-icon {
  background: rgba(15, 118, 110, 0.15);
}

.alert-error .alert-icon {
  background: rgba(181, 66, 66, 0.15);
}

/* Toggle */
.toggle-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.toggle-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--line);
  border-radius: 12px;
  transition: background 0.2s;
}

.toggle-slider::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-input:checked + .toggle-slider {
  background: var(--accent);
}

.toggle-input:checked + .toggle-slider::after {
  transform: translateX(20px);
}

/* Empty state */
.empty-state {
  padding: 40px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 32px;
  max-width: 400px;
  width: 90%;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 8px;
}

.modal-desc {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--ink);
  background: var(--canvas);
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
}

.modal-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.text-muted {
  color: var(--muted);
}

@media (max-width: 640px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .section-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .data-row {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }
  
  .data-value {
    text-align: left;
  }
  
  .role-tags {
    justify-content: flex-start;
  }
}
</style>
